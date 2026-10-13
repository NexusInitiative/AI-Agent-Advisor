# Source Map

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Relevant content can be underused in the middle of long inputs. | [S-001](https://arxiv.org/abs/2307.03172) (Lost in the Middle) | Medium | Result varies by model, task, and context length; verify on current models. |
| Context engineering should select and compact the smallest high-signal token set. | [S-002](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Medium | Vendor engineering guidance, not independent proof. |
| Long-context prompting benefits from deliberate document placement and structure. | [S-003](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/long-context-tips) | Medium | Provider-specific guidance; details change across model generations. |
| Stable instruction prefixes enable provider prompt caching. | [S-004](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | High | Mechanics and pricing are provider- and version-specific. |
| Reliability fell as input length grew even on simple tasks across 18 models; distractors and low question-answer similarity made it worse. | [S-005](https://www.trychroma.com/research/context-rot) (Chroma, Context Rot, July 14, 2025) | Medium | Technical report, not peer reviewed. |
| Models claiming 32K or more tokens of context often could not sustain satisfactory performance at 32K on harder tasks (only half of 17 tested), despite near-perfect needle-in-a-haystack scores. | [S-006](https://arxiv.org/abs/2404.06654) (RULER, COLM 2024) | High | Synthetic tasks; 2024 models. |
| Tested LLMs scored 39% lower on average in multi-turn than single-turn conversations across six tasks, mostly from unreliability; after a wrong turn they often did not recover. | [S-007](https://arxiv.org/abs/2505.06120) (LLMs Get Lost In Multi-Turn Conversation) | Medium | Preprint; simulated conversations. |
| Output quality first rose and then fell as retrieved passages were added; reordering helped without training. | [S-008](https://arxiv.org/abs/2410.05983) (Long-Context LLMs Meet RAG) | Medium | Preprint. |
| The token-budget slot sizes in `context-budgeting.md` are illustrative arithmetic. | None | n/a | No source establishes default shares for a context window; derive budgets from measured token counts. |
