---
name: advise-eval
description: |
  This skill should be used when the user asks to "design an eval framework", "how should I test my AI agent",
  "set up LLM evaluations", "build a regression suite for my prompt", "which metrics should I use for my RAG or agent",
  "is LLM-as-a-judge reliable", "calibrate an LLM judge", "add evals to CI", "evaluate tool use or agent trajectories",
  or needs guidance on datasets, graders, human review, offline/online evaluation, safety evaluation, or production
  feedback loops for an LLM application, workflow, RAG system, or multi-agent system.
---

# Evaluation Advisor

Build evaluations as a versioned measurement system, not as a benchmark score or a single LLM judge. The default design is:

> deterministic checks for validity → reference or execution checks for correctness → calibrated LLM judges for nuanced quality → human review for calibration and high-risk decisions → production monitoring to find new cases.

## 1. Diagnose the decision before choosing a metric

Ask or infer:

- What user or business outcome must improve?
- What can never happen (unsafe action, data leak, fabricated claim, invalid tool call)?
- Is the system a single model, workflow, RAG pipeline, agent, or multi-agent system?
- Which artifacts are available: reference answers, labels, source documents, tool traces, or only production traces?
- What are the latency, cost, privacy, and review constraints?

Turn the answers into a success-criteria table with one row per behavior:

| Behavior | Failure modes | Grader | Threshold | Severity |
|---|---|---|---|---|
| Answer from retrieved policy | unsupported claim, omission | claim check + human audit | zero critical hallucinations | critical |
| Refund agent | wrong tool, bad arguments, unauthorized action | schema/execution checks | 100% approval gate compliance | critical |
| Support response | irrelevant or unclear answer | rubric judge + sampled human labels | agreed quality threshold | normal |

Keep dimensions separate: hard validity, task correctness, quality, safety, and operations. Do not hide a critical safety failure inside a weighted average.

## 2. Establish the smallest useful baseline

Start with the simplest test system that can falsify the current design:

1. Create a manually curated development set covering common cases, edge cases, ambiguous inputs, known failures, adversarial inputs, and safety cases.
2. Keep a protected holdout set. Do not tune prompts or rubrics against it.
3. Run the current application and record outputs, traces, grader versions, model parameters, latency, tokens, cost, retries, and errors.
4. Add deterministic checks before any LLM-based grading.
5. Review failures, classify them, and add representative regressions.

There is no universal required dataset size. A useful first pass is roughly 50–100 cases, but coverage and risk matter more than the count. Seed from expert-authored cases, historical traces, user feedback, previous bugs, and human-reviewed synthetic variations. Do not let synthetic data replace production-distribution coverage.

Treat this tuple as the reproducibility key:

```text
dataset version + application version + model/configuration version
+ prompt version + evaluator/judge version + execution configuration
```

## 3. Match the grader to the property

Use the cheapest reliable grader that can answer the question.

### Code and execution graders

Use code for JSON/schema validity, required and forbidden fields, exact labels, tool names and argument schemas, authorization rules, URL checks, compilation, unit tests, SQL execution, numerical answers, latency, token, cost, retry, and step-count limits. Never ask an LLM whether JSON parsed or whether a tool name matches.

For agent systems, grade the trace as well as the final answer:

- selected the allowed tool;
- supplied valid and minimally sufficient arguments;
- interpreted the result correctly;
- requested approval before restricted actions;
- recovered from tool errors;
- avoided unnecessary loops and data access;
- completed the task.

### Reference-based graders

Use expected labels, required facts, forbidden claims, executable tests, annotated relevant documents, citation verification, or a solver when an external correctness check exists. Prefer these over stylistic similarity. A reference answer is not always the only acceptable answer; encode invariants and acceptable alternatives where appropriate.

### LLM rubric graders

Use an LLM judge only for semantic or subjective properties that code cannot reliably assess: completeness, nuanced policy compliance, groundedness, relevance, tone, or trajectory quality. Use one criterion per judge where practical. Require structured output containing a score/label, evidence, and failure category. Give the judge only the context needed for that criterion and explicitly say what not to judge.

Use pairwise comparison when the decision is “is B better than A?” Randomize A/B order, hide model/provider identity, and report both absolute scores and pairwise preference. Do not treat a judge's explanation as proof; it is evidence to inspect.

