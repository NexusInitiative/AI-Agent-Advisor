# AI Advisor

A senior AI engineer on call in your terminal. Twelve research-backed advisor skills for Claude Code and Codex that turn questions like *"should I fine-tune or use RAG?"* or *"is my LLM judge production-ready?"* into a concrete, opinionated recommendation — not a wall of "it depends."

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg) ![Skills: 12](https://img.shields.io/badge/skills-12-brightgreen.svg) ![Claude Code + Codex](https://img.shields.io/badge/Claude%20Code-%2B%20Codex-8A2BE2.svg)

## How it works

Each skill is a decision-oriented workflow, not an encyclopedia entry. Once installed, skills trigger automatically when your question matches — ask *"my retrieval results are bad"* and the RAG advisor loads itself, asks the right diagnostic questions, and recommends a fix with the trade-off spelled out. Every recommendation is backed by a per-skill source map linking claims to primary research, so you can check the reasoning.

## Example

You don't invoke anything — you just ask. Here's the shape of an exchange `advise-rag` produces (illustrative):

```text
You ›  My RAG keeps missing the right passage. Should I switch embedding models?

AI Advisor ›  One diagnostic question first: are your queries keyword-heavy
              (error codes, product names, exact strings), or conceptual
              ("how does X relate to Y")?

You ›  Mostly exact error strings pulled from support tickets.

AI Advisor ›  Then a new embedding model won't fix it. Dense retrieval matches
              *meaning*, not tokens, so an exact error code gets blurred into
              similar-looking ones — that's a token-matching gap, not an
              embedding-quality gap.

              Recommendation: add BM25 (sparse) retrieval and fuse it with your
              dense results using Reciprocal Rank Fusion (k = 60). Hybrid almost
              always beats either method alone on mixed queries, and it needs no
              training. Measure context recall on ~50 real tickets before and
              after, so the lift is provable rather than assumed.
```

Every skill follows the same pattern: **diagnose first, then give one opinionated recommendation with the trade-off named** — not a list of ten options to figure out yourself.

## Install (Claude Code)

```
/plugin marketplace add NexusInitiative/AI-Agent-Advisor
/plugin install ai-advisor@ai-agent-advisor
```

## Install (Codex)

Requires GitHub CLI v2.90.0 or later (`gh skill` is built in).

```
gh skill install NexusInitiative/AI-Agent-Advisor --agent codex
```

Or install a single skill by name:

```
gh skill install NexusInitiative/AI-Agent-Advisor advise-rag --agent codex
```

## Skills

| Skill | Topic | Ask it something like… |
|---|---|---|
| `advise-rag` | RAG pipeline design and retrieval patterns | *"my retrieval results are bad"* |
| `advise-models` | Model selection and trade-offs | *"which model should I use for this?"* |
| `advise-multi-agent` | Multi-agent architecture and orchestration | *"should I use multiple agents?"* |
| `advise-eval` | Evaluation frameworks and LLM-as-judge | *"is my LLM judge production-ready?"* |
| `advise-prompting` | Prompt engineering techniques | *"why is my prompt being ignored?"* |
| `advise-fine-tune` | When and how to fine-tune | *"should I fine-tune or prompt-engineer?"* |
| `advise-context` | Context window management | *"my agent loses track mid-task"* |
| `advise-memory` | Agent memory patterns | *"my agent keeps forgetting"* |
| `advise-caching` | Prompt and semantic caching | *"reduce my API costs with caching"* |
| `advise-embedding` | Embedding models and strategies | *"what embedding model should I use?"* |
| `advise-vector-db` | Vector database selection | *"Pinecone vs Weaviate vs pgvector?"* |
| `advise-harness` | Agent harness and scaffolding | *"how do I sandbox my agent's tools?"* |

## Contributing

All skills are complete with research-backed content and per-skill source maps. See [CONTRIBUTING.md](CONTRIBUTING.md) for the skill format, quality bar, and how to add new skills or deepen existing ones.
