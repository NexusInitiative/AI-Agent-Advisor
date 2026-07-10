# Architecture Patterns

Use this reference to map an agent problem to a concrete memory architecture.

| Pattern | Use When | Default Advice |
|---|---|---|
| No memory | One-shot tasks, stateless APIs, privacy-sensitive flows | Do not add memory just because it sounds agentic. |
| Checkpoint-only | Multi-turn task continuity inside one thread | Persist graph/thread state first. |
| Summary memory | Long active sessions exceed context | Summarize state, decisions, constraints, and open tasks. |
| Typed semantic store | Cross-session personalization or project facts | Store scoped records with schema, source, time, and confidence. |
| Episodic log | Need auditability, debugging, learning from runs | Append events and outcomes; consolidate later. |
| RAG-backed store | Large unstructured memory corpus | Treat it as retrieval infrastructure; still define write/read policy. |
| Graph/temporal memory | Need entity, relationship, or time reasoning | Add only when relational queries justify the operational cost. |
| Virtual context manager | Agent must actively page large state | Use MemGPT/Letta-style tiers: core context plus archival memory. |
| Coding-agent runbook | Repo agent repeats tasks over time | Store decisions, commands, failures, conventions, and fix patterns. |

## Recommended Baseline

For most production agents that actually need memory:

1. Checkpoint active thread state.
2. Store append-only episodes for events and outcomes.
3. Store a small typed semantic profile or project fact store.
4. Consolidate episodes into semantic or procedural memory in the background.
5. Retrieve with strict namespace filters and ranking by relevance, recency, and importance.

This is enough for most assistants, support agents, coding agents, and workflow agents.

## When To Choose Each Pattern

Choose no memory when outputs should depend only on the current request and approved sources. This is common for compliance-heavy flows, public web tools, and sensitive intake forms.

Choose checkpoint-only when the problem is "resume this workflow" rather than "remember me next week." LangGraph-style short-term memory is the canonical shape: thread state persisted through checkpoints.

Choose summary memory when context length, latency, or cost is the issue. A summary should preserve operational facts, not emotional color.

Choose typed semantic memory when personalization or durable project state matters. Prefer JSON or relational schemas before introducing vector search.

Choose episodic memory when the agent must learn from history or explain decisions. For coding agents, this should include commands run, failing tests, touched files, rejected approaches, and successful fixes.

Choose procedural memory when repeated tasks should improve. Examples: "always run this migration check," "this repo uses pnpm, not npm," "when this API fails, inspect these logs first."

Choose graph/temporal memory when facts change and the agent must preserve both current and historical truth. Use active filters such as `valid_to IS NULL` for current-state retrieval.

Choose virtual context management when the agent needs much more state than fits in the LLM context and must decide what to page in. This adds complexity; it is justified for long conversations, document-heavy work, and autonomous agents with large task state.

## Anti-Patterns

- Storing every message as memory.
- Using a vector DB as the whole memory architecture.
- Mixing all users, projects, and agents in one namespace.
- Letting autonomous agents edit global rules without approval.
- Treating old memory as more authoritative than current user input.
- Adding reflection before there are outcome metrics.
