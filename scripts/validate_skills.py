#!/usr/bin/env python3
"""Validate every skill against the repo quality bar and Claude Code skill rules.

Checks (errors fail CI):
  - SKILL.md exists with parseable YAML frontmatter containing name + description
  - name matches the directory, is <=64 chars, lowercase letters/numbers/hyphens only
  - description is non-empty, <=1024 chars, and contains no XML tags
  - SKILL.md body is <=500 lines (Claude Code progressive-disclosure guidance)
  - no stub markers remain
  - every local markdown link in SKILL.md resolves to an existing file
  - reference files link only one level deep (references/*.md must not link to
    further local .md files outside their own directory)
  - agents/openai.yaml exists with the three required keys

Warnings (reported, non-fatal):
  - SKILL.md body outside the CONTRIBUTING 1,000-2,000 word target
  - topical reference files (non source-map) under 300 words

Usage: python3 scripts/validate_skills.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#\s]+)\)")
STUB_MARKERS = ("Status: Stub", "needs content", "Add reference files to `references/`")

errors: list[str] = []
warnings: list[str] = []


def parse_frontmatter(text: str, where: str):
    if not text.startswith("---"):
        errors.append(f"{where}: missing YAML frontmatter")
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        errors.append(f"{where}: unterminated YAML frontmatter")
        return None, text
    fm_raw, body = parts[1], parts[2]
    # Minimal YAML parse: name scalar + description block scalar.
    fm: dict[str, str] = {}
    current_key = None
    block_lines: list[str] = []
    for line in fm_raw.splitlines():
        if re.match(r"^[A-Za-z_][\w-]*:", line):
            if current_key and block_lines:
                fm[current_key] = "\n".join(block_lines).strip()
                block_lines = []
            key, _, value = line.partition(":")
            value = value.strip()
            if value in ("|", ">", "|-", ">-"):
                current_key = key.strip()
            else:
                fm[key.strip()] = value.strip("\"'")
                current_key = None
        elif current_key is not None:
            block_lines.append(line.strip())
    if current_key and block_lines:
        fm[current_key] = "\n".join(block_lines).strip()
    return fm, body


def check_local_links(md_file: Path, base: Path, one_level_only: bool) -> None:
    text = md_file.read_text(encoding="utf-8")
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (md_file.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"{md_file.relative_to(REPO)}: broken local link -> {target}")
        elif one_level_only and resolved.suffix == ".md" and resolved.parent != md_file.parent:
            errors.append(
                f"{md_file.relative_to(REPO)}: nested reference link -> {target} "
                "(references must stay one level deep from SKILL.md)"
            )


def main() -> int:
    skill_dirs = sorted(d for d in SKILLS.iterdir() if d.is_dir())
    if not skill_dirs:
        errors.append("no skill directories found under skills/")

    for skill_dir in skill_dirs:
        rel = skill_dir.relative_to(REPO)
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"{rel}: missing SKILL.md")
            continue

        text = skill_md.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text, str(rel / "SKILL.md"))
        if fm is None:
            continue

        name = fm.get("name", "")
        desc = fm.get("description", "")
        if not name:
            errors.append(f"{rel}: frontmatter missing 'name'")
        else:
            if name != skill_dir.name:
                errors.append(f"{rel}: name '{name}' does not match directory")
            if len(name) > 64:
                errors.append(f"{rel}: name exceeds 64 characters")
            if not NAME_RE.match(name):
                errors.append(f"{rel}: name must be lowercase letters/numbers/hyphens")
        if not desc:
            errors.append(f"{rel}: frontmatter missing 'description'")
        else:
            if len(desc) > 1024:
                errors.append(f"{rel}: description exceeds 1024 characters ({len(desc)})")
            if re.search(r"<[^>]+>", desc):
                errors.append(f"{rel}: description contains XML tags")

        body_lines = [ln for ln in body.splitlines()]
        if len(body_lines) > 500:
            errors.append(f"{rel}: SKILL.md body is {len(body_lines)} lines (max 500)")

        for marker in STUB_MARKERS:
            if marker in text:
                errors.append(f"{rel}: stub marker still present: '{marker}'")

        words = len(body.split())
        if not (1000 <= words <= 2200):
            warnings.append(f"{rel}: SKILL.md body is {words} words (target 1,000-2,000)")

        check_local_links(skill_md, skill_dir, one_level_only=False)

        refs_dir = skill_dir / "references"
        if refs_dir.is_dir():
            for ref in sorted(refs_dir.glob("*.md")):
                check_local_links(ref, skill_dir, one_level_only=True)
                ref_words = len(ref.read_text(encoding="utf-8").split())
                if ref.name != "source-map.md" and ref_words < 300:
                    warnings.append(
                        f"{ref.relative_to(REPO)}: {ref_words} words (target 300-1,500)"
                    )

        oai = skill_dir / "agents" / "openai.yaml"
        if not oai.exists():
            errors.append(f"{rel}: missing agents/openai.yaml")
        else:
            oai_text = oai.read_text(encoding="utf-8")
            for key in ("allow_implicit_invocation", "display_name", "short_description"):
                if key not in oai_text:
                    errors.append(f"{rel}: agents/openai.yaml missing '{key}'")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\n{len(skill_dirs)} skills checked: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
