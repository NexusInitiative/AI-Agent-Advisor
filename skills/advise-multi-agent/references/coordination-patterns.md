# Coordination Patterns Reference

Use this file when implementing the orchestrator, handoffs, shared state, or containment for a multi-agent system.

## Topology Selection Table

| Topology | Use when | Key risk | Mitigation |
|---|---|---|---|
| Router/handoff | Crisp intent categories; specialist owns whole task after routing | Misroute strands the task | Measure routing accuracy separately; allow re-route once |
| Manager–worker | Decomposable plan; results need validation and merge | Manager context bloat from worker output | Workers return compact artifacts + evidence links, not transcripts |
| Parallel workers + reviewer | Independent subtasks (research questions, per-file fixes) | Duplicated or conflicting work | Disjoint task specs; single merger; dedupe at dispatch |
| Producer–critic | A testable property exists (tests, citations, policy) | Rubber-stamp or endless loop | Defined pass/fail criteria; max 1–2 critique rounds |
| Blackboard | Many agents share evolving task state over time | Write conflicts, stale reads | Versioned store, single-writer per key, provenance on writes |

## Task Record (Orchestrator-Owned)

The orchestrator maintains one record per task; workers never own it:

```yaml
task_id: T-142
goal: "…"
constraints: ["…"]
budget: {tokens: N, tool_calls: N, wall_time_s: N}
status: running          # running | done | partial | failed
subtasks:
  - id: T-142.1
    worker: researcher-a
    contract: {inputs: [...], output_schema: ..., stop_rule: "..."}
    status: done
    evidence: [links]
merged_result: null
termination_reason: null
```

## Handoff Schema (Worker Input)

Send exactly this — no conversation history:

```yaml
goal: one bounded objective
constraints: hard requirements, deadline, budget slice
inputs: [paths, IDs, URLs]      # references, not pasted content
prior_work: [artifact links with one-line summaries]
output_contract: JSON schema or file spec the result must satisfy
known_risks: ["…"]
stop_rule: "return partial + reason after X attempts / Y tokens"
```

Worker output must satisfy the contract plus: `status`, `evidence`, `cost_used`, `open_questions`. The orchestrator validates all of it before acceptance — schema first, then provenance (does the evidence actually support the claims?), then budget accounting.

## Containment Checklist

- [ ] Global limits enforced in the harness: fan-out width, delegation depth, per-run token/tool/time budgets
- [ ] Worker results schema-validated before entering shared state
- [ ] Provenance recorded on every shared write (agent, inputs, evidence)
- [ ] Conflicting answers resolved by the orchestrator on evidence quality — no voting on authorized actions
- [ ] Terminal statuses required; watchdog for silent workers
- [ ] Partial-result degradation defined per fan-out (minimum viable subset)
- [ ] Injection defense at each boundary: worker-fetched web/file content cannot alter another agent's instructions (see `advise-harness`)

## Boundary Evaluation Plan

Evaluate separately, with dedicated cases (see `advise-eval`):

1. **Routing:** accuracy on a labeled intent set, including ambiguous inputs.
2. **Handoff completeness:** can a fresh worker complete the subtask from the contract alone? (Test by replaying contracts without any other context.)
3. **Worker quality:** per-worker task success on their bounded objective.
4. **Merge correctness:** injected conflicting/partial worker outputs produce correct merged results.
5. **Recovery:** kill a worker mid-run; assert the run degrades or retries per policy.
6. **End-to-end:** user-task success, total cost, and p95 latency vs. the single-agent baseline — the comparison that decides whether the topology earns its keep.
