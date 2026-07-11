# Source Map

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| ANN is a recall/latency/resource trade-off; rankings shift with data, filters, and hardware. | [S-001](https://ann-benchmarks.com/), [S-002](https://arxiv.org/abs/1807.05614) (ANN-Benchmarks) | High | Benchmark results do not transfer directly to your workload; re-measure. |
| HNSW provides strong graph-based ANN recall/latency at memory and build cost. | [S-003](https://arxiv.org/abs/1603.09320) (Malkov & Yashunin) | High | Update/delete degradation and parameter sensitivity are implementation-specific. |
| Relational vector storage (pgvector) has documented operator, index, and tuning behavior. | [S-004](https://github.com/pgvector/pgvector) | High | Behavior is version-specific; recheck docs before relying on limits. |
