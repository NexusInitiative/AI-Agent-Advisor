# Adaptation Playbook

Keep a frozen test set split by entity or time to detect leakage. Compare prompt-only, retrieval/tool, and adaptation baselines. Use LoRA or other PEFT first for open models; use full tuning only with a justified quality target and operational capacity. Version the dataset, base model, adapter, prompt, and evaluator together.
