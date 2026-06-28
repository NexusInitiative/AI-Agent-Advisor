# Contributing to AI Advisor

This repo is a Claude Code and Codex plugin that provides expert advice on building AI agent systems. Each skill is a standalone directory under `skills/` that contributors can research and fill in independently.

## How Skills Work

When a user installs this plugin and asks a question that matches a skill's trigger phrases, the agent loads that `SKILL.md` and uses it to guide the response. The agent reads the skill body as authoritative instructions — it shapes what questions get asked, what trade-offs get surfaced, and what recommendations get made. The better the content, the better the advice.

---

## Writing a Great Skill

This is the most important section. A skill that just summarizes Wikipedia is useless. A skill that helps a developer make the right architectural decision in 5 minutes is invaluable. Here's how to write the latter.

### 1. Trigger Phrases — Write How Developers Actually Talk

The `description` frontmatter is not a keyword list. It's how the agent decides whether to activate your skill at all. If the phrases don't match how real developers phrase their questions, the skill never fires.

**Bad trigger phrases** (too formal, too broad):
```yaml
description: |
  This skill should be used for retrieval-augmented generation,
  RAG systems, or document retrieval.
```

**Good trigger phrases** (natural, specific, conversational):
```yaml
description: |
  This skill should be used when the user asks to "help me design my RAG pipeline",
  "what chunking strategy should I use", "my retrieval results are bad",
  "should I use dense or sparse retrieval", "how do I improve my RAG accuracy",
  "help me pick a retrieval approach", or needs guidance on building or debugging
  a retrieval-augmented generation system.
```

**Rules for trigger phrases:**
- Write them as quoted natural language sentences, not keywords
- Include at least 5–8 distinct phrasings covering different entry points to the topic
- Cover both "help me build X" and "I'm having trouble with X" angles — beginners ask the former, experienced devs ask the latter
- Include diagnostic or debugging variants ("my X isn't working", "X is too slow/expensive/inaccurate")
- Think about what someone types when they're frustrated, not when they're writing documentation

**Test your triggers mentally:** Read each phrase out loud. Does it sound like something a real developer would type in a chat window at 2pm on a Tuesday? If it sounds like a textbook section header, rewrite it.

---

### 2. Skill Body — Process Over Knowledge

The most common mistake is writing a skill that explains *what* a topic is instead of advising *what to do*. The agent already has broad knowledge of these topics. What it needs from your skill is:

- A decision framework (what questions to ask before recommending anything)
- Concrete trade-offs (when A is better than B and why)
- Opinionated recommendations (not "it depends" — "it depends on X, and if X then do Y")
- Common failure modes and how to recognize them early

**Bad skill body (encyclopedic):**
```markdown
## What is RAG?
Retrieval-Augmented Generation (RAG) is a technique that combines...
There are several chunking strategies including fixed-size, semantic...
Dense retrieval uses embedding similarity while sparse retrieval...
```

**Good skill body (advisory):**
```markdown
## Step 1 — Establish What the User Actually Needs

Before recommending anything, ask:
- What is the source data? (PDFs, code, databases, web pages, mixed?)
- What does a good answer look like? (Exact facts? Summaries? Citations?)
- What's the failure mode they most want to avoid? (Hallucination? Missed context? Slow retrieval?)

The answers change everything. A legal document search needs precision above all.
A customer support bot needs recall. A coding assistant needs exact syntax matches.
Don't skip this step.

## Step 2 — Recommend a Starting Architecture

For most new RAG pipelines, start with the simplest thing that could work:
- Fixed-size chunking (512 tokens, 10% overlap)
- One embedding model (text-embedding-3-small or equivalent)
- Cosine similarity search
- Top-5 retrieval with no reranking

This baseline tells you whether retrieval quality is even the problem before
you invest in complexity. Most teams skip this and go straight to hybrid search
and rerankers, then can't tell what's actually helping.
```

**The test:** After reading your skill body, can a developer make a concrete decision they couldn't make before? If the answer is "they learned some things but still need to figure out what to do," the skill needs more opinions and less explanation.

---

### 3. Process vs. Reference — What Goes Where

`SKILL.md` and `references/` serve different purposes. Mixing them produces a skill that's either too bloated to load efficiently or too thin to be useful.

**SKILL.md contains:**
- The decision-making process (ordered steps)
- Questions to ask the user before recommending
- Opinionated recommendations with clear rationale
- When to escalate to a deeper reference file

**`references/` contains:**
- Comparison tables (model benchmarks, vector DB feature matrices, pricing)
- Detailed explanations of specific sub-topics
- Code examples and templates
- Troubleshooting checklists
- Anything that would bloat the main skill past ~1,500 words

