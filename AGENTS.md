# AI Advisor

This repository is a skill plugin for Claude Code and Codex. It provides expert advice on building AI agent systems.

## What This Repo Is

Each directory under `skills/` is a self-contained skill. When a user's question matches a skill's trigger phrases, the agent loads that skill and uses it to guide the response.

## Skills Available

| Skill | When to Use |
|---|---|
| `advise-rag` | Questions about RAG pipelines, retrieval, chunking, reranking |
| `advise-models` | Choosing models, comparing providers, cost/quality trade-offs |
| `advise-multi-agent` | Orchestrating agents, multi-agent patterns, handoffs |
| `advise-eval` | Evaluation frameworks, LLM-as-judge, regression testing |
| `advise-prompting` | Prompt engineering, system prompt design, few-shot |
| `advise-fine-tune` | When to fine-tune, LoRA, distillation, dataset prep |
| `advise-context` | Context window management, summarization, token budgets |
| `advise-memory` | Agent memory patterns, persistent vs. session memory |
| `advise-caching` | Prompt caching, semantic caching, cost reduction |
| `advise-embedding` | Embedding models, dimensionality, similarity metrics |
| `advise-vector-db` | Vector database selection, ANN algorithms, hybrid search |
| `advise-harness` | Agent harness design, scaffolding, observability |

## Skill Status

All listed skills include advisor guidance and supporting references. See `CONTRIBUTING.md` to improve an existing skill or add a new one.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the skill format and how to add or fill in skills.
