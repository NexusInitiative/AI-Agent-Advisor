# Memory Taxonomy

Use this reference when a user asks what kind of memory an agent needs. These labels overlap: working, semantic, episodic, and procedural describe the role of information, while vector, graph, and temporal systems describe storage or query mechanisms. Keep the taxonomy tied to architecture choices, not cognitive trivia.

## Working Or Thread Memory

Working memory is active task state inside one thread or run: recent messages, current plan, scratchpad notes, uploaded files, tool outputs, partial artifacts, and unresolved questions. It should be checkpointed so a workflow can resume, but it normally should not become cross-session personalization.

Use it when the user says the agent "forgets what we were doing" inside an active task. Do not solve this with a vector DB; solve it with state persistence and context management.

## Summarized Session Memory

Summaries compress long active conversations. Store decisions, constraints, open tasks, source references, assumptions, and handoff state. Avoid broad narrative summaries because they blur evidence and create stale context.

Use when the conversation exceeds context or when active state must move between threads.

## Semantic Memory

Semantic memory stores facts intended to be durable: user preferences, project conventions, account properties, org rules, named entities, and stable constraints. It is usually a current-state view, not proof that a fact is true.

Recommended fields:

- `id`
- `scope`
- `type`
- `content`
- `source`
- `created_at`
- `updated_at`
- `confidence`
- `valid_from`
- `valid_to`

Use semantic memory for the current application view. When facts change, supersede old records rather than leaving two active truths, while retaining history when the product needs to answer what was true before.

## Episodic Memory

Episodic memory stores events: what happened, what was tried, what failed, what changed, and what outcome resulted. It is usually append-only and timestamped.

Use it for debugging, auditability, learning from past runs, "what happened last time?", and future consolidation. Episodes are evidence; do not treat them as current truth until consolidated.

## Procedural Memory

Procedural memory stores reusable ways of doing work: instructions, prompts, runbooks, successful command sequences, code snippets, examples, or full skills.

Use it when repeated work improves from remembered process rather than remembered facts. For coding agents, procedural memory often includes repo conventions, test commands, fragile files, and known fix patterns.

## Reflective Memory

Reflective memory stores lessons extracted from feedback or outcomes. Reflexion-style memory can improve future attempts without fine-tuning, but it is easy to over-trust weak reflections.

Use it only when a reflection is tied to concrete feedback, failure, metric movement, or human approval. Avoid generic self-critiques.

## Skill Libraries

A skill library is procedural memory made executable or semi-executable. Voyager is the clean reference pattern: successful behaviors become reusable skills that can be retrieved and composed.

Use for coding, robotics, game agents, workflow automation, and repeated tool-use tasks.

## Graph And Temporal Memory

Graph memory stores entities, relations, and events. Temporal graph memory adds validity windows so the agent can answer "what is true now?" and "what was true then?"

Use it only when relationships or time are first-class: changing preferences, account hierarchies, experiments, contracts, investigations, or multi-agent shared state. If the task is only similarity search, a graph is unnecessary.
