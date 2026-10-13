# Triage and Localization

Read this when the symptom does not point at a component, when you are unsure the evaluation itself can be trusted, or when you need the statistics to tell a real change from noise. Sources are in [source-map.md](source-map.md). Items marked *(procedure)* are workflow steps grounded in the cited findings rather than findings themselves.

## Trace checklist

Capture these for every failing case so a substitution test is possible later *(procedure)*:

- The request exactly as sent, and the prompt as rendered after templates, system messages, and retrieved text are applied.
- The raw provider response, including stop or finish reason and any refusal flag, before parsing.
- Retrieval: candidate IDs with scores, the post-rerank list, the final context actually sent, and each chunk's document version and index build.
- Tools: each call, its arguments, the result, errors, retries, and elapsed time.
- State: model ID and version, adapter version, prompt version, cache status, memory entries read, and grader version.

Anthropic's guidance on agent evals is to read transcripts: a transcript tells you whether the agent made a genuine mistake or your grader rejected a valid solution. Without traces you can only guess which of seven RAG failure points or fourteen multi-agent failure modes you are looking at.

## How to run each substitution

| Test | How | Reads as |
|---|---|---|
| Gold evidence | Hand-pick the passages that answer the question and place them in the prompt | Fixes it: retrieval, ranking, or selection. Does not: generation, prompt, or a sufficiency or conflict problem |
| Closed-book | Ask with no retrieved text | A correct closed-book answer plus a wrong RAG answer means retrieved content is misleading the model; models have overridden correct priors with wrong context over 60% of the time (ClashEval) |
| Base versus tuned | Same prompt, same inputs, untuned and tuned | Isolates tuning from prompt and retrieval |
| Version bisect | Rerun the same inputs on the previous model, prompt, index, or adapter | Hosted-model behavior can change between versions (one study saw prime identification fall from 84% to 51%), so pin and compare |
| Train versus fresh | Score training-like inputs and newly written inputs | A gap points to overfitting or leakage (GSM1k found accuracy drops of up to 8% on a freshly written matched set) |
| Cache bypass | Disable semantic and prompt caches | A static similarity threshold gives no correctness guarantee (vCache) |
| Replay | Feed a saved good response to the parser | Separates adapter bugs from model output |
| Direct tool call | Execute the model's call without the model | Separates API, permission, and data problems from the model's choice |
| Repeat | Run identically several times, scoring raw text and parsed answer separately | Under settings meant to be deterministic, accuracy varied up to 15% across runs and no tested model was fully repeatable |

## Evaluation-system recipes

### E1. Evals say it's fine, users say it's bad

**Test.** Collect recent real failures and score them with your current grader and set.

**Causes and fixes, most likely first.**

1. *The set no longer represents traffic or has leaked.* Benchmark leakage can dramatically inflate results (Zhou et al.), and surveys document contamination as a general reliability problem (Xu et al.). Refresh from production, deduplicate against training data, and split by entity or time.
2. *The judge misses hard cases.* On JudgeBench, strong judges scored only slightly better than random on difficult response pairs; judges also show position, verbosity, and self-enhancement bias. Calibrate against expert labels on hard and plausible-wrong answers, swap answer order, and audit false passes by category.
3. *Criteria drifted.* In a user study, people needed criteria to grade outputs, but grading outputs changed their criteria. Re-review the rubric against fresh outputs.
4. *The retrieval metric is not the outcome.* Query-document relevance labels correlated weakly with downstream RAG performance (eRAG). Add an answer-level check.
5. *An average hides a slice.* Report by category and severity *(procedure)*.

**Verify.** The new failures now fail your eval, and the eval's pass rate on a fresh sample matches reviewed production quality.

### E2. Score dropped but outputs look fine (or the reverse)

**Test.** Read transcripts for the cases whose grades changed.

**Causes and fixes.**

1. *Grader or task bugs.* Anthropic describes a model whose CORE-Bench score was 42% until rigid grading (penalizing "96.12" where "96.124991…" was expected), ambiguous task specs, and irreproducible stochastic tasks were fixed, after which it scored 95%. Everything the grader checks should be clear from the task description.
2. *Infrastructure.* Resource limits changed an agentic coding benchmark by 6 percentage points (p < 0.01) between the most and least generous setups; Anthropic recommends treating resource configuration as a controlled variable and being skeptical of gaps under 3 points until configurations match.
3. *Noise.* Repeated runs differ (Atil et al.); evaluations are experiments, so use standard errors and paired comparisons (Miller).
4. *Judge order effects.* LLM-judged comparisons were highly sensitive to the order candidates were presented in (Han et al.).

**Verify.** The score change survives a rerun with matched configuration and a paired confidence interval that excludes zero.

### E3. The held-out set no longer predicts production

**Cause.** Standard inference assumes hypotheses are fixed before the data are seen; choosing prompts, models, or thresholds repeatedly on the same set violates that (Dwork et al.). Leakage and traffic drift add to it.

**Fix.** Keep development, selection, and release sets separate; refresh the release set from fresh traffic; compare baseline and candidate on the same snapshot *(procedure)*.

## Statistics for comparing changes

- **Pair the comparison.** Score baseline and candidate on identical cases and analyze per-case differences with standard errors (Miller), instead of comparing two bare rates.
- **Zero failures is not zero risk.** With zero failures in `n` independent, representative trials, the exact one-sided 95% upper bound on the failure probability solves `(1 − p)^n = 0.05`. This follows from the exact binomial definition documented by NIST and was checked numerically: about 5.8% at `n = 50` and about 0.997% at `n = 299`. It assumes independent, representative sampling, which curated stress cases and near-duplicate variants do not satisfy.
- **Measure consistency separately.** `pass@k` is the chance at least one of k attempts succeeds; `pass^k` is the chance all k succeed, averaged across tasks (τ-bench). In τ-bench, agents succeeded on under half the tasks and `pass^8` fell below 25% in retail. A system can look fine on `pass@1` and be unreliable for customers.
- **Do not multiply marginal rates.** A ten-step workflow at 95% per step succeeds `0.95^10 ≈ 59.9%` only if each step's 95% is conditional on earlier success. Measure the whole workflow *(derived)*.
