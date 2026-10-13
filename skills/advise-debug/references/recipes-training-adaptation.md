# Recipes: Training and Adaptation (T1–T6)

Same template as the other recipe files. Sources are in [source-map.md](source-map.md); method and data choices live in `advise-fine-tune`. Items marked *(procedure)* are workflow steps rather than findings. Before debugging a tuned model at all, confirm it beat the cheap baselines: a prompt-only baseline and a retrieval baseline on the same holdout (for knowledge injection, retrieval outperformed unsupervised fine-tuning in Ovadia et al. and, for less popular facts, by a large margin in Soudani et al.).

## T1. Great in training or validation, worse in production or on a fresh holdout

**Test.** Score the tuned model on a freshly written holdout that matches the validation set, check overlap between training and evaluation data, and compare against the prompt-only baseline on the same holdout. A matched fresh set exposed accuracy drops of up to 8% for several model families on grade-school math (GSM1k), and the size of the gap correlated with how likely a model was to generate the original benchmark's examples (Spearman r² = 0.36), which the authors read as partial memorization; many frontier models showed minimal signs of overfitting.

**Causes and fixes, most likely first.**

1. *Leakage and near-duplicates.* Benchmark leakage can dramatically boost evaluation results (Zhou et al.). Deduplicating training data made models emit memorized text ten times less often, and train-test overlap affected over 4% of validation sets in standard datasets (Lee et al.). Deduplicate within and across splits and split by entity or time *(procedure)*.
2. *Training too long on duplicated or easy-to-memorize data.* Memorization grows with model capacity, the number of times an example is duplicated, and context length (Carlini et al.), and varies by fine-tuning task (Zeng et al.). Check for verbatim regurgitation of training examples.
3. *Fitting facts the model did not already know.* Examples with new knowledge were learned more slowly, emerged as overfitting late in training, and increased hallucination roughly linearly once learned (Gekhman et al., EMNLP 2024). Early stopping lowered that risk, and filtering out unknown examples reduced overfitting without costing performance. Keep examples at the edge of what the model knows, since a model tuned only on its best-known facts did not do best.
4. *Unrepresentative inputs.* Sample training inputs from the production distribution *(procedure)*. Fine-tuning can also distort pretrained features and do worse out of distribution than a gentler transfer in vision experiments (Kumar et al.), which is a reason to hold out distribution-shifted cases.

**Choose checkpoints by the task metric, not loss alone.** The classical signal is a validation loss that turns upward while training loss keeps falling (Goodfellow et al., *Deep Learning*, section 7.8). For LLM fine-tuning that signal is not an oracle: InstructGPT's SFT models overfit on validation loss after one epoch, yet more epochs improved human preference ratings, and LIMA found perplexity did not correlate with generation quality and selected checkpoints using a held-out development set. Track a task or preference metric alongside loss.

**Verify.** Paired comparison on a fresh holdout with standard errors, and a regression slice.

**Do not** tune hyperparameters on the final test set; adaptive reuse of one set breaks standard inference (Dwork et al.).

## T2. The tuned model got worse at other things

**Test.** Run a regression set of non-target tasks (general instruction following, refusals, adjacent tasks) on the base and tuned models.

**Causes and fixes.**

1. *Catastrophic forgetting.* It was generally observed in 1B–7B models during continual instruction tuning, with severity increasing with scale in that range, and general instruction tuning helped alleviate it in later fine-tuning (Luo et al.). Learning several skills sequentially risks forgetting; mixing data and a dual-stage mixed strategy helped (Dong et al., ACL 2024).
2. *LoRA is not forgetting-proof.* Forgetting scaled with fine-tuning performance, trainable parameters, and update steps, and could not be avoided by early stopping or fewer parameters (Kalajdzievski). But LoRA learned less and forgot less than full fine-tuning and kept generations more diverse; it substantially underperformed full fine-tuning on programming and math in standard low-rank settings (Biderman et al., TMLR 2024). Choose according to whether target performance or retention matters more.

