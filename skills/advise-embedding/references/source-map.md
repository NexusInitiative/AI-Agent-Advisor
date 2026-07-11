# Source Map

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| No embedding method dominates every task; benchmark aggregates don't replace domain evaluation. | [S-001](https://aclanthology.org/2023.eacl-main.148/) (MTEB), [S-002](https://docs.mteb.org/) | High | Benchmark coverage and leaderboard composition change over time. |
| Provider formatting, dimensions parameter, and similarity guidance are product-specific. | [S-003](https://platform.openai.com/docs/guides/embeddings) | High | Recheck documentation before a migration; details are version-sensitive. |
| Embeddings can be trained to truncate to smaller dimensions gracefully. | [S-004](https://arxiv.org/abs/2205.13147) (Matryoshka Representation Learning) | Medium | Applies to MRL-trained models; measure quality at each dimension regardless. |
