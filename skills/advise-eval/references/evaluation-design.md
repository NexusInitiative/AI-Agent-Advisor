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

## CI Wiring Example

A minimal GitHub Actions gate that runs the smoke suite on every PR:

```yaml
eval-smoke:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - run: python evals/runners/run_eval.py \
        --dataset evals/datasets/development.jsonl \
        --tags smoke --output results/pr.json
    - run: python evals/runners/compare_runs.py \
        results/baseline.json results/pr.json \
        --gates evals/gates.yaml
```

Two properties matter more than the specific tooling: the baseline result file is pinned per main-branch commit (so comparisons are apples-to-apples), and the gates file is versioned next to the datasets so a gate change is a reviewable diff, never a dashboard edit.

## Slicing Results

Report every run sliced by the metadata fields in the example record — category, risk, difficulty, and source. An aggregate pass rate of 94% is uninterpretable; "policy_qa: 99%, refunds/high-risk: 71%" is a work order. Store per-case outputs with grader evidence so any regression can be diagnosed from the artifact without re-running.
