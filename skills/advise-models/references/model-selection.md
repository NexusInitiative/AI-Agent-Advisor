# Model Selection Reference

Use this file when running a model comparison, filling the requirements worksheet, or deciding whether routing is ready to ship.

## Requirements Worksheet

Fill this before touching a leaderboard; unanswered rows are assumptions to name in the recommendation.

| Question | Answer | Hard constraint? |
|---|---|---|
| Dominant task type(s) and traffic share | | |
| Unacceptable failures (list concretely) | | yes |
| p95 latency target / expected QPS | | |
| Budget per request / per month | | |
| Context length actually required (measured) | | |
| Modalities and languages | | |
| Data residency / privacy / compliance | | often yes |
| Tool use / structured output required | | |
| Fine-tuning or logit access needed | | |

## Comparison Protocol

1. Freeze the eval set, prompts, tools, retrieval, sampling parameters, and timeouts. Record any per-provider prompt adaptations explicitly.
2. Run every candidate on the full set; repeat nondeterministic tasks enough times to estimate run-to-run variance (one study measured accuracy varying by up to 15% across runs of settings meant to be deterministic) and use distributions (mean, variance, worst case). Compare candidates as paired differences with standard errors rather than bare averages.
3. Score each gate separately: critical task success, critical failure rate, p95 latency at realistic concurrency, measured cost, compliance pass, fallback drill.
4. Slice results by task category and input length — a model that wins short inputs and loses long ones needs a per-slice decision, which may itself become the routing seed.
5. Record: model IDs + exact versions, date, pricing snapshot, eval snapshot, and the decision rationale. Model comparisons rot in months; an undated comparison is unusable.

**Interpreting public benchmarks:** use HELM-style multi-metric benchmarks to build the shortlist and to sanity-check that your eval isn't wildly misranking; distrust single-number leaderboards, benchmarks older than the model generation, and any benchmark suspiciously close to a model's training cutoff (contamination). Your task eval outranks all of them.

## Routing Readiness Checklist

Ship a cheap-model route only when all are true:

- [ ] Single-model baseline measured, with per-category results
- [ ] Target subset identified where the cheap model matches the capable one on *your* eval (not "seems fine")
- [ ] Escalation trigger is observable and validated on held-out data: input features, schema-validation failure, or a trained evaluator or classifier. A model's own self-reflection can work (Self-Route used it to cut cost 39–65% at comparable quality), but validate any self-reported trigger against held-out outcomes before trusting it
- [ ] High-stakes categories are pinned to the capable model regardless of trigger
- [ ] Every routing decision logged with the trigger value for audit
- [ ] Misroute cost estimated and accepted by the product owner
- [ ] Re-validation scheduled on any provider version change

Cascade patterns (try cheap → validate → escalate on failure) suit tasks with cheap deterministic validation (schemas, unit tests, exact-match lookups). Predictive routing (classify first, route once) suits latency-sensitive traffic where a retry is too slow.

## Version Management

- Pin exact model versions in production; treat aliases as staging-only.
- Subscribe to provider changelogs; a version bump triggers the eval, not hope.
- Keep the runner-up warm: adapter in code, prompts retested on a schedule, auth alive.
- Sample production traffic into the eval on a regular schedule to catch drift the provider didn't announce; the same hosted service changed substantially within months in one study (Chen et al.), so set the cadence from how often your provider ships changes.
