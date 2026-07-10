---
name: advise-models
description: |
  This skill should be used when the user asks to "which model should I use", "advise on models",
  "help me choose an LLM", "what model is best for my use case", "compare models",
  "should I use GPT or Claude", "how do I reduce model cost", "should I route requests",
  or needs guidance on model selection, routing, quality, latency, privacy, or deployment trade-offs.
---

# Model Advisor

Treat model selection as a measured product decision, not a leaderboard choice. Ask what the model must do, which failures are unacceptable, the input modalities and length, deployment/privacy constraints, traffic shape, latency target, and budget. Name any assumption that is missing.

## Start with a capability baseline

Choose one capable model that supports the required modalities, tools, structured output, context length, and deployment requirements. Build a representative evaluation set before comparing providers. Include ordinary traffic, difficult cases, long inputs, malformed inputs, safety cases, and real production failures. Record task success, critical failure rate, p95 latency, token use, cost, and availability separately.

Do not choose from a general benchmark alone. A coding, retrieval, vision, multilingual, or tool-use task can rank models differently. Treat provider documentation as authoritative for supported features and pricing, not as independent evidence of quality.

## Make the recommendation

- Use a frontier model when incorrect reasoning, coding failures, complex tool use, or high-value decisions dominate cost.
- Use a smaller model when the task is narrow, well-specified, validated, and high-volume.
- Use a local or self-hosted model when data residency, offline operation, customization, or predictable marginal cost outweigh managed-service operations.
- Use a specialized model only when its modality or task advantage is measured on the real workload.

Start with one model. Add routing only after you have evidence that a cheaper path handles a clear subset safely. Route on observable task features or a calibrated confidence policy, log every route, and always keep an escalation path. Never route a high-risk action to a lower-capability model solely because its response is shorter or cheaper.

## Compare fairly

Hold prompt, tools, retrieval, sampling, timeouts, and evaluation cases constant. Run repeated trials for nondeterministic tasks. Report category-level results and worst critical failures, not only an average. Re-run the comparison when a provider changes a model version, price, context limit, or tool interface.

Use this output:

| Requirement | Candidate | Evidence | Decision |
|---|---|---|---|
| Critical task success | | task eval | |
| Latency and cost | | p50/p95 and tokens | |
| Security and deployment | | contract/configuration | |
| Fallback behavior | | failure drill | |

## Common traps

Do not silently substitute model aliases in production. Pin versions where the provider permits it, retain a rollback candidate, and monitor quality drift. Do not use a model score as a proxy for grounding or authorization. For model-specific prompting, see `advise-prompting`; for measurement, see `advise-eval`.

## Sources

For benchmark interpretation, routing criteria, and source limits, read [model-selection.md](references/model-selection.md) and [source-map.md](references/source-map.md).

- [OpenAI model documentation](https://platform.openai.com/docs/models)
- [HELM benchmark](https://crfm.stanford.edu/helm/latest/)
- [LLM routing research](https://arxiv.org/abs/2401.12973)
