---
name: advise-prompting
description: |
  This skill should be used when the user asks to "advise on prompting", "help me write a better prompt",
  "improve my system prompt", "why is my prompt ignored", "should I use few-shot examples",
  "make my model follow instructions", "how do I prompt a reasoning model",
  "should I tell the model to think step by step", "my prompt changes keep breaking other cases",
  "help me diagnose an LLM failure before changing the prompt", or "apply failure first, technique second",
  or needs guidance on prompt contracts, structured output, reasoning-model prompting, or choosing a
  measured intervention for an apparent prompting failure. For evaluation-system design, use advise-eval;
  for retrieval architecture, use advise-rag; for runtime permissions and injection controls, use advise-harness;
  when wrong answers appear in production and the broken component is unknown, use advise-debug.
---

# Prompting Advisor

**Failure first, technique second.** Name the failed requirement, reproduce it, probe the suspected bottleneck, change one component, and prove that the complete application improved. Treat the prompt as an interface contract: task, inputs, evidence, output, constraints, and failure behavior.

Start with a minimal explicit prompt and a small diagnostic regression set. Add examples, retrieval, reasoning effort, retries, or training when a controlled comparison supports the intervention. This skill owns the prompt, the contract, and the output interface. When the symptom is a wrong answer and the broken component is unknown (retrieval, tuned weights, tools, cache, or grader), start with `advise-debug`; read [failure-first.md](references/failure-first.md) when a prompting complaint could originate in another component.

## Step 1 — Establish the failed requirement

Ask or infer four things before rewriting:

- What exact input, output, or action failed, and what should have happened?
- Which model/configuration, evidence, tools, and consuming application produced it?
- Which constraints are mandatory, and what should happen when required information is missing?
- What baseline cases and latency/cost budgets are available for comparison?

Use existing context. Ask a targeted question when its answer changes the recommendation; proceed with a stated assumption when it does not. Distinguish task success, constraint compliance, and communication quality. A polished answer can conceal an unsupported price; a correct final database state can conceal an unauthorized intermediate write.

Reproduce the case with the same evidence and environment. Inspect the raw provider response, completion status, parsed result, tool trace, and relevant state. Verify the expected answer and grader before attributing the failure to the model.

Check contradictions and omitted failure behavior first. Replace vague adjectives such as “format nicely” with observable requirements; IFEval is built on exactly this idea of instructions whose compliance can be verified by code. Keep a concrete failing example and its raw trace: reading transcripts is how a genuine model mistake is told apart from a grader that rejected a valid answer or a broken task.

## Step 2 — Locate the bottleneck

Use one controlled substitution to choose the next experiment:

| Symptom | Probe | Next step if it helps |
|---|---|---|
| Invented or stale fact | Supply authoritative evidence directly | Fix evidence access with `advise-rag` |
| Evidence present but ignored | Supply only necessary evidence | Test selection, order, and evidence-use instructions |
| Wrong calculation with sufficient inputs | Supply a verified calculation | Offload exact computation; compare effort/model settings with `advise-models` |
| Invalid JSON | Inspect refusal/truncation; try supported constrained output | Fix output interface or configuration |
| Correct raw answer, broken application result | Replay a known-good response through the adapter | Fix parsing, streaming assembly, or integration |
| Wrong tool or arguments | Replay a known-correct call in a safe fixture | Improve tool purpose, arguments, or extraction |
| Correct call fails | Execute it directly in a safe fixture | Fix API, permissions, timeout, or data state |
| Retrieved instructions cause unsafe actions | Test executor enforcement without model cooperation | Fix authorization with `advise-harness` |

These probes suggest a bottleneck; they do not prove that every failure has one cause. Retest the full workflow after changing a component. Do not prescribe a larger model for missing evidence or a longer prompt for a broken adapter.

## Step 3 — Write the minimum contract

Put stable application policy, task rules, evidence rules, and tool restrictions in the provider's trusted instruction layer. Put the current request in the user turn and external documents/tool results in data channels. OpenAI's agent-safety guidance warns that untrusted input placed in a developer message gets the highest degree of control over the model. Make precedence explicit without treating a textual declaration as an enforced security boundary.

Specify the transformation, required fields, units, source associations, output consumer, and handling of empty, contradictory, malformed, or insufficient input. For extraction, retain source spans and the association between each value and its record. Finding an ID somewhere in the input does not verify that association.

Prefer “do X when Y” rules. Keep prohibitions that express important constraints; remove redundant emphasis and conflicting examples. Add a role when it supplies concrete behavior or domain context.

Use XML, Markdown sections, or structured records to make evidence boundaries readable. Tags and JSON organize content; they do not enforce authorization or prevent injection, because indirect prompt injection works by placing instructions inside retrieved data (Greshake et al.). Keep untrusted content out of privileged instructions and enforce object, action, and destination permissions in the executor. Refer runtime design to `advise-harness`.

Specify a parseable missing-evidence outcome such as `NOT_FOUND`, `NEEDS_INPUT`, or `CONFLICTING_EVIDENCE`, with what is missing. Apply only explicit, appropriate defaults. Do not force plausible values into required factual fields. Read [prompt-contracts.md](references/prompt-contracts.md) for the contract template.

