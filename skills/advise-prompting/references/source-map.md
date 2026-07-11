# Source Map

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Define instructions, evidence rules, and output contracts explicitly; provider mechanics differ. | [S-001](https://platform.openai.com/docs/guides/prompt-engineering), [S-002](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview) | High | Product syntax changes; keep the contract provider-independent. |
| Structured-output modes plus deterministic validation beat free-form JSON. | [S-003](https://platform.openai.com/docs/guides/structured-outputs) | High | Feature availability and syntax are provider- and version-specific. |
| Example content steers reasoning style; few-shot effects vary by model and task. | [S-004](https://arxiv.org/abs/2201.11903) (Chain-of-Thought Prompting) | Medium | Original results on older models; magnitude differs on current models. |