## 4. Calibrate and audit the judge

An LLM judge is a noisy measurement instrument. Before gating releases on it:

1. Create a human-labeled calibration sample containing clear passes, clear failures, borderline cases, different response lengths and styles, and outputs from multiple model families.
2. Compare judge labels with human consensus using the metric appropriate to the task: accuracy, precision/recall, confusion matrix, Cohen’s kappa for categories, or rank correlation for ordinal scores.
3. Optimize for the asymmetric risk that matters. For safety and critical correctness, track false-pass rate separately; a judge that approves dangerous failures is not acceptable.
4. Recalibrate whenever the judge model, judge prompt, rubric, dataset distribution, or output format changes.
5. Route disagreement and ambiguous cases to humans instead of forcing an automated decision.

Mitigate known bias by randomizing pairwise order, normalizing irrelevant formatting, requiring claim-level evidence, separating criteria, and using an independent judge family when feasible. Test the judge on adversarially persuasive but incorrect outputs and on concise correct outputs. Do not assume a stronger judge is automatically reliable: judge benchmarks show that difficult factual, reasoning, mathematical, and coding comparisons can defeat strong models.

## 5. Evaluate each layer and the whole system

Use the layer that owns the failure:

- **RAG retrieval:** relevant-document recall, precision, rank quality, context sufficiency, noise sensitivity.
- **RAG generation:** factual correctness, claim-level groundedness/faithfulness, completeness, answer relevance, citation validity.
- **Tools:** tool-call accuracy/F1, argument validity, execution success, permission and approval compliance.
- **Agent trajectory:** goal completion, recovery, unnecessary steps, state consistency, data-access minimization, unsafe action rate.
- **End-to-end:** user-task success, safety, latency, cost, and reliability.

Do not diagnose a generation problem with only an end-to-end score. Save the input, expected criteria, output, retrieved context, tool calls/results, prompt/model versions, grader evidence, and operational data for every failed case.

Use a compact failure taxonomy such as `retrieval/no_context`, `retrieval/rank`, `generation/unsupported_claim`, `generation/omission`, `tool/wrong_tool`, `tool/invalid_args`, `agent/unnecessary_loop`, `safety/injection_followed`, and `format/schema_invalid`.

## 6. Account for nondeterminism and compare versions correctly

Run important cases multiple times and report distribution, not just one score: mean, variance or confidence interval, pass consistency, worst-case critical failures, latency p95, and cost. Record sampling and execution settings.

For a candidate change, compare against the same dataset and configuration. Report:

```text
absolute: task-success rate and criterion scores
relative: pairwise preference or win/loss/tie
operational: p95 latency, cost, retries, and failure rate
```

Use category-level deltas and practical/statistical significance where possible. A tiny aggregate score change should not block a release unless it represents a critical-case regression or a meaningful operational breach.

## 7. Build a tiered release and production loop

Start with:

- **Pull request smoke suite:** 20–50 high-value cases, deterministic checks, cheap judges, and hard safety/schema gates.
- **Nightly/release regression:** broader development and adversarial sets, repeated runs, calibrated judges, and holdout comparison.
- **Production monitoring:** sampled traces, safety and policy checks, latency/cost alerts, user feedback, and human review queues.

Promote production failures, novel edge cases, and reviewed synthetic cases into the development set. Preserve holdout integrity. Version datasets and evaluators like code.

Example gate policy:

```yaml
quality_gates:
  schema_validity: {minimum: 1.0}
  critical_task_success: {minimum: 0.95}
  critical_safety_failures: {maximum_count: 0}
  groundedness: {minimum: 0.90, allowed_regression: 0.01}
  p95_latency_ms: {maximum: 3000}
```

Prefer explicit gates over one composite score. If the user asks for a tool-specific implementation, recommend the closest existing reference below, but keep the metric design independent of the vendor.

## References

- For detailed judge rubrics, calibration design, and bias tests, read [llm-judge.md](references/llm-judge.md).
- For dataset schemas, agent/RAG metric mapping, and CI examples, read [evaluation-design.md](references/evaluation-design.md).
- For the verified source map and caveats, read [source-map.md](references/source-map.md).
- For RAG-specific retrieval and generation advice, defer to `advise-rag`.
- For model selection, defer to `advise-models`; for prompt regression mechanics, defer to `advise-prompting`.
