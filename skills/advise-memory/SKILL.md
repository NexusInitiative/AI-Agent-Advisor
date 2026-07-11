---
name: advise-memory
description: |
  This skill should be used when the user asks to "how do I add memory to my agent",
  "my agent keeps forgetting", "should I use LangGraph memory or a vector DB",
  "short-term vs long-term memory", "semantic vs episodic vs procedural memory",
  "how should my coding agent remember past bugs", "how do I stop memory from getting stale",
  "how do I evaluate agent memory", "what should my agent save or forget",
  "persistent memory for a chatbot", "persistent memory for a coding agent",
  "memory for a companion agent", or needs guidance designing, debugging, governing,
  or evaluating agent memory architecture.
---

# Memory Advisor

Treat agent memory as an architecture decision, not a feature checkbox. The useful question is not "what memory system should I add?" but "what future decision will improve because the agent remembered this, and what harm happens if it remembers incorrectly?"

Use the write -> manage -> read loop:

1. Write: decide what is eligible to become memory.
2. Manage: merge, update, expire, scope, delete, and resolve contradictions.
3. Read: retrieve or inject only memories that should affect this turn.

Do not recommend cross-session memory until the task actually needs continuity beyond the active context. “Long-term” does not mean global: it may be scoped to one user, project, or run history. A vector DB is retrieval infrastructure, not a memory policy.

## Step 1 - Diagnose The Need

Ask or infer these before recommending:

- What must persist: active task state, user facts, project decisions, past failures, examples, instructions, or entity relationships?
- What is the scope and lifecycle: per thread, user, project, repo, org, agent, or global, and for how long?
- What is the worst failure: forgetting, stale recall, cross-user leakage, unsafe personalization, memory poisoning, or irrelevant context?
- What is the source of truth: exact history, current state, approved policy, learned process, or some combination?

If the user only needs continuity inside one conversation or workflow, recommend short-term checkpointed state. If the user needs continuity across sessions, add narrowly scoped long-term memory. If the user needs source-grounded facts from documents, use RAG or another knowledge store; memory and RAG can coexist, but do not silently turn retrieved document text into personal or global memory.

## Step 2 - Start With The Smallest Useful Architecture

Start with the smallest stack that matches the need:

- Short-term thread checkpointing for active task state.
- Add a small typed semantic store for durable facts or preferences that must cross sessions.
- Add an episodic log for events, decisions, failures, tool calls, and outcomes when auditability, debugging, or learning justifies it.
- Explicit namespaces such as `(user_id, app_id)`, `(project_id, repo_id)`, or `(org_id, policy_id)`.
- Write gate that saves only stable, useful, future-relevant information.
- Retrieval ranked by relevance, recency, importance, trust, and scope.
- Periodic consolidation only when episodes need to become semantic facts or procedural lessons.
- User-visible correction and deletion controls for personal memory.

Avoid starting with graph storage, autonomous reflection, or broad vector storage. Add them when the query shape or evaluations justify their operational and safety cost.

## Step 3 - Choose The Memory Type

Use short-term state when the agent needs continuity inside an active thread: current plan, files touched, tool results, open questions, and intermediate artifacts. Persist it with checkpoints so the thread can resume.

Use summarized session memory when the live context is too long. Summarize decisions, constraints, unresolved tasks, and references. Do not summarize raw chat into vague narrative; summaries should preserve operational state.

Use semantic memory for facts intended to be durable: user preferences, project conventions, org policies, account settings, and durable entities. Treat it as a current-state view, not automatically as ground truth. Store typed records with `content`, `scope`, `source`, `created_at`, `updated_at`, `confidence`, and optional `valid_from`/`valid_to`.

Use episodic memory for what happened: traces, decisions, failed attempts, feedback, incidents, and outcomes. Keep episodes append-only by default, subject to retention and deletion requirements. They are evidence; semantic facts are conclusions.

Use procedural memory when the agent should repeat a better process: runbooks, examples, prompts, reusable commands, code snippets, or skills. For coding agents, this is often more valuable than remembering chat history.

Use reflection or lesson memory only when feedback is concrete and outcome-linked. This is a derived category, not a guarantee of correctness. A reflection such as "next time, run the focused test before refactoring" is useful; a broad self-critique from weak evidence is memory pollution.

Use graph or temporal representations only when relationships and time matter: changing user preferences, customer/account hierarchies, experiments, contracts, or multi-party state. These are query/storage choices that can support semantic or episodic memory; they are not replacements for write and access policy. If the only query is "find similar past notes," graph storage is unnecessary.

See [memory-taxonomy.md](references/memory-taxonomy.md) and [architecture-patterns.md](references/architecture-patterns.md) for deeper breakdowns.

## Step 4 - Decide The Write Policy

Memory quality is mostly write-policy quality. Use a write gate:

