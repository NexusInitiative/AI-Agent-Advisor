# Adaptation Playbook

Use this file once fine-tuning is justified and you're choosing a method and running experiments.

## Method Selection Table

| Method | Choose when | Watch out for |
|---|---|---|
| Hosted SFT (provider API) | Closed model, behavior-shaping task, no infra appetite | Limited hyperparameters; data leaves your boundary — check provider data-use terms |
| LoRA | Open model, most adaptation tasks | Rank/alpha and target-module choices matter; sweep small (r=8–64) before assuming more is better |
| QLoRA | LoRA quality goals but GPU memory-bound | Quantization can shift quality; compare against plain LoRA on a subset when possible |
| Distillation | Cost/latency: replace big-model calls on a defined task | Student inherits teacher errors; cap synthetic share and human-review samples |
| Full fine-tune | You own the model, have large clean data, PEFT measurably insufficient | Catastrophic forgetting; highest rollback and regression risk |
| DPO/preference tuning | Systematic preference gaps after SFT (tone, helpfulness trade-offs) | Needs preference pairs; not a substitute for SFT on correctness tasks |

## Data Checklist

- [ ] Inputs sampled from production distribution (or best available proxy), including hard and adversarial cases
- [ ] Outputs are exactly the desired behavior — format, refusals, edge handling — not "close enough"
- [ ] Deduplicated (exact + near-duplicate) across and within splits
- [ ] Contradictory labels resolved; labeler agreement spot-checked
- [ ] Train/val/test split by entity or time wherever the same source could leak across splits
- [ ] Protected holdout that no one — human or hyperparameter search — optimizes against
- [ ] Synthetic examples tagged as synthetic, sampled for human review, and capped as a share of the set
- [ ] Provenance, licenses, PII handling documented; privacy/legal review for production-derived data

## Experiment Protocol

1. Fix the eval harness first (same holdout, same graders — see `advise-eval`).
2. Establish the four baselines: raw base model, best prompt-only, retrieval/tool-augmented, and (if distilling) teacher-with-prompt.
3. Train the smallest candidate (lowest rank, smallest data slice that could plausibly work). Scale data before scaling method complexity.
4. After each run record: data version, base model + revision, method + hyperparameters, seed, validation curve, holdout metrics, regression-set metrics.
5. Attribute wins honestly: if the tuned model beats the prompt baseline but not the retrieval baseline, the answer was retrieval, not weights.

## Overfitting and Forgetting Signals

- Validation loss improves while holdout task metric stalls → memorizing surface patterns; diversify data.
- Output diversity collapses (identical phrasing everywhere) → too many epochs or too-narrow data.
- Regression-set drops (safety refusals weaken, adjacent tasks degrade) → mix general instruction data back in, reduce epochs, or lower LR.
- Format perfect, content wrong → the task needed grounding, not tuning; pair the tuned model with retrieval.

## Versioning and Rollback

Version as one immutable tuple: `dataset@vN + preprocessing@vN + base-model@rev + hyperparams + adapter@vN + prompt@vN + evaluator@vN`. Store eval snapshots with the tuple. Serve adapters behind a flag so rollback is an adapter swap, not a redeploy. Schedule holdout re-runs in production monitoring to catch silent base-model or traffic drift.
