---
name: advise-fine-tune
description: |
  This skill should be used when the user asks to "should I fine-tune", "advise on fine-tuning",
  "when to fine-tune vs prompt engineer", "help with fine-tuning a model",
  "distillation vs fine-tuning", "should I use LoRA", "how much training data do I need",
  or needs guidance on model customization, training data, or adaptation trade-offs.
---

# Fine-Tuning Advisor

Do not recommend fine-tuning until a strong prompt, retrieval/tool design, and evaluation baseline exist. Fine-tuning changes behavior; it does not reliably add current knowledge, fix missing source access, or replace authorization and validation.

## Diagnose the gap

Fine-tune when a stable, repeated behavior is valuable and prompt-only performance remains inadequate: narrow classification, extraction, format consistency, domain style, tool-call policy, or distillation to a cheaper model. Prefer prompting, structured output, retrieval, or tools when the issue is changing facts, a small set of rules, missing context, or calculation accuracy.

Define a held-out target metric and an error taxonomy before collecting data. If you cannot label a correct answer consistently, you are not ready to train.

## Build the data first

Use high-quality examples that match production inputs and include the exact desired output. Deduplicate, remove contradictory labels, separate train/validation/test by entity or time where leakage is possible, and keep a protected holdout. Include failures, refusals, and edge cases deliberately. A small, clean dataset beats a large pile of weak synthetic outputs.

Document data provenance, licenses, sensitive fields, and the policy for harmful or private content. Do not train on raw production conversations without the appropriate privacy and legal review.

## Choose the least expensive adaptation

- Use supervised fine-tuning for repeatable input-to-output behavior.
- Use LoRA or another parameter-efficient method for most open-model adaptation; it reduces trainable parameters and experiment cost.
- Use quantized PEFT only when memory constraints justify the added complexity and quality is measured.
- Use distillation when a stronger teacher can generate or label a well-defined task and the deployed student passes the same held-out eval.
- Avoid full fine-tuning unless you control the model, have substantial data, and PEFT cannot meet the target.

Train small experiments first. Compare base, prompt-only, retrieval/tool baseline, and candidate adapters on the same holdout. Track task quality, critical regressions, calibration, latency, serving cost, and harmful behavior. Stop when validation no longer improves; inspect errors rather than increasing epochs blindly.

## Ship safely

Version the dataset, preprocessing, base model, hyperparameters, adapter, prompt, and evaluator. Canary the candidate, retain rollback, and monitor drift. Re-train only for a demonstrated distribution or requirement change.

For evaluation design see `advise-eval`; for model choices see `advise-models`.

## Sources

- [OpenAI fine-tuning guide](https://platform.openai.com/docs/guides/fine-tuning)
- [LoRA paper](https://arxiv.org/abs/2106.09685)
- [QLoRA paper](https://arxiv.org/abs/2305.14314)
