# Write And Retrieve Policy

Use this reference when the user asks what the agent should save, forget, update, or retrieve.

## Write Gate

Before saving a memory, require all of these:

- Durable: likely to remain useful beyond the current turn.
- Future-relevant: likely to change a future decision or response.
- Scoped: clearly belongs to a user, project, org, thread, or agent.
- Safe: not secret, sensitive without consent, or outside policy.
- Evidenced: has a source message, tool result, document, or human approval.

Reject transient mood, raw chat filler, secrets, credentials, one-off task details, and facts inferred from weak evidence.

## Write Paths

Hot-path writes happen during the user interaction. Use them for explicit "remember this" requests or when the next turn must depend on the update. They add latency and can distract the agent.

Background writes happen asynchronously. Use them for conversation summaries, episode extraction, profile cleanup, and consolidation. They preserve latency but may leave another thread stale briefly.

Human-approved writes are best for sensitive personal facts, enterprise memory, shared procedural rules, and global instructions.

Scheduled consolidation turns raw episodes into durable facts or reusable procedures. Run it after a task completes, after feedback arrives, or on a fixed cadence.

## Update And Contradiction Handling

Do not keep contradictory records as simultaneously active current truth. Use one of these:

- Update a profile field when there is one current value.
- Add a new collection item when the new fact is independent.
- Supersede with `valid_to` when facts change over time.
- Keep both as episodes when the system only knows that conflicting statements were made.
- Ask the user when contradiction affects a high-risk decision.

Current user input should override old memory unless the user explicitly asks for historical behavior.

## Dedupe And Consolidation

Use exact IDs for structured records and semantic duplicate checks for text memories. Merge near-duplicates instead of accumulating variants like "prefers Python," "likes Python," and "usually uses Python."

Keep an append-only episode log for evidence, then periodically create or update semantic facts:

1. Select episodes with high future value.
2. Extract candidate facts or lessons.
3. Compare against active memories.
4. Add, update, supersede, delete, or noop.
5. Record source links and confidence.

## Forgetting And Decay

Use decay for retrieval priority, not silent deletion. A memory can become less likely to retrieve as it ages, unless it is reinforced by repeated use or user confirmation.

Use deletion or active exclusion for user requests, privacy requirements, unsafe content, or false memories. For audit-heavy systems, soft-delete or close validity windows while excluding the memory from active retrieval.

## Retrieval Assembly

Filter before ranking:

1. Tenant/user/project/org namespace.
2. Memory type.
3. Validity window.
4. Safety and access policy.
5. Query relevance.

Then rank by:

- Semantic relevance to the current task.
- Recency for changing facts.
- Importance for high-value facts.
- Source trust and confidence.
- Frequency of successful past use.

Return few, compact memories. Too much memory is context pollution.

## Read Modes

Use always-in-context memory only for tiny facts or instructions that should affect nearly every turn.

Use retrieved-on-demand memory for most semantic, episodic, and procedural memories.

Use tool-called memory when the agent should decide whether memory is needed.

Use few-shot retrieval when prior examples improve tool use, formatting, or task policy.

Use summary injection for active task state and long-session continuity.
