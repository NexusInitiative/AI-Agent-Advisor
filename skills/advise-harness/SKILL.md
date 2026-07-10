---
name: advise-harness
description: |
  This skill should be used when the user asks to "advise on agent harness", "how do I build an agent harness",
  "help with Claude Code harness setup", "what harness pattern should I use", "agent scaffolding advice",
  "how do I sandbox agent tools", "how should I trace agents", "add human approval to my agent",
  or needs guidance on agent runtime infrastructure, permissions, observability, or recovery.
---

# Harness Advisor

An agent harness is the runtime contract around a model: state, tools, permissions, execution limits, observability, approvals, and recovery. Build it before granting the model broad autonomy.

## Define the operating boundary

Write down the agent's allowed goals, users, data scopes, tools, side effects, and forbidden actions. Separate read-only discovery from actions that modify code, money, records, or external communications. Give each tool a typed input/output schema, deterministic error shape, timeout, idempotency policy, and least-privilege credential.

Run tools in a sandbox appropriate to their risk. Restrict filesystem roots, network destinations, process execution, secrets, and egress. Treat repository files, web content, tool outputs, and user text as untrusted instructions. Do not let a model override the harness permission policy through prompt text.

## Start with a controllable loop

Use an explicit state machine: receive task -> plan -> request tool -> validate tool call -> execute -> inspect result -> continue, pause, or finish. Persist a checkpoint after meaningful steps so runs can resume without replaying side effects. Enforce maximum turns, tokens, wall time, tool calls, retries, and spend. Require a terminal status and a useful failure reason.

Put human approval before irreversible or high-impact actions. Show the proposed action, affected scope, rationale, and a safe cancel path. Do not use blanket approvals for a broad class of future actions unless the product owner deliberately configures that policy.

## Make every run debuggable

Trace run IDs, model/configuration, prompt/template versions, state transitions, tool arguments/results, permission decisions, retries, token/cost use, latency, and final status. Redact secrets and sensitive content before export. Correlate child-agent work with its parent task. Keep enough provenance to reproduce a failure without retaining unnecessary personal data.

## Validate the harness, not only the answer

Test invalid tool arguments, timeouts, partial side effects, retries, prompt injection, permission escalation, secret exposure, concurrent runs, cancellation, checkpoint recovery, and audit-log completeness. Use deterministic tests for permission/schema behavior and scenario tests for agent trajectories. Start in observe-only or limited-scope mode, then expand authority based on measured safety and task success.

For evaluation see `advise-eval`; for coordination see `advise-multi-agent`; for memory see `advise-memory`.

## Sources

For runtime controls and release checks, read [runtime-controls.md](references/runtime-controls.md) and [source-map.md](references/source-map.md).

- [OpenAI Agents SDK tracing](https://openai.github.io/openai-agents-python/tracing/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