**Fix.** Mix general instruction data into the tuning set, keep a regression suite as a release gate, and keep adapters swappable so rollback is cheap *(procedure)*.

**Verify.** Regression-set deltas, base versus tuned.

## T3. Fluent output, but the tuned model invents facts

**Test.** Split evaluation questions into facts the base model already answers and facts it does not, and compare closed-book accuracy before and after tuning (the known/unknown split in Gekhman et al.).

**Causes and fixes.** Fine-tuning mostly teaches a model to expose knowledge it already has; new-fact examples were learned slowly and raised hallucination once fit (Gekhman et al.). Unsupervised fine-tuning struggled to add new facts, and retrieval consistently outperformed it (Ovadia et al.), including by a large margin for the least popular facts (Soudani et al.). Move facts to retrieval, filter unknown-fact examples, stop early, and if you want the model to use retrieved documents, train with distractor documents as in RAFT.

**Verify.** Closed-book accuracy on known and unknown facts, plus an end-to-end comparison with a retrieval baseline.

## T4. Safety or refusal behavior weakened after tuning

**Test.** Run a safety and refusal evaluation before and after, including prompts unrelated to your task domain.

**Causes.**

1. *Even benign data can erode safety.* Fine-tuning GPT-3.5 Turbo and Llama-2 on utility datasets degraded safety alignment, "though to a lesser extent" than adversarial data (Qi et al.), who suggest forgetting of the initial alignment or tension between helpfulness and harmlessness. Ten adversarial examples at under $0.20 jailbroke GPT-3.5 Turbo.
2. *Narrow data, broad effect.* Fine-tuning on insecure-code outputs produced broadly misaligned behavior on unrelated prompts in several models, strongest in GPT-4o and Qwen2.5-Coder-32B-Instruct; the same examples framed as a computer-security class did not (Betley et al.). The effect was inconsistent across samples.
3. *Guardrails are forgotten like other behavior* (Kalajdzievski examined effects on Llama 2 chat's safety guardrails).

**Fix.** Audit tuning data for harmful or insecure content; Qi et al. discuss fine-tuning-data moderation, mixing in safety examples, and post-fine-tuning red-team auditing, and note that backdoored data can evade auditing. Treat the safety evaluation as a release gate.

**Verify.** Safety-evaluation deltas, including unrelated domains.

## T5. Repetitive outputs, lost diversity, or agrees with everything

**Test.** Compare output diversity on identical prompts between base and tuned models, and test with prompts that assert a wrong premise.

**Causes and fixes.**

1. *Preference optimization trades diversity for generalization.* RLHF improved out-of-distribution generalization over SFT but significantly reduced output diversity (Kirk et al.). Use SFT where varied outputs matter.
2. *Sycophancy.* Five assistants consistently showed sycophancy, and both humans and preference models sometimes preferred convincingly written sycophantic responses over correct ones (Sharma et al.). Include wrong-premise cases in evaluation.
3. *Over-optimizing a proxy reward.* Optimizing a reward model too far hurt gold-standard performance (Gao et al.). Track a held-out human or gold metric and stop where it peaks *(procedure)*.

**Verify.** Diversity and truthfulness-under-pressure metrics before and after.

## T6. Works in the notebook, fails when served

**Test.** Render the exact prompt token sequence used in training and in serving and diff them: chat template, special tokens, system prompt, beginning and end tokens.

**Causes and fixes.** With the wrong control tokens, models would have drastically worse performance, and the same base model fine-tuned by different teams can use different formats (Hugging Face chat-template documentation). Chat templates already include the special tokens, so adding extra ones is often incorrect or duplicated and hurts performance; set `add_special_tokens=False` when tokenizing a templated string. Apply the model's own template in both data preparation and inference, with the generation prompt added only at inference.

**Verify.** Identical token sequences for the same conversation in both paths, and evaluation parity.
