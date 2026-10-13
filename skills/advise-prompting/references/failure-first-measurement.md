# Measuring Failure-First Changes

Use this reference to compare prompting interventions. Refer full dataset, judge, and CI architecture to `advise-eval`.

## Keep the measurement decision explicit

Define the user outcome, permitted evidence/actions, failure behavior, and latency/spend budget. Grade outcomes and relevant action history separately. A tool agent's final message does not establish that its promised state change occurred; the final state alone may hide an unauthorized intermediate action. τ-bench grades by comparing the final database state with an annotated goal state, which is why it checks outcomes rather than the agent's description of them.

Maintain distinct collections:

| Collection | Purpose | Handling |
|---|---|---|
| Development | Reproduce errors and tune components | Inspect freely; optimizers may consume feedback |
| Selection/validation | Choose candidate configurations | Expect selection bias after repeated comparisons |
| Held-out release | Estimate unseen-case performance | Exclude from examples, training, optimizer feedback |
| Regression/challenge | Preserve bugs and test rare/adversarial failures | Version; report separately from traffic prevalence |

Add fresh cases through explicit snapshots. Compare baseline and candidate on the same snapshot and equal resource budgets. Correct wrong labels or stale requirements with an audit trail. A frozen set with incorrect ground truth is not useful protection.

Sample representative traffic according to product usage, and maintain additional stress coverage for permissions, injection, ambiguous inputs, missing/conflicting evidence, retries, and uncommon formats. Synthetic cases can fill gaps that production traces have not exposed. A fixed category mixture such as 40/30/20/10 is neither a required design nor a production-distribution estimate.

## Size for uncertainty, not a slogan

A few dozen curated cases can expose obvious defects, but neither “50 per category” nor “100–200 before deployment” is a statistical law. Required coverage depends on prevalence, effect size, dependence, and consequence. Miller's treatment of evaluations as experiments gives formulas for standard errors, paired differences between two models, and planning an evaluation; use them instead of a fixed count.

For zero failures in `n` independent representative Bernoulli trials, setting the observed failure count to zero in the exact binomial definition documented by NIST gives `(1 − p)^n = α` at the upper bound, so the one-sided 95% exact upper bound on failure probability is:

`p_upper = 1 − 0.05 ** (1 / n)`.

This is derived rather than quoted: at `n=50` it is 5.8%, and at `n=299` it is 0.997%, just below 1% (both checked numerically). These calculated examples illustrate uncertainty, not universal launch gates. Curated stress cases, correlated variants of one document, and repeated runs of one task do not satisfy representative independent sampling. Report counts and sampling assumptions with rates.

Use paired baseline/candidate results to see which cases changed. Confirm selected interventions on held-out cases. Repeatedly selecting on the release set turns it into another development surface: the theory of adaptive data analysis shows that standard estimates assume the hypotheses were fixed before the data were seen (Dwork et al.). Renew protected coverage when this occurs.

## Grade the smallest observable requirement

Use deterministic parsers, type checks, reference data, invariants, executable tests, and state checks where appropriate. Execution checks can still fail because of the environment and are not literally free.

Use binary grading for mandatory properties such as no unauthorized write or no unsupported price. Use calibrated ratings or pairwise judgments for graded quality. Keep hard constraints, correctness, grounding, omissions, communication quality, and operations separate; do not bury a severe regression in a composite improvement.

Pin the semantic judge's model/configuration, rubric, evidence, and examples. Calibrate against expert-labeled difficult failures and plausible wrong answers. Audit false passes and false fails by category and severity: aggregate agreement on easy pairs can conceal failure on hard ones, and on JudgeBench strong judges scored only slightly better than random guessing. Blind model identity and swap answer order in pairwise comparisons, because judges show position, verbosity, and self-enhancement biases and position bias varies with the judge and the quality gap between answers. A different-family judge is a hypothesis to test, not immunity from bias. Criteria also drift: users need criteria to grade outputs, but grading outputs changes their criteria, so re-review the rubric against fresh outputs (Shankar et al.).

## Distinguish repeated reliability

- `pass@1`: a single attempt succeeds.
- `pass@k`: at least one of k attempts succeeds. Operational value requires a selector that can find a useful answer.
- `pass^k`: all k attempts succeed on the same task, averaged across tasks (the definition used by τ-bench).

Under independent repeats conditional on a task with success probability `p_i`, its all-success probability is `p_i ** k`. Aggregate all-success is the mean of those powers, not the power of mean success. If 70% of tasks always succeed and 30% always fail, both `pass@1` and `pass^3` are 70%, not 34.3%. If every task instead has independent 70% success, `pass^3` is 34.3%. This arithmetic is derived from the τ-bench definition under stated within-task independence. Estimate from grouped task-level repeats and document state/reset behavior. Repeats matter in practice: τ-bench measured agents succeeding on under 50% of tasks with `pass^8` under 25% in the retail domain, and another study measured accuracy varying by up to 15% across repeated runs of settings expected to be deterministic.

Likewise, a ten-stage workflow succeeds with probability `0.95 ** 10 ≈ 59.9%` only if each required stage has 95% success conditional on prior success. Multiplying marginal stage rates is not generally justified. Measure workflow outcomes directly.

## Release and monitor the comparison

Record prompt/model settings, schema, tool registry, evidence/index snapshot, environment, grader versions, per-case outputs, costs, and latencies. Separate first-attempt success from repaired success, and include abstention/coverage so systems cannot improve apparent correctness by declining difficult cases.

Use fast deterministic/regression checks for routine changes and broader semantic, repeated, and adversarial coverage for relevant releases. Define hard invariant gates and statistical regression tolerances separately. A finite suite with zero failures cannot prove zero production risk.

Roll out gradually with explicit rollback criteria. Monitor parse failures, truncations, refusals, retry exhaustion, invalid/failed tool calls, citation support, no-progress loops, tail latency/cost, and actual user outcomes. Behavior of the same hosted model can change between versions (one study measured prime-number identification falling from 84% to 51% between two releases of the same service), so keep the regression set running after launch. Turn new failures into labeled versioned cases. If an intervention improves its local metric but harms end-to-end outcomes, reject or revise it.
