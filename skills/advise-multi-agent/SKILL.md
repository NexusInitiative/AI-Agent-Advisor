---
name: advise-multi-agent
description: |
  This skill should be used when the user asks to "advise on multi-agent systems",
  "should I use multiple agents", "how do I orchestrate agents", "help with agent coordination",
  "design a multi-agent pipeline", "how should agents hand off work", "should agents run in parallel",
  or needs guidance on multi-agent architecture, state, delegation, or coordination failures.
---

# Multi-Agent Advisor

**Default to one agent with tools.** Multiple agents multiply tokens, latency, and failure modes — Anthropic reported that agents used about 4× the tokens of a chat and its multi-agent research system about 15×, and that token usage alone explained 80% of the performance variance on BrowseComp, so extra agents often buy performance by spending more. Evaluating cost alongside accuracy, Kapoor et al. found state-of-the-art agents were needlessly complex and costly. Add a second agent only when a specific, measurable boundary justifies it.

## Step 1 — Diagnose Whether a Boundary Actually Exists

Ask or infer. Legitimate reasons to split:

- **Context isolation:** one context window can't hold the working state for both roles (e.g., broad codebase exploration vs. focused implementation), and summarizing between roles is cheaper than thrashing one context.
- **Permission separation:** roles need conflicting authority (a researcher that reads everything vs. an executor that writes narrowly) and the harness should enforce the difference (see `advise-harness`).
- **True parallelism:** independent subtasks with no shared mutable state — parallel research questions, per-file test fixes, fan-out document processing.
- **Independent verification:** a checker that grades a defined property with evidence or tests, kept blind to the producer's reasoning.

**Not** legitimate reasons by themselves: "more perspectives," anthropomorphic org charts (PM-agent, engineer-agent, QA-agent chatting), or hoping debate improves accuracy. Debate raised reasoning and factuality in one study (Du et al.), but a benchmark of debate strategies found current systems did not reliably outperform self-consistency or ensembling and were sensitive to hyperparameters (Smit et al.), so measure against the cheaper baseline. If the work shares context, needs tight back-and-forth, or follows one sequential tool path, keep one agent. If a single-agent baseline hasn't been measured yet, that's the next step — not architecture.

---

## Step 2 — Use the Smallest Topology That Fits the Boundary

One orchestrator owns the user goal, budget, shared state, and final response. Workers get a bounded objective, allowed tools, an input contract, an output schema, a timeout, and a stopping rule.

- **Router/handoff** — one agent classifies and hands the whole task to a specialist (by language, product area, subsystem). Simplest; use when categories are crisp. OpenAI's Agents SDK handoff model is a clean reference shape.
- **Manager–worker** — the manager decomposes, dispatches bounded subtasks, validates each result, and owns the merge. The default for decomposable work.
- **Parallel workers + one reviewer** — only for genuinely independent subtasks; all merges flow through a single reviewer/merger, never peer-to-peer reconciliation.
- **Producer–critic** — the critic checks a *defined* property (tests pass, claims cited, policy satisfied) with evidence. Open-ended "debate" loops cost more tokens and have not been shown to beat cheaper baselines reliably (Smit et al.).

Resist deeper hierarchies until a two-level topology measurably fails. Every level adds latency, cost, and a new place for context to be lost in translation.

---

## Step 3 — Make Handoffs Contracts, Not Conversations

Pass artifacts, not transcripts. A handoff should contain:

```text
goal:            one bounded objective
constraints:     hard requirements, budget, deadline
inputs:          source-of-truth references (paths, IDs, URLs) — not pasted copies
prior work:      what's done, with evidence links
output contract: machine-readable schema for the result
risks:           known traps the worker should avoid
stop rule:       when to give up and return partial + reason
```

Forwarding conversation history instead invites the worker to relitigate decisions and inherit stale context. Keep shared task state in a versioned store or blackboard the orchestrator owns; workers get private scratch space; every shared write carries provenance (which agent, from what evidence). Namespace all tenant/project state — see `advise-memory` for shared-state governance.

---

## Step 4 — Contain Failures at Every Boundary

Multi-agent error propagation is the core hazard (the coordination-mechanisms survey catalogs this well): one agent's confident mistake becomes the next agent's trusted input. The MAST analysis of 1,600+ traces across seven frameworks attributes failures to system design (41.8%), inter-agent misalignment (36.9%), and task verification (21.3%), and found that a verifier is not a silver bullet: single final-stage checks were inadequate, so verify at several levels.

- Treat each handoff as an untrusted boundary: validate output schemas, tool permissions, provenance, and budget consumption *before* the orchestrator accepts a result.
- Enforce global limits — fan-out width, recursion depth, per-run token/tool/wall-time budgets — in the harness, not by prompt request.
- The orchestrator resolves conflicting worker answers by evidence quality; never let agents vote on an action requiring authorization.
- Require terminal statuses from workers (`done`, `partial`, `failed:<reason>`) so silent worker death doesn't hang the run.
- Design for partial results: a research fan-out returning four of five branches should degrade gracefully, not abort.

---

## Step 5 — Trace and Evaluate Each Boundary Separately

Trace parent run → child runs with task IDs, inputs, outputs, tool calls, cost, latency, and termination reason per worker (see `advise-harness` for the trace shape). Evaluate end-to-end success *and* per-boundary metrics: routing accuracy, handoff-contract completeness, worker quality on their bounded task, merge correctness, and recovery from injected worker failures. An end-to-end score alone cannot tell you whether the router, the worker, or the merge lost the run — see `advise-eval`.

**Decision rule:** if the measured single-agent baseline misses target because of context overload, permission conflicts, or parallelizable independence — add *one* bounded worker, re-measure, and only then consider more. If the addition doesn't move the metric, remove it. Do not build the society of agents first.

When reviewing an existing multi-agent design, apply the collapse test to each agent: "if this agent were a plain function call or tool used by its neighbor, what would break?" If the honest answer is "nothing," collapse it. Systems that survive the collapse test tend to have two or three agents with sharp boundaries, not seven with fuzzy ones.

---

## Common Failure Modes and Fixes

| Symptom | Likely Cause | Fix |
|---|---|---|
| Token cost many times a single agent, quality flat (Anthropic: about 4× chat tokens for an agent, about 15× for multi-agent) | Split without a real boundary | Collapse to one agent + tools; re-measure |
| Workers redo or contradict each other's work | Transcript handoffs, no shared task record | Artifact contracts + orchestrator-owned state |
| One wrong claim propagates to the final answer | No validation at boundaries | Schema + provenance checks before accepting results |
| Infinite delegation loops | No depth/fan-out limits in the harness | Hard global budgets with terminal statuses |
| Critic approves everything | Open-ended review, no defined property | Give the critic testable criteria and evidence requirements |
| Can't tell which agent failed | End-to-end metrics only | Per-boundary tracing and evals |
| Race conditions on shared state | Peer-to-peer writes | Single-writer merge through the orchestrator |

To diagnose an existing failing run, tag its traces with the MAST failure modes (step repetition, reasoning-action mismatch, unawareness of termination, disobeyed specification, and so on) using `advise-debug` recipe A4.

---

## References

- **Topology details, handoff schema, blackboard pattern, and containment checklist:** read [coordination-patterns.md](references/coordination-patterns.md) when designing or debugging the coordination layer.
- **Verified sources with claims and caveats:** read [source-map.md](references/source-map.md) when citing evidence behind these recommendations.
