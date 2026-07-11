# Runtime Controls Reference

Use this file when implementing the agent loop, limits, approvals, tracing, or the harness test plan.

## Execution Limits Starter Table

Set every limit explicitly; "unlimited" is a decision, not a default. Starting points for an interactive task agent (tune per workload):

| Limit | Starting point | Terminal status on breach |
|---|---|---|
| Max turns per run | 25–50 | `budget_exceeded` |
| Max wall time | 10–30 min interactive; task-scaled for batch | `timeout` |
| Max tool calls per run | 100 | `budget_exceeded` |
| Retries per tool call | 2–3 with backoff | `tool_failure` |
| Spend per run (tokens/$) | product-specific hard cap | `budget_exceeded` |
| Concurrent runs per user/tenant | small integer | queued, not failed |

Every breach must produce a terminal status plus a human-readable reason in the trace. If runs routinely hit a limit while succeeding, raise the limit deliberately and record why.

## Approval Matrix

| Action class | Default policy |
|---|---|
| Read internal data within scope | Allow, log |
| Write to agent workspace/scratch | Allow, log |
| Write to shared internal systems (tickets, docs) | Allow with post-hoc review queue, or approve for new agents |
| External communications (email, posts, PRs to other repos) | Human approval |
| Money movement, deletions, production config | Human approval + second factor where supported |
| New capability/tool not in policy | Deny; policy change is a human code change |

Approval UI must show: proposed action, exact targets/scope, agent rationale, what happens on deny. Batch related approvals where safe to fight fatigue.

## Trace Field Checklist

Per run: `run_id`, `parent_run_id`, `task_id`, user/tenant, model + config, prompt/template versions, start/end, terminal status + reason, total tokens/cost.

Per step: state transition, tool name, arguments (redacted), result summary + full payload pointer, permission decision (rule matched, allow/deny), latency, retries, tokens.

Redaction happens in the trace writer via an allowlist of loggable fields — not by asking the model to avoid secrets. Verify with a test that plants a fake secret and asserts it never reaches the trace store.

## Harness Test Checklist

Deterministic (run in CI):

- [ ] Tool rejects malformed and semantically-invalid arguments (wrong tenant, out-of-scope path)
- [ ] Permission denials produce the correct terminal/paused state, never silent success
- [ ] Injection strings in web/file/tool content do not alter permission outcomes
- [ ] Timeout mid-side-effect resumes from checkpoint without duplicate effects (verify idempotency keys)
- [ ] Cancellation at every state lands in `cancelled` with cleanup done
- [ ] Concurrent runs on shared state don't interleave writes
- [ ] Budget breaches produce correct statuses at exact thresholds
- [ ] Planted secret never appears in exported traces
- [ ] Audit log reconstructs a scripted run end-to-end

Scenario (run on release): full trajectories with tool failures injected at each step, adversarial content in each untrusted channel, and approval deny/approve paths. Grade trajectories, not just final answers — see `advise-eval`.

## Staged Rollout Gates

1. **Observe-only:** agent proposes; humans execute. Exit when proposal acceptance is high and incidents are zero over a defined window.
2. **Scoped autonomy:** low-risk tool classes auto-execute; the rest gated. Exit per tool class on measured success/incident rates.
3. **Expanded autonomy:** approvals only for the irreversible classes in the matrix above. Re-enter earlier stages on incident.

Record the gate decisions — they are the governance artifact auditors and NIST-AI-RMF-style reviews will ask for.
