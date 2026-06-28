# Contributing to AI Advisor

This repo is a Claude Code plugin that provides expert advice on building AI agents. Each skill is a standalone directory under `skills/` that contributors can research and fill in independently.

## How Skills Work

When a user installs this plugin and asks a question matching a skill's trigger phrases, Claude loads that `SKILL.md` and uses it to guide the response. The better the content, the better the advice.

## Filling In a Skill

1. Pick a skill from `skills/` that interests you
2. Research the topic — see the "What This Skill Should Cover" section as a starting point
3. Replace the stub content in `SKILL.md` with real guidance (~1,500 words of process steps)
4. Add deeper reference material as separate files in `references/`

### SKILL.md Structure

```markdown
---
name: advise-your-topic
description: |
  This skill should be used when the user asks to "<trigger phrase>",
  "<another trigger phrase>", or "<another>".
---

# Topic Title

## Step 1 — Do the first thing
Concrete guidance here.

## Step 2 — Do the next thing
...
```

**Tips:**
- The `description` frontmatter is how Claude decides when to activate the skill — write trigger phrases that sound like real questions
- Keep `SKILL.md` focused on **process** (what steps to follow, what questions to ask, what decisions to make)
- Move large reference tables, comparisons, and examples to `references/` files and link to them

### Reference Files

Add files to `references/` for supporting material:

```
skills/advise-rag/
├── SKILL.md
└── references/
    ├── chunking-strategies.md
    ├── retrieval-patterns.md
    └── failure-modes.md
```

## Adding a New Skill

1. Create a new directory: `skills/advise-<topic>/`
2. Copy the stub template below into `SKILL.md`
3. Create a `references/` subdirectory
4. Open a PR — stubs are welcome, partial content is welcome

### Stub Template

```markdown
---
name: advise-your-topic
description: |
  This skill should be used when the user asks to "...", "...", or "...".
---

# Topic Advisor

> **Status: Stub** — This skill needs content. See [CONTRIBUTING.md](../../CONTRIBUTING.md) to fill it in.

## What This Skill Should Cover

- Point 1
- Point 2

## References

Add reference files to `references/` as you build this out.
```

## Installing the Plugin Locally (for testing)

```
/plugin install ai-advisor@github:NexusInitiative/AI-Agent-Advisor
```

Or point to your local fork during development.
