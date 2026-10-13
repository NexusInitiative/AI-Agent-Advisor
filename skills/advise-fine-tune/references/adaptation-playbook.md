# Adaptation Playbook

Use this file once fine-tuning is justified and you're choosing a method and running experiments.

## Method Selection Table

| Method | Choose when | Watch out for |
|---|---|---|
| Hosted SFT (provider API) | Closed model, behavior-shaping task, no infra appetite | Limited hyperparameters; data leaves your boundary — check provider data-use terms |
| LoRA | Open model, most adaptation tasks | Rank and target-module choices matter, so sweep them instead of assuming more is better; full fine-tuning learned perturbations with ranks 10–100× higher than typical LoRA configurations, which may explain its edge on code and math (Biderman et al.) |
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

Each signal below is paired with the evidence behind it; `advise-debug` recipes T1–T6 give the discriminating tests.

- Validation loss turns upward while training loss keeps falling → the classical overfitting signal (Goodfellow et al., *Deep Learning*, section 7.8). In LLM tuning it is a signal, not an oracle: InstructGPT's SFT models overfit on validation loss after one epoch yet more epochs improved human preference, and LIMA found perplexity did not correlate with generation quality. Decide with a held-out task or preference metric.
- Holdout task metric stalls or a freshly written matched set scores lower than the validation set → leakage or memorization (GSM1k found drops of up to 8%); deduplicate within and across splits (Lee et al.) and split by entity or time.
- Hallucination rises after tuning → examples with facts the model did not know are fit late and raise hallucination roughly linearly (Gekhman et al.); filter them, stop early, and move facts to retrieval.
- Output diversity collapses → preference optimization reduced diversity relative to SFT (Kirk et al.); LoRA kept generations more diverse than full fine-tuning (Biderman et al.).
- Regression-set drops (safety refusals weaken, adjacent tasks degrade) → forgetting occurs in 1B–7B models and with LoRA, and is not removed by early stopping (Luo et al.; Kalajdzievski); mix general instruction data back in, and gate on the regression suite.
- Format perfect, content wrong → the task needed grounding, not tuning; pair the tuned model with retrieval.

## Versioning and Rollback

Version as one immutable tuple: `dataset@vN + preprocessing@vN + base-model@rev + hyperparams + adapter@vN + prompt@vN + evaluator@vN`. Store eval snapshots with the tuple. Serve adapters behind a flag so rollback is an adapter swap, not a redeploy. Schedule holdout re-runs in production monitoring to catch silent base-model or traffic drift.
