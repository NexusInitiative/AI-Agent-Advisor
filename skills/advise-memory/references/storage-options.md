# Storage Options

Use this reference when choosing where memory should live. Storage should follow the policy; it should not define the policy.

| Store | Good For | Limits |
|---|---|---|
| JSON profile | Small user/org/project facts | Gets brittle as fields grow and conflict |
| Document collection | Many scoped facts or notes | Needs dedupe, update, and retrieval policy |
| SQLite/Postgres | Typed facts, episodes, audit logs | Requires schema design and migrations |
| Postgres + pgvector | Transactional records plus semantic retrieval | More ops work than a hosted vector DB |
| Vector DB | Similarity search over text memories | Does not handle truth, scope, updates, or consent alone |
| KV store | Fast thread state, sessions, checkpoints | Weak for querying and audit |
| Graph DB | Entities, relations, temporal reasoning | Can overfit simple problems and grow complex |
| Markdown/files | Repo runbooks and human-readable project memory | Weak concurrency and access control |
| Event log | Append-only episodes and audit trails | Needs consolidation for efficient use |

## Practical Defaults

Use a checkpointer or KV/relational store for short-term thread state.

Use Postgres or SQLite for typed semantic facts and episodic logs. Add `pgvector` only when semantic retrieval is needed over memory text.

Use a vector DB when the memory corpus is large, text-heavy, and similarity search is the main access pattern. Still keep metadata filters for user/project scope, timestamps, source, confidence, and active status.

Use markdown files for coding-agent project memory when humans should review or edit the memory. Examples: `decisions.md`, `runbook.md`, `known-failures.md`. Do not use files for multi-tenant personal data unless access control is handled elsewhere.

Use graph storage when queries are relationship-first: "which experiments contradict this result?", "which accounts are affected by this policy change?", "what was true about this entity last month?"

## Minimal Schema

For a typed memory table, start with:

- `id`
- `tenant_id`
- `user_id` or `project_id`
- `agent_id`
- `memory_type`
- `content`
- `structured_value`
- `source_type`
- `source_id`
- `confidence`
- `created_at`
- `updated_at`
- `valid_from`
- `valid_to`
- `deleted_at`

If using embeddings, store them as an index over selected fields. Do not embed oversized raw transcripts; extract concise candidate memories first.

## Concurrency

If multiple agents can write memory, use transactional semantics for current facts. Vector stores alone are usually not enough for concurrent updates because they do not resolve active truth, write ordering, or auditability.

For shared memory, prefer append-only writes plus a consolidated current-state view. Require approval for global procedural memory.

## Where Not To Put Memory

Do not store secrets or credentials in memory. Use secret managers.

Do not store volatile task scratch in long-term memory. Use thread state.

Do not store every chat turn as semantic memory. Keep raw transcripts only when the product requires history search and has retention controls.