## Step 4 — Control shape; validate meaning

For machine-consumed output, use the provider's supported structured-output mode and validate in application code. Check the serving system's schema subset and endpoint syntax: OpenAI Responses and Chat Completions use different configuration nesting; Anthropic has its own schema behavior.

Treat refusal, incomplete generation, and transport errors as separate states before parsing. A schema guarantee under supported conditions does not guarantee that every request completes or every value is true. Represent missing values explicitly. Validate field relationships, units, allowed IDs, evidence support, and business constraints separately.

Retry with a specific validation error when semantic repair is appropriate. Fix insufficient output budgets or unsupported settings directly. Use bounded backoff for transient service errors; inspect state or use idempotency before retrying uncertain writes. Do not hide persistent defects behind a higher repaired-success rate.

Do not assume a `reasoning_steps` field helps, and do not assume it hurts. One study found that format restrictions degraded reasoning, more so as the constraints tightened (Tam et al.). Compare schema-with-reasoning-field, free-form-then-extract, and the provider's documented thinking controls on your task. Request a brief explanation, evidence span, or computed result when the consumer needs it.

## Step 5 — Add steering for a measured gap

Start with clear zero-shot instructions. Add representative examples when recurring label boundaries, tone, format, or abstention behavior remain wrong. Choose distinct cases, audit contradictions, and compare with zero-shot. Provider guidance differs (Claude documentation suggests 3–5 examples; OpenAI suggests trying zero-shot first for reasoning models), and few-shot accuracy has been shown to swing with example choice, order, and format, so there is no universal optimal example count.

For reasoning-tuned models, use documented effort controls and explicit success criteria. Do not add “think step by step” by habit. Request verifiable calculations, cited evidence, or tool results when helpful; visible reasoning is a limited diagnostic signal, not an audit log, because models often do not mention the influences on their answers. Compare a stronger model or more effort after establishing sufficient inputs. Asking a model to re-check its own reasoning without external feedback did not reliably help and sometimes hurt (Huang et al.); prefer tool, test, or retrieval checks.

For long documents, test selection and evidence placement. Claude guidance recommends long data before the final query and reports gains in its own tests; evaluate it on the workload rather than promising a universal lift. Refer context budgets to `advise-context` and retrieval design to `advise-rag`. The comparison of long context against retrieval is a measured quality/cost choice, not a fixed token threshold.

Repeated sampling can help when candidates can be verified or compared (self-consistency raised accuracy on several reasoning benchmarks). Majority selection returns the most common answer, so it cannot repair an error that every sample shares; evaluate the selector and its cost. Prompt optimizers such as GEPA require useful feedback and separate development, selection, and release cases; benchmark gains are not production guarantees.

Keep eligible stable prefixes reusable and check actual cache usage with `advise-caching`. Preserve the contract across providers while adapting documented syntax and supported settings.

## Step 6 — Compare, confirm, and ship

Use versioned real requests, known failures, and targeted synthetic stress cases. Keep development, selection, held-out release, and regression/challenge collections distinct. Compare incumbent and candidate on the same snapshot. Report representative traffic and stress results separately; a fixed category mixture does not estimate production prevalence.

Use deterministic checks for observable invariants and calibrated semantic judges where needed. Binary checks fit mandatory requirements; ratings or pairwise judgments can fit graded quality. Judge agreement on easy cases can hide failures on hard ones: on JudgeBench, strong judges scored only slightly above chance. Consult `advise-eval` for sample design, calibration, and release gates.

Change one component at a time. Report per-axis correctness, grounding, omissions, schema validity, action compliance, abstention/coverage, first-attempt and repaired success, latency, and cost. Keep hard constraints separate from weighted scores. A small diagnostic suite exposes patterns; its sampling error is large, so it cannot guarantee detection of regressions.

Distinguish `pass@1` (one attempt succeeds), `pass@k` (any of k succeeds), and `pass^k` (all k succeed on the same task). Do not cube aggregate success to estimate repeated reliability. Retain per-case results and measure the full workflow directly.

Confirm selected changes on held-out cases, then use gradual rollout and rollback criteria. Version the prompt, model settings, schema, tools, evidence/index, environment, and graders. Re-evaluate relevant component changes, because the behavior of the same hosted model can change over time. Monitor raw failures, refusals, truncations, retries, unsupported claims, invalid tool calls, and user outcomes.

Finish advice with a concrete recommendation: **observed failure → likely bottleneck → next probe → smallest intervention → comparison and release gate**. If no candidate improves the target requirement within the other constraints, retain the baseline and explain what evidence is still needed.

## References

- **Contract template and examples:** read [prompt-contracts.md](references/prompt-contracts.md) when writing the prompt itself.
- **Controlled probes and intervention choices:** read [failure-first.md](references/failure-first.md) for cross-component diagnosis and recovery.
- **Dataset separation, uncertainty, repeated reliability, and gates:** read [failure-first-measurement.md](references/failure-first-measurement.md) when comparing candidates; use `advise-eval` for full evaluation-system design.
- **Primary evidence and limits:** read [source-map.md](references/source-map.md) before citing research or applying provider-specific guidance.
