# AI Advisor

A senior AI engineer on call in your terminal. Twelve research-backed advisor skills for Claude Code and Codex that turn questions like *"should I fine-tune or use RAG?"* or *"is my LLM judge production-ready?"* into a concrete, opinionated recommendation — not a wall of "it depends."

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg) ![Skills: 12](https://img.shields.io/badge/skills-12-brightgreen.svg) ![Claude Code + Codex](https://img.shields.io/badge/Claude%20Code-%2B%20Codex-8A2BE2.svg)

## How it works

Each skill is a decision-oriented workflow, not an encyclopedia entry. Once installed, skills trigger automatically when your question matches — ask *"my retrieval results are bad"* and the RAG advisor loads itself, asks the right diagnostic questions, and recommends a fix with the trade-off spelled out. Every recommendation is backed by a per-skill source map linking claims to primary research, so you can check the reasoning.

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

| Skill | Topic |
|---|---|
| `advise-rag` | RAG pipeline design and retrieval patterns |
| `advise-models` | Model selection and trade-offs |
| `advise-multi-agent` | Multi-agent architecture and orchestration |
| `advise-eval` | Evaluation frameworks and LLM-as-judge |
| `advise-prompting` | Prompt engineering techniques |
| `advise-fine-tune` | When and how to fine-tune |
| `advise-context` | Context window management |
| `advise-memory` | Agent memory patterns |
| `advise-caching` | Prompt and semantic caching |
| `advise-embedding` | Embedding models and strategies |
| `advise-vector-db` | Vector database selection |
| `advise-harness` | Agent harness and scaffolding |

## Contributing

All skills are complete with research-backed content and per-skill source maps. See [CONTRIBUTING.md](CONTRIBUTING.md) for the skill format, quality bar, and how to add new skills or deepen existing ones.
