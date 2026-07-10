# Privacy And Safety

Use this reference when the user asks about stale, unsafe, sensitive, or cross-user memory.

## User Control

Personal memory needs visible controls:

- Show what is remembered when feasible.
- Let users correct memory.
- Let users delete individual memories.
- Let users disable memory.
- Support "do not remember this" and temporary/private modes.
- Explain whether deleting a chat deletes saved memory; do not assume those are the same store.

OpenAI's Memory FAQ is a useful product-control model: saved memories, chat-history-derived personalization, temporary chat, deletion controls, and separation between chat history and saved memory all matter for user expectations.

## Consent And Sensitive Data

Default to excluding:

- Credentials, API keys, tokens, and passwords.
- Government IDs and financial account numbers.
- Health, biometric, sexual, religious, political, or minor-related data unless the product explicitly requires it and has consent.
- Private third-party facts the user did not authorize storing.
- Transient emotional state unless it is core to the product and consented.

For sensitive but legitimate use cases, require explicit consent, narrow scope, retention limits, and auditability.

## Isolation

Partition memory by tenant, user, project, org, and agent. Apply namespace filters before semantic retrieval. Test that similar users or projects cannot retrieve one another's memories.

Never use global memory as a shortcut for shared learning. Global procedural rules should be curated, reviewed, and versioned.

## Provenance And Trust

Every memory should carry:

- Source type and source ID.
- Timestamp.
- Writer identity: user, agent, system, human reviewer.
- Confidence or verification status.
- Scope and access policy.

Use source trust in retrieval ranking. Human-approved policy should outrank inferred memory. Current user input should outrank older memory.

## Staleness

Changing facts need validity windows or explicit supersession. Do not leave "user prefers Python" and "user prefers TypeScript" both active unless they are scoped to different contexts.

For memories that may decay, lower retrieval priority over time. Do not silently delete personal memory unless the retention policy says so or the user requests it.

## Memory Poisoning

Memory poisoning happens when untrusted input causes the agent to store false, unsafe, or attacker-controlled memory for later use.

Defenses:

- Reject writes from untrusted retrieved documents unless confirmed.
- Do not let web pages or user-uploaded docs write global memory.
- Require approval for procedural or policy memories.
- Store source and confidence.
- Detect sudden high-volume or high-impact memory changes.
- Keep append-only evidence for audit.

Graph or temporal memory has its own poisoning risk: fake historical events can make poisoned "current truth" look legitimate. Use source trust, transaction logs, and active-state filters.

## Right To Forget

Implement deletion as an active retrieval guarantee: once deleted, memory must not appear in future context. In regulated systems, you may also need hard deletion. In audit-heavy systems, soft deletion can preserve lineage, but active retrieval must exclude deleted records.
