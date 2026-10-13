# Source Map

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| No embedding method dominates every task; benchmark aggregates don't replace domain evaluation. | [S-001](https://aclanthology.org/2023.eacl-main.148/) (MTEB), [S-002](https://docs.mteb.org/) | High | Benchmark coverage and leaderboard composition change over time. |
| Provider formatting, dimensions parameter, and similarity guidance are product-specific. | [S-003](https://platform.openai.com/docs/guides/embeddings) | High | Recheck documentation before a migration; details are version-sensitive. |
| Embeddings can be trained to truncate to smaller dimensions gracefully. | [S-004](https://arxiv.org/abs/2205.13147) (Matryoshka Representation Learning) | Medium | Applies to MRL-trained models; measure quality at each dimension regardless. |
| Embeddings from different models are not directly comparable unless trained to be compatible; upgrading a model otherwise forces recomputing stored vectors ("backfilling"), which is why migrations re-embed everything into a new index. | [S-005](https://arxiv.org/abs/2003.11942) (Towards Backward-Compatible Representation Learning, CVPR 2020) | Medium | Image-retrieval features; used as an analogy for text embeddings. |
| The number of distinct top-k document sets a single-vector embedding can return is limited by its dimension; state-of-the-art models fail on the LIMIT dataset of simple queries. | [S-006](https://arxiv.org/abs/2508.21038) (On the Theoretical Limitations of Embedding-Based Retrieval, ICLR 2026) | High | Applies to single-vector retrieval. |
