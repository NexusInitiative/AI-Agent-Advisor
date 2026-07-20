# Source Map

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Choose models with task-specific, multi-metric evaluation rather than one leaderboard number. | [S-001](https://crfm.stanford.edu/helm/), [S-002](https://platform.openai.com/docs/models) | High | HELM is comparative evidence across scenarios; provider docs describe only their own products. |
| Cascade/routing strategies can cut cost substantially while preserving quality on some workloads. | [S-003](https://arxiv.org/abs/2305.05176) (FrugalGPT) | Medium | Reported savings are workload-specific; gains depend on router quality and validation cost. |
| Model capabilities, prices, and aliases are version-sensitive and change frequently. | [S-002](https://platform.openai.com/docs/models) | High | Re-check provider documentation at decision time; do not rely on numbers cached in advice. |
| Reasoning models suit hard, ambiguous, or accuracy-critical tasks; standard models suit speed- and cost-sensitive well-defined tasks. | [S-004](https://developers.openai.com/api/docs/guides/reasoning-best-practices) | High | Model-family behavior evolves; validate the reasoning-vs-standard split on your own eval, not on provider positioning. |