- Save only information that is durable, future-relevant, scoped, and safe.
- Prefer explicit user requests for personal facts: "remember that..."
- Require evidence for inferred memories; store the source and confidence.
- Update or supersede contradictions instead of keeping competing current truths; retain the conflicting statements as episodes when historical accuracy matters.
- Exclude secrets, credentials, highly sensitive personal data, and transient mood unless the product has explicit consent and a clear use case.

Choose the write path:

- Hot path: write before responding when the next turn needs the memory or the user asked explicitly. Costs latency and may distract the agent.
- Background: extract and consolidate after the interaction. Better for logs, summaries, and profile maintenance.
- Human-approved: use for enterprise policy, sensitive personal memory, procedural rules, and shared/global memory.
- Scheduled consolidation: periodically merge episodes into semantic facts or procedural lessons.

Do not let the agent write everything. Trash memory becomes trash context.

## Step 5 - Decide The Read Policy

Current, explicit user input should normally outrank older inferred memory for the same scope, but it does not override system/developer instructions, authorization, safety policy, or a verified source of truth. If the user asks about history, retrieve the historical record instead of rewriting current state. Read policies should decide what enters context:

- Always-in-context: only tiny high-value memories, such as user-visible instructions or active project constraints.
- Retrieved-on-demand: semantic facts, episodes, examples, and archival notes.
- Tool-called: use when the agent should decide whether to search memory.
- Summary injection: use for long sessions and active task state.
- Few-shot retrieval: use episodic examples to improve formatting, tool use, or task style.

Assemble memory with scope filters first, then ranking. A good default score combines semantic relevance, recency, importance, source trust, and whether the memory is still valid. Never retrieve across users or tenants by default.

See [write-retrieve-policy.md](references/write-retrieve-policy.md).

## Step 6 - Add Governance

Every long-term memory system needs governance before launch. The exact requirements depend on the product, jurisdiction, and data handled; involve the appropriate privacy, security, and legal reviewers for sensitive or regulated use cases.

- Namespaces for user, project, org, app, and agent boundaries.
- Provenance: source message, tool run, document, human approval, or system event.
- Timestamps and validity windows for changing facts.
- Confidence and verification status for inferred facts.
- Deletion, correction, export, retention, and "do not remember this" controls.
- Audit trails for shared, procedural, or enterprise-impacting memory.
- Memory poisoning defenses: source trust, write approvals, anomaly checks, and no global writes from untrusted input.

Per-user and global memory must be isolated by default. Shared memory is a deliberate product decision, not a shortcut.

See [privacy-and-safety.md](references/privacy-and-safety.md) and [storage-options.md](references/storage-options.md).

## Step 7 - Evaluate Before Trusting It

Do not ship memory because demos feel personalized. Test it:

- Write policy: does it save the right facts and reject unsafe or useless ones?
- Retrieval: does the needed memory appear in top results under correct scope?
- Answer quality: does memory improve task success without irrelevant personalization?
- Temporal updates: does new information supersede old information?
- Abstention: does the agent avoid claiming memory when it has none?
- Privacy: can one user, tenant, or project retrieve another's memory?
- Regression: do memory changes improve measured cases without hurting baseline behavior?

Use LongMemEval/LoCoMo-style scenarios for multi-session recall, temporal reasoning, knowledge updates, and abstention, but treat them as research benchmarks and scenario templates rather than product guarantees. Add domain-specific cases and human review for high-impact decisions. For implementation details, see [evaluation.md](references/evaluation.md).

## Decision Branches

For a personal assistant, use a small semantic profile, episodic summaries, explicit user controls, and conservative sensitive-data rules.

For a coding agent, remember repo conventions, decisions, fragile files, failed attempts, commands run, successful fixes, and reusable procedural snippets. Do not store full chat history as the primary memory.

For customer support, use user/account-scoped facts, ticket episodes, strict audit logs, policy-safe retrieval, and no cross-customer recall.

For multi-agent systems, use a shared blackboard for task state, private per-agent scratch state, scoped shared memory, and provenance on every write.

For research or science agents, use experiment logs, temporal facts, datasets, hypotheses, and contradiction handling. Prefer append-only evidence plus current-state views.

For companion or game agents, use episodic memory, importance/recency ranking, stable preferences, relationship context, and careful forgetting. Do not save every turn.

## Common Failure Modes

| Symptom | Likely Cause | Fix |
|---|---|---|
| Memory makes answers worse | Irrelevant recall | Add stricter scope filters and top-k limits |
| Agent remembers false facts | Weak write gate | Require source, confidence, and contradiction checks |
| Stale preferences keep appearing | No validity model | Add `valid_to`, recency decay, and user correction |
| Vector DB becomes a junk drawer | Storage without policy | Define schemas, write rules, and consolidation |
| Cross-user leakage | Bad namespace design | Partition by tenant/user/project before retrieval |
| Reflection creates fake lessons | No outcome evidence | Write reflections only from verified failures or feedback |
| Memory is too slow | Hot-path extraction | Move consolidation to background |
| Agent over-personalizes | Too much always-in-context memory | Retrieve on demand and cap personal facts |

Use [source-map.md](references/source-map.md) when citing the research behind these recommendations.
