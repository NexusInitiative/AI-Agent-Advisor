# Multi-agent judges and production-readiness for drift monitoring

This reference extends the judge guidance in `llm-judge.md`. Read that first. The numeric thresholds here are illustrative starting points, not universal requirements — set every one from the decision's risk, the cost of a false pass, and the variance you measure on your own data, exactly as the rest of this skill insists.

## When more than one judge is worth the cost

A single well-calibrated judge is the default. It is cheaper, faster to update, and easier to reason about. Add judges only when you have evidence the added cost buys risk reduction:

- **Asymmetric, expensive failure.** Safety, authorization, financial, or data-loss decisions where the cost of an approved failure dwarfs the cost of extra grading.
- **Uncorrelated blind spots.** One model family systematically mis-scores a category (hard math, a domain dialect, its own outputs). A second judge from a different family catches what the first cannot.
- **Decomposable judgment.** A verdict depends on several independent properties (safety, correctness, groundedness, tone) whose evidence differs, so one judge per property is more reliable than one judge weighing all of them.
- **High-volume monitoring.** Continuous production grading where a single judge's silent drift approves many errors before anyone notices.

If a single judge already meets your false-pass target on held-out human labels, more judges add latency and spend without comparable benefit. Prove the single judge is insufficient before reaching for an ensemble.

## Patterns

### Ensemble consensus

Independent judges vote on the same criterion; aggregate at the decision level (majority, supermajority, or unanimous by risk), never by averaging scores.

- Calibrate each judge separately against the same human-adjudicated set, and track each one's false-pass and false-fail rate on its own.
- Choose judges whose errors are *uncorrelated* — different model families, or a model judge paired with a deterministic verifier. Three judges from the same family that share a bias give false confidence, not redundancy.
- Route disagreement and low-confidence agreement to human review rather than forcing a machine decision.

```json
{
  "criterion": "safety_violation",
  "judges": [
    {"id": "claude_v2", "pass": false, "confidence": 0.92},
    {"id": "llama_v3",  "pass": false, "confidence": 0.78},
    {"id": "rule_check","pass": true,  "confidence": 0.55}
  ],
  "consensus": "fail",
  "agreement": "2/3",
  "route": "human_audit"
}
```

Cost scales with judge count. Consensus also slows change: updating one judge without the others makes the ensemble inconsistent. Persistent disagreement on a category usually means the rubric is ambiguous — fix the rubric, do not paper over it with a vote.

### Hierarchical routing

Cases flow through tiers of increasing cost: deterministic checks → cheap model → capable model → human. Each tier decides the cases it can and escalates the rest. This extends the grader-ordering principle from `SKILL.md` §3 (cheapest reliable grader first) and the cost-placement guidance in `llm-judge.md`, adding a capability cascade within the judge tier itself. It is the workhorse pattern for production cost control.

```yaml
routing:
  - tier: deterministic         # schema, tool-arg, execution checks
    decide_if: all_pass
    escalate_if: any_fail
  - tier: fast_model
    decide_if: score >= 8 or score <= 3
    escalate_if: 4 <= score <= 7 or confidence < 0.7
  - tier: capable_model
    decide_if: confidence >= 0.7
    escalate_if: confidence < 0.7
  - tier: human
    decide: always
```

Calibrate each tier on cases representative of *that tier's* difficulty, and log which tier decided each case. The failure mode to watch is a cheap tier that systematically misroutes, starving or flooding the expensive tier with skewed input.

### Specialized decomposition

Different judges own different dimensions; results combine only through explicit fusion logic that mirrors business rules, never a weighted average that can hide a critical failure inside a high mean.

```json
{
  "dimensions": {
    "safety":       {"judge": "safety_clf_v2",   "verdict": "safe"},
    "correctness":  {"judge": "sql_reference",    "verdict": "correct"},
    "completeness": {"judge": "completeness_v3",  "verdict": "incomplete"},
    "relevance":    {"judge": "embedding_check",  "verdict": "relevant"}
  },
  "fusion": "safety AND correctness AND completeness AND relevance",
  "overall": "fail",
  "failed_on": ["completeness"]
}
```

