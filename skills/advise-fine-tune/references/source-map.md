# Source Map

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Fine-tuning needs task-matched train and holdout data. | [S-001](https://platform.openai.com/docs/guides/fine-tuning) | High | Applies to the documented service; data governance is organization-specific. |
| Prefer parameter-efficient adaptation before full tuning. | [S-002](https://arxiv.org/abs/2106.09685), [S-003](https://arxiv.org/abs/2305.14314) | Medium | Measure quality and serving behavior for the base model and hardware. |
