# Source Map

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Use explicit handoffs and bounded workers with contracts. | [S-001](https://openai.github.io/openai-agents-python/handoffs/), [S-002](https://arxiv.org/abs/2308.08155) (AutoGen) | Medium | Framework behavior is product-specific; the contract principle generalizes. |
| Coordination can amplify error propagation across agents. | [S-003](https://arxiv.org/abs/2501.06322) (multi-agent collaboration survey) | Medium | Survey evidence, not a production guarantee. |
| Multi-agent systems cost substantially more tokens than single-agent chat; orchestrator-worker with artifact handoffs is a workable production shape. | [S-004](https://www.anthropic.com/engineering/multi-agent-research-system) | Medium | Vendor engineering report on one system; token multipliers are workload-specific. |
