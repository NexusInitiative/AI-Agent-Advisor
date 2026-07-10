---
name: advise-multi-agent
description: |
  This skill should be used when the user asks to "advise on multi-agent systems",
  "should I use multiple agents", "how do I orchestrate agents", "help with agent coordination",
  "design a multi-agent pipeline", "how should agents hand off work", "should agents run in parallel",
  or needs guidance on multi-agent architecture, state, delegation, or coordination failures.
---

# Multi-Agent Advisor

Default to one agent with tools. Add another agent only when work can be isolated by role, permissions, context, or latency and the coordination benefit exceeds extra tokens, delay, and failure modes.

## Diagnose the boundary

Ask whether the task needs different expertise, conflicting permissions, independent parallel work, or a separate verification step. Keep one agent when the work shares the same context, requires frequent back-and-forth, or has a single sequential tool path. "More perspectives" alone is not a sufficient reason.

## Use the smallest topology

Start with an orchestrator that owns the user goal, state, budget, and final response. Give workers a bounded objective, allowed tools, input contract, output schema, timeout, and stopping rule.

- Use a **router/handoff** for clear intent categories such as language, account type, or subsystem.
- Use **manager-worker** for decomposable plans where the manager validates each result.
- Use **parallel workers** only for independent research, tests, or files; merge through one reviewer.
- Use a **critic** only when it checks a defined property with evidence or tests. Avoid open-ended self-debate.

Pass artifacts, not conversation transcripts. A handoff should include goal, constraints, source-of-truth references, completed work, evidence, remaining risks, and a machine-readable result where possible. Put shared task state in a versioned blackboard or store; keep private scratch state private. Namespace all tenant and project state.

## Make failure contained

Treat each handoff as an untrusted boundary. Validate schemas, tool permissions, provenance, and budgets before accepting a worker result. Limit fan-out, depth, retries, token budgets, tool calls, and wall time. Require the manager to resolve conflicting answers; never have agents vote on an action that needs authorization.

Trace the parent run, child run, task ID, inputs, outputs, tool calls, cost, latency, and termination reason. Evaluate end-to-end success and each boundary: routing accuracy, handoff completeness, tool safety, worker quality, merge correctness, and recovery.

## Decision rule

If a single-agent baseline misses a measurable target because of context overload, permission separation, or independent work, add one bounded worker and re-evaluate. Do not build a society of agents before this passes.

For durable facts and shared state, see `advise-memory`; for agent runtime controls, see `advise-harness`; for evaluation, see `advise-eval`.

## Sources

For topology selection, handoff contracts, and boundaries, read [coordination-patterns.md](references/coordination-patterns.md) and [source-map.md](references/source-map.md).

- [OpenAI Agents SDK handoffs](https://openai.github.io/openai-agents-python/handoffs/)
- [AutoGen multi-agent framework paper](https://arxiv.org/abs/2308.08155)
- [Multi-agent collaboration survey](https://arxiv.org/abs/2501.06322)