Keep the per-dimension verdicts and evidence separate so a failure routes to the right fix. Fusion rules are brittle: when business requirements change, cached results may need re-evaluation. Watch for correlated failures across dimensions that a per-dimension view alone will miss.

### Debate and critique

One model produces or defends an answer; a second critiques it; a third (or a deterministic rule) adjudicates. Useful for subjective or contested judgments where surfacing the strongest counter-argument improves the decision. This pattern is not covered by this skill's cited judge-reliability sources (see `references/source-map.md`); treat it as an engineering option to validate on your own calibration set, not an evidence-backed default.

Treat the debate transcript as evidence to inspect, not proof — a persuasive critic can be confidently wrong, which is itself one of the biases below. Debate adds several model calls per case; reserve it for high-stakes, genuinely contestable criteria, not routine grading.

## Bias detection

The single-judge biases in `llm-judge.md` do not disappear in an ensemble — a shared bias across judges of the same lineage compounds instead of canceling. Detect them explicitly.

| Bias | How it shows up | How to detect it |
|---|---|---|
| Position | Prefers the first or last option in pairwise | Swap A/B order and re-run; a preference that flips with position is not trustworthy |
| Verbosity | Rewards length independent of correctness | Score a correct answer terse vs. padded; compare equal-length answers of unequal quality |
| Self-preference | Favors outputs from its own model family or style | Compare false-pass rate on in-family vs. out-of-family outputs |
| Persuasion / sycophancy | Swayed by confident, well-argued but wrong answers | Include incorrect-but-persuasive and correct-but-terse cases; track false pass on them |
| Recency / context position (distinct from pairwise position bias above; not covered by this skill's cited sources) | Over-weights facts seen last in a long context passed to the judge | Shuffle fact order in context and re-evaluate |
| Domain miscalibration | Under-performs on hard math, code, or specialist facts | Benchmark the judge against experts per domain; slice failures by domain |
| Confidence miscalibration | Stated confidence doesn't track accuracy | Compare confidence buckets to empirical accuracy on the calibration set |

**Audit protocol.** Build a small adversarial probe set covering the corners: correct-terse, correct-verbose, incorrect-terse, incorrect-persuasive, correct answers from several model families, and outputs from models inside and outside the judge's lineage. Run every judge over it and report per-judge results rather than a pooled number. The table below is a hypothetical illustration of the report shape — substitute your own judges and measured results, not real model names or invented scores:

```text
                correct-terse   correct-verbose   incorrect-terse   incorrect-persuasive
judge_a (fast)  PASS            PASS              FAIL              PASS  <- flips on persuasive-wrong: persuasion bias
judge_b (capable) PASS          PASS              FAIL              FAIL
judge_c (fast)  FAIL            PASS              FAIL              FAIL  <- fails a correct-terse case: possibly under-calibrated
```

A judge whose verdict flips on order swaps, or whose false-pass rate jumps on the persuasive-wrong column, is not ready to gate. Cross-judge *agreement* is its own signal: if judges agreed on calibration cases but diverge on new production traffic, suspect distribution shift or rubric ambiguity, not a broken judge.

**Mitigations** (in addition to those in `SKILL.md` §4): randomize and order-swap every pairwise comparison; normalize length/formatting before judging when it isn't part of the criterion; keep one criterion per judge; include an independent-family judge; require claim-level evidence and inspect it even when the score looks right; deploy in audit mode over sensitive cases before letting any judge gate.

## What makes a judge production-ready for drift monitoring

A judge used to watch a live system for drift is itself a component that can drift. "Production-ready" is not a single accuracy number — it is a set of properties you can point to. Treat the following as a checklist; the specific numbers are examples to replace with risk-derived targets.

**1. Calibrated on production-shaped data.** Verdicts compared against human-adjudicated labels drawn from the real input distribution, not just dev examples. Report false-pass rate, false-fail rate, and agreement *separately* and *sliced by risk category* — never a single averaged score. A judge is not ready to gate if its false-pass rate on critical cases exceeds what the decision can tolerate (for many safety gates that tolerance is near zero).

**2. Bias-tested and documented.** The adversarial probe set above has been run, and the judge ships with a written record of which biases affect it and how they are contained. Position-swap stability and behavior on persuasive-wrong / correct-terse cases are explicitly measured, not assumed.

**3. Reproducible and versioned.** Every verdict carries the tuple from `SKILL.md` §2 extended to the judge: `judge model + judge prompt + rubric version + calibration-set version`. Any historical case can be re-graded with any prior judge version and yield the same verdict (cache keyed by case ID + output hash + judge version, per `llm-judge.md`). Judge changes ship with a re-calibration delta, not silently.

**4. Evidence-producing.** Structured output — verdict, confidence, supported/unsupported claims, and a failure category that maps to an action (`hallucination`, `bad_retrieval`, `ambiguous_rubric`, …). A verdict you cannot explain is one you cannot debug in production.

**5. Aware of its own uncertainty.** Confidence should fall on out-of-distribution inputs and automatically trigger human escalation, rather than staying high and then failing abruptly. The single most dangerous property in a monitoring judge is confident wrongness on cases it has never seen.

**6. Continuously monitored.** The monitor needs a monitor. Sample a fraction of the cases the judge auto-approved, have humans label them, and track false-pass rate *over time*. Watch the judge's confidence distribution, escalation rate, and (for ensembles) inter-judge agreement. Alert when false-pass rate rises materially above the calibration baseline, when agreement drops, or when escalation rate swings — any of these can be the first sign of either model drift or judge drift, and you need to tell the two apart.

**7. Rollback-ready.** Judge config is deployed like code: canary on a slice of traffic, watched, and reversible. A regressing judge can be rolled back to a prior version without losing the production trace record.

### Separating system drift from judge drift

The whole point of a monitoring judge is to detect drift in the system under test — but a shift in the judge's own scores can come from either source. Disambiguate with a **fixed anchor set**: a small, frozen set of cases with known human labels that you re-grade on a schedule. If judge scores move on the anchor set, the *judge* drifted (model update, silent provider change) — recalibrate or roll back. If anchor-set scores hold steady but production scores move, the *system* drifted — which is exactly the signal you deployed the judge to catch. Without an anchor set you cannot tell a real regression from a judge that quietly changed underneath you.

## Recommended rollout

- **Single-judge, normal risk.** Calibrate on production-shaped cases; document biases; deploy to a traffic slice in audit mode; sample human labels weekly on auto-approved cases; alert on false-pass rising above baseline; recalibrate after any model/prompt change and on a schedule.
- **High-stakes (safety, auth, financial).** Ensemble of 2–3 uncorrelated judges or judge-plus-verifier; calibrate each independently; route disagreement and low confidence to humans; run in audit mode (grade but don't gate) until a clean window of human-labeled data confirms impact, then enable gating with human escalation retained.
- **Continuous drift monitoring.** Maintain the frozen anchor set and re-grade it on a schedule; dashboard false-pass (sampled), agreement, escalation rate, and confidence distribution; set a data-quality SLO that halts auto-gating when false-pass or escalation breaches it; archive every verdict with its evidence for retrospective diagnosis.

## Sources

- [Judging LLM-as-a-Judge (MT-Bench / Chatbot Arena)](https://arxiv.org/abs/2306.05685): judge–human correlation alongside position, verbosity, and self-enhancement biases.
- [A Survey on LLM-as-a-Judge](https://arxiv.org/abs/2411.15594): taxonomy of judge designs, ensemble/multi-agent approaches, and reliability/bias findings. A survey, not a guarantee for any specific domain.
- [JudgeBench](https://arxiv.org/abs/2410.12784): stress-tests judges on hard knowledge, reasoning, math, and coding comparisons — evidence for testing the judge itself rather than assuming reliability.
- [Systematic study of position bias in pairwise LLM evaluation](https://arxiv.org/abs/2406.07791): basis for order randomization and order-swapped checks.

The numeric thresholds in this document are practical starting points, not statistically universal requirements. Set them from risk, variance, domain coverage, and the acceptable error rate of the decision the judge gates.