**How to link from SKILL.md to a reference:**
```markdown
## Step 3 — Choose a Chunking Strategy

The right chunking strategy depends on your document type. For a detailed
breakdown of each approach with examples, see [chunking-strategies.md](references/chunking-strategies.md).

In short: use semantic chunking for prose documents, fixed-size for structured
data, and hierarchical chunking when users need both summary and detail answers.
```

**Ideal split:**
- `SKILL.md`: 1,000–2,000 words. If you're going over 2,000, move content to references.
- `references/*.md`: No hard limit. These are loaded on demand, so depth is fine.
- Number of reference files: As many as the topic warrants. One per sub-topic is a good default.

---

### 4. What Good Advisor Content Looks Like

Great skills share these traits:

**They ask before they recommend.** Real advisors don't prescribe without diagnosing. Start every skill with 2–4 clarifying questions the agent should ask (or infer from context) before making recommendations.

**They give a default path.** Most developers want a starting point, not a decision tree. Always provide a "start here" recommendation for the most common case, then branch from there.

**They acknowledge trade-offs honestly.** Don't write marketing copy for any one approach. If pgvector is fine for small datasets but breaks down at scale, say so. If fine-tuning is usually the wrong choice, say so. Developers trust advisors who tell them the hard truths.

**They explain *why* behind recommendations.** "Use hybrid search" is useless without "because dense retrieval misses keyword-critical queries like product codes or error messages." The *why* is what lets a developer adapt the advice to their specific situation.

**They know when to refer out.** A good skill knows its edges. If a question is really about vector DB selection inside a RAG question, say "for vector DB trade-offs, see `advise-vector-db`" and stay focused.

**They're opinionated.** "It depends" is the enemy of a useful skill. Replace it with: "It depends on X. If X is true, do Y because Z. If X is not true, do W because V." Every fork in the decision tree should resolve to a recommendation.

---

### 5. Length and Depth Guidelines

| Section | Target Length | Notes |
|---|---|---|
| `description` frontmatter | 5–10 trigger phrases | Quality over quantity — 8 great phrases beat 20 bad ones |
| `SKILL.md` body | 1,000–2,000 words | Process steps, not encyclopedic coverage |
| Each `references/*.md` | 300–1,500 words | One focused topic per file |
| Number of reference files | 2–6 per skill | More is fine if the topic warrants it |

---

### 6. Testing Your Skill

Before opening a PR, validate your skill works as intended.

**Test trigger activation:**
Install the plugin locally and ask questions using your trigger phrases. Also ask adjacent questions that *shouldn't* activate the skill and verify they don't.

```
/plugin install ai-advisor@github:YOUR-FORK/AI-Agent-Advisor
```

Then ask:
- Exact trigger phrase → should activate
- Paraphrased version → should activate
- Unrelated question → should NOT activate

**Test response quality:**
Ask the skill a hard question — one where the right answer is non-obvious. A good skill produces a response that:
- Asks at least one clarifying question (or infers context and states its assumption)
- Makes a concrete recommendation, not a list of options
- Explains the trade-off behind the recommendation
- Points to a reference file when appropriate

**Red flags to fix before merging:**
- The response reads like a blog post intro ("RAG is a powerful technique that...")
- The response lists options without recommending one
- The response gives the same advice regardless of what context the user provides
- The skill activates on questions that belong to a different skill

---

## Filling In a Skill (Quick Steps)

1. Pick a skill from `skills/` — check the stub's "What This Skill Should Cover" section
2. Research the topic thoroughly before writing (papers, docs, practitioner blog posts, real failure post-mortems)
3. Write the `SKILL.md` body as process steps with opinions, not explanations
4. Move deep reference material to `references/` files
5. Update the trigger phrases in frontmatter to match how developers actually ask about this topic
6. Test locally, then open a PR

---

## Adding a New Skill

1. Create a new directory: `skills/advise-<topic>/`
2. Copy the stub template below into `SKILL.md`
3. Create a `references/` subdirectory
4. Add `agents/openai.yaml` for Codex support (copy from any existing skill)
5. Open a PR — stubs are welcome, partial content is welcome

### Stub Template

```markdown
---
name: advise-your-topic
description: |
  This skill should be used when the user asks to "...", "...", "...",
  "...", or needs guidance on [topic].
---

# Topic Advisor

> **Status: Stub** — This skill needs content. See [CONTRIBUTING.md](../../CONTRIBUTING.md) to fill it in.

## What This Skill Should Cover

- Point 1
- Point 2

## References

Add reference files to `references/` as you build this out.
```

### `agents/openai.yaml` Template (for Codex)

```yaml
allow_implicit_invocation: true
display_name: "Topic Advisor"
short_description: "One sentence describing what this skill advises on"
```

---

## Installing the Plugin Locally (for testing)

**Claude Code:**
```
/plugin install ai-advisor@github:NexusInitiative/AI-Agent-Advisor
```

**Codex:**
```
gh skill install NexusInitiative/AI-Agent-Advisor
```

Point to your local fork during development by substituting your GitHub username.
