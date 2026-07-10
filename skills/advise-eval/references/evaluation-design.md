# Evaluation design reference

## Minimal example record

```json
{
  "id": "support-refund-017",
  "input": {"user_message": "Can I receive a refund after 45 days?"},
  "reference": {
    "required_facts": ["standard refund period is 30 days"],
    "forbidden_claims": ["refunds are always available within 60 days"],
    "acceptable_answers": ["No, unless a documented exception applies."]
  },
  "metadata": {"category": "policy_qa", "risk": "high", "source": "production_failure"}
}
```

Keep references private from the application under test. Include metadata for risk, difficulty, source, tenant/domain, and failure category so results can be sliced instead of averaged away.

## Metric selection

| System | Start with | Add when needed |
|---|---|---|
| Classifier | exact label match, confusion matrix | calibration, per-class recall |
| Structured output | parse/schema validity | business-rule checks, refusal behavior |
| RAG | annotated retrieval recall/precision, claim support | rank metrics, citation checks, sufficiency |
| Tool agent | tool/argument checks, execution success | trajectory efficiency, recovery, approval compliance |
| Chat or writing | rubric dimensions + human sample | pairwise comparisons, user feedback |

## Suggested repository layout

```text
evals/
  datasets/{development,holdout,adversarial,production_regressions}.jsonl
  graders/{deterministic,groundedness,completeness,tool_calls,safety}.py
  rubrics/{groundedness,task_success,trajectory}.md
  runners/{run_eval,compare_runs}.py
  calibration/{human_labels,judge_analysis}.jsonl
  results/
```

The layout is a starting convention, not a requirement. The important properties are versioning, reproducibility, trace retention, and diagnosable failures.
