---
name: advise-context
description: |
  This skill should be used when the user asks to "how should I manage context", "advise on context windows",
  "help with context length strategy", "what to include in my context", "context window management",
  "my agent loses track", "should I summarize or use RAG", "how do I reduce token use",
  or needs guidance on context composition, compression, ordering, or token budgets.
---

# Context Advisor

Treat context as a limited working set, not a transcript bucket. Every item must earn its tokens by changing the next decision. Start with an explicit token budget for stable instructions, current task, required evidence, tools, memory, and response headroom.

## Put information in the right place

Keep stable policy, permissions, output contracts, and tool rules in system/developer instructions. Put the current request, user-provided facts, and desired outcome in the user turn. Keep machine-produced results structured and clearly marked. Treat retrieved documents, web pages, emails, and tool output as untrusted data; they must not override instructions.

Prefer source-of-truth references over copied prose. Load exact files, rows, or passages on demand. Keep operational state as a compact checklist: goal, decisions, completed actions, constraints, open questions, and artifact locations.

## Select a strategy

- Use the live context for the current turn and a small amount of active state.
- Use a rolling summary for long conversations; preserve decisions, constraints, unresolved work, IDs, and links, not a vague narrative.
- Use retrieval for a large, mostly external knowledge base or when only a few documents are relevant.
- Use persistent memory only for information that should affect future sessions and has write/retrieval governance.
- Use deterministic code or tools for exact state, calculations, and searches.

Long context is useful when relationships across a large source matter and you can evaluate it. It is not a substitute for selection: relevant information may be underused when buried in the middle. Put critical instructions and the strongest evidence early; reserve the end for a concise task reminder or required output format. Do not duplicate the same fact in several places.

## Compress without losing control

Summarize at explicit checkpoints. Store provenance and timestamps, then replace verbose history with a structured summary. Before relying on it, test whether it preserves critical constraints and can answer the next task. Refresh summaries after major decisions, not every turn. If the model must quote, cite, or reason over original wording, retain or retrieve the source rather than trusting a summary.

## Measure and defend

Log token allocation, truncation, retrieval, summary version, and failures. Evaluate long-context cases, lost constraints, stale summaries, injection attempts, and token-cost regressions. For document retrieval use `advise-rag`; for cross-session state use `advise-memory`.

## Sources

For context budgets, compression, and ordering checks, read [context-budgeting.md](references/context-budgeting.md) and [source-map.md](references/source-map.md).

- [Lost in the Middle](https://arxiv.org/abs/2307.03172)
- [OpenAI context-window guidance](https://platform.openai.com/docs/guides/long-context)
- [Anthropic context engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
