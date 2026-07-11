# Source Map

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Prefer the simplest agent architecture that works; add machinery in proportion to need. | [S-001](https://www.anthropic.com/engineering/building-effective-agents) | Medium | Vendor engineering guidance, not independent proof. |
| Agent runs benefit from traceable execution and structured run/step records. | [S-002](https://openai.github.io/openai-agents-python/tracing/), [S-003](https://openai.github.io/openai-agents-python/handoffs/) | High | SDK mechanics are provider-specific; the trace shape generalizes. |
| Manage AI risk through explicit governance, measurement, and staged deployment. | [S-004](https://www.nist.gov/itl/ai-risk-management-framework) | High | Framework guidance needs organizational implementation. |
| Prompt injection is the top-listed LLM application risk and a runtime security concern. | [S-005](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | Medium | OWASP is guidance, not a complete control set. |
