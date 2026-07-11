# Source Map

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Relevant content can be underused in the middle of long inputs. | [S-001](https://arxiv.org/abs/2307.03172) (Lost in the Middle) | Medium | Result varies by model, task, and context length; verify on current models. |
| Context engineering should select and compact the smallest high-signal token set. | [S-002](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Medium | Vendor engineering guidance, not independent proof. |
| Long-context prompting benefits from deliberate document placement and structure. | [S-003](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/long-context-tips) | Medium | Provider-specific guidance; details change across model generations. |
| Stable instruction prefixes enable provider prompt caching. | [S-004](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | High | Mechanics and pricing are provider- and version-specific. |
