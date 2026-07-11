# Source Map

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Fine-tuning needs task-matched training data and a held-out evaluation; hundreds to a few thousand strong examples is a realistic starting range. | [S-001](https://platform.openai.com/docs/guides/fine-tuning) | High | Applies to the documented service; exact data guidance is provider- and task-specific. |
| Low-rank adaptation can match full fine-tuning quality on many tasks at a fraction of trainable parameters. | [S-002](https://arxiv.org/abs/2106.09685) (LoRA) | High | Results are task-dependent; rank and target-module choices matter. |
| Quantized-base PEFT preserves most quality while cutting memory dramatically. | [S-003](https://arxiv.org/abs/2305.14314) (QLoRA) | Medium | Measure quality vs. plain LoRA on your base model and hardware. |
