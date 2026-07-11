---
name: advise-harness
description: |
  This skill should be used when the user asks to "advise on agent harness", "how do I build an agent harness",
  "help with Claude Code harness setup", "what harness pattern should I use", "agent scaffolding advice",
  "how do I sandbox agent tools", "how should I trace agents", "add human approval to my agent",
  or needs guidance on agent runtime infrastructure, permissions, observability, or recovery.
---

# Harness Advisor

An agent harness is the runtime contract around a model: state, tools, permissions, execution limits, observability, approvals, and recovery. The harness — not the prompt — is what makes an agent safe to give real authority. Build it before granting autonomy, and grow authority only as measured trust grows.

## Step 1 — Diagnose the Risk Profile

Ask or infer before recommending harness machinery:

- What can the agent *touch*? Read-only data, internal writes, money, production systems, external communications?
- What is the blast radius of the worst single bad action, and is it reversible?
- Who is accountable when it misbehaves, and what evidence will they need?
- What untrusted content flows in — web pages, repo files, user uploads, emails?
- Is this one agent or a fleet? Interactive or unattended?

A read-only research assistant needs a fraction of the controls below. An unattended agent that writes to production or sends external messages needs all of them. Anthropic's [building effective agents](https://www.anthropic.com/engineering/building-effective-agents) guidance applies here: prefer the simplest architecture that works and add harness machinery in proportion to authority.

---

## Step 2 — Define the Operating Boundary in Writing

Before code: write down allowed goals, users, data scopes, tools, side effects, and forbidden actions. Separate **read/discover** tools from **act/modify** tools — this split drives permissions, approvals, and testing for everything downstream.

Give every tool a hard contract:

- Typed input/output schema, validated *outside* the model — never trust the model to self-validate arguments
- Deterministic error shape (the model should see "what failed and why," not a stack trace)
- Timeout, retry policy, and idempotency semantics (safe to retry? needs an idempotency key?)
- Least-privilege credential scoped to the tool, not a god-token shared by the process

Run tools in sandboxes matched to risk: restrict filesystem roots, network egress destinations, process execution, and secret access. Treat repository files, web content, tool outputs, and user text as untrusted data — the OWASP LLM Top 10 puts prompt injection first for a reason. The permission policy lives in the harness; prompt text (including injected text) must not be able to widen it.

---

## Step 3 — Build a Controllable Loop, Not a Free-Running One

Use an explicit state machine: receive task → plan → propose tool call → validate against policy → execute → inspect result → continue, pause for approval, or finish. The harness owns the transitions; the model proposes.

**Hard limits, enforced outside the model:** maximum turns, tokens, wall time, tool calls, retries per tool, and spend per run. Every run ends in a terminal status with a machine-readable reason (`completed`, `budget_exceeded`, `approval_denied`, `tool_failure`, `cancelled`).

**Checkpoints:** persist state after meaningful steps so runs resume without replaying side effects. Record side effects with idempotency keys so a resumed run never double-executes a payment, email, or deploy.

**Approvals:** require human approval before irreversible or high-impact actions (external communications, deletions, money, production changes). Show the approver the proposed action, affected scope, the agent's rationale, and a safe cancel. Approval fatigue is a real failure mode — scope approvals narrowly to the risky action class instead of interrupting on everything, and never let blanket approval be the accidental default.

---

## Step 4 — Make Every Run Reconstructible

Trace per run: run ID, parent/child links for subagents, model + configuration, prompt/template versions, every state transition, tool arguments and results, permission decisions (allowed/denied and why), retries, token/cost use, latency per step, and terminal status. OpenAI's Agents SDK tracing model is a reasonable reference shape even off that stack.

Redact secrets and sensitive content before export; keep enough provenance to reproduce any failure without hoarding personal data. The test: for any bad outcome, can you answer "what did the agent see, what did it decide, what did it do, and what did the harness allow?" from the trace alone — without re-running anything?

---

## Step 5 — Test the Harness Itself, Then Expand Authority Gradually

The harness has its own failure modes independent of answer quality. Test deterministically: invalid and malicious tool arguments, timeouts mid-side-effect, partial failures, retry storms, injection attempts from every untrusted channel, permission escalation attempts, concurrent runs on shared state, cancellation at every state, checkpoint recovery, and audit-log completeness. Add scenario tests for full trajectories (see `advise-eval` for trajectory grading).

Roll out in stages: observe-only (agent proposes, humans execute) → limited scope with approvals → expanded autonomy per tool class as measured incident and success rates justify. NIST's AI RMF is a useful governance frame when you need organizational sign-off for each stage.

Budget real time for this: teams routinely spend more engineering effort on the harness than on prompts, and that ratio is correct. Prompts are cheap to change and easy to test; a missing idempotency key or an over-scoped credential is discovered in production, expensively.

---

## Common Failure Modes and Fixes

| Symptom | Likely Cause | Fix |
|---|---|---|
| Agent loops burning tokens | No turn/spend budget in the harness | Enforce hard limits with terminal statuses outside the model |
| Injected web/repo text changes agent behavior | Untrusted content treated as instructions | Delimit as data, validate tool calls against policy, deny-by-default new capabilities |
| Duplicate side effects after crash/retry | No idempotency keys or checkpoints | Record side effects with keys; resume from checkpoint, never replay |
| Approvals rubber-stamped | Everything requires approval | Reserve approvals for irreversible/high-impact classes; automate the rest |
| Incident can't be reconstructed | Partial or unstructured logging | Trace the full decision chain per Step 4; test trace completeness |
| Tool misuse with valid-looking args | Schema-only validation | Add semantic policy checks (scope, quotas, allowed targets) at the boundary |
| Secrets appear in traces | Raw argument/result logging | Redact at the trace writer, not in the model prompt |

For agent coordination across multiple agents, see `advise-multi-agent`; for cross-session state, see `advise-memory`; for measuring agent quality, see `advise-eval`.

---

## References

- **Limit values, approval matrix, trace field list, and harness test checklist:** read [runtime-controls.md](references/runtime-controls.md) when implementing the loop and controls.
- **Verified sources with claims and caveats:** read [source-map.md](references/source-map.md) when citing evidence behind these recommendations.
