# AI Advisor

This repository is a skill plugin for Claude Code and Codex. It provides expert advice on building AI agent systems.

## What This Repo Is

Each directory under `skills/` is a self-contained skill. When a user's question matches a skill's trigger phrases, the agent loads that skill and uses it to guide the response.

## Skills Available

| Skill | When to Use | Example trigger |
|---|---|---|
| `advise-rag` | Questions about RAG pipelines, retrieval, chunking, reranking | "my retrieval results are bad" |
| `advise-models` | Choosing models, comparing providers, cost/quality trade-offs | "which model should I use?" |
| `advise-multi-agent` | Orchestrating agents, multi-agent patterns, handoffs | "should I use multiple agents?" |
| `advise-eval` | Evaluation frameworks, LLM-as-judge, regression testing | "is my LLM judge production-ready?" |
| `advise-prompting` | Failure-first prompt diagnosis, contracts, structured output | "why is my prompt being ignored?" |
| `advise-fine-tune` | When to fine-tune, LoRA, distillation, dataset prep | "should I fine-tune or prompt-engineer?" |
| `advise-context` | Context window management, summarization, token budgets | "my agent loses track mid-task" |
| `advise-memory` | Agent memory patterns, persistent vs. session memory | "my agent keeps forgetting" |
| `advise-caching` | Prompt caching, semantic caching, cost reduction | "reduce my API costs with caching" |
| `advise-embedding` | Embedding models, dimensionality, similarity metrics | "what embedding model should I use?" |
| `advise-vector-db` | Vector database selection, ANN algorithms, hybrid search | "Pinecone vs Weaviate vs pgvector?" |
| `advise-harness` | Agent harness design, scaffolding, observability | "how do I sandbox my agent's tools?" |
| `advise-debug` | Wrong AI answers when the failing component is unknown: symptom-to-fix recipes for RAG, fine-tuning, prompts, agents, caches, and graders | "my fine-tuned model got worse" |

When the failing component is already known, use that component's skill; use `advise-debug` for answer-level symptoms and for "it worked before and broke now".

## Skill Status

All skills are **complete**: each `SKILL.md` is a decision-oriented workflow, and each `references/` directory contains focused deep-dive files plus a `source-map.md` linking every recommendation to verified primary sources. Statements that are derived (mathematical or logical consequences) or procedural (workflow steps) are labeled as such in the source maps, and no numeric threshold is given without a source. See `CONTRIBUTING.md` to deepen a skill or add a new one.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the skill format and how to add or fill in skills.
