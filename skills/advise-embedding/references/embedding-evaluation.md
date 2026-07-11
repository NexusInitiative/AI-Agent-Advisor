# Embedding Evaluation Reference

Use this file when building the labeled eval set, running a model bake-off, or migrating embedding models.

## Building the Labeled Set

- **Queries:** 100–300, sampled from production logs where possible. Stratify by language, document type, query length, and query class (keyword-ish, conceptual, question-form). Include known-hard cases: ambiguous queries, rare entities, negations.
- **Labels:** for each query, mark relevant documents. Pragmatic protocol: pool the top-10 results from two quick baselines (one dense model + BM25), label that pool, and treat unlabeled documents as non-relevant. This biases recall estimates slightly but is cheap and consistent across model comparisons.
- **Refresh:** re-sample quarterly or when the product surface changes; a stale eval set rewards yesterday's traffic.

## Metrics

| Metric | Use it for |
|---|---|
| recall@k (k = your retrieval depth) | "Did the right thing make the candidate set?" — the primary metric when a reranker or LLM consumes the results |
| MRR | Single-answer lookup tasks |
| NDCG@k | Graded relevance, ranked UIs |
| p95 embed + search latency | Production viability |
| $/1M tokens embedded, index GB | Cost envelope |

Always report per-slice (language, doc type, query class) alongside aggregate. A model that wins aggregate but loses your largest slice is the wrong model.

## Bake-off Protocol

1. Freeze: chunking, preprocessing, metadata, index type and parameters, k, and any reranker.
2. For each candidate model: apply its documented query/document formatting (instructions, prefixes) exactly; embed the corpus; build an identical index configuration.
3. Run the full query set once per candidate; compute metrics with confidence intervals (bootstrap over queries).
4. Inspect 20+ losses of the losing model and 20+ of the winning model — label whether the failure was chunking, formatting, or genuinely the model. This inspection frequently reveals input bugs worth more than the model swap.
5. Decide on quality + latency + cost jointly; record the decision and the eval snapshot.

Do not compare a candidate run against last month's baseline numbers — corpus drift invalidates the comparison. Re-run the baseline in the same session.

## Dimension and Quantization Sweeps

Sweep dimensions (e.g., full, 1024, 512, 256) with the same protocol and plot recall@k vs. dimension; pick the knee. Then, holding the chosen dimension, evaluate index-level compression (int8, binary, product quantization) — index recall loss and model quality loss compound, so measure them together, not sequentially against different baselines.

## Migration Checklist

1. New index built from a full re-embed (never incremental into the old space).
2. Model ID, dimensions, normalization, preprocessing version stored with the index.
3. Shadow traffic: mirror a sample of live queries to both indexes; compare result overlap and click/answer quality where measurable.
4. Eval set passes on the new index at or above the old index, per slice.
5. Flagged cutover with instant rollback to the old index.
6. Old index retired only after the new one wins in production metrics for a defined period.

## Exact-Match Safety Net

Regardless of model quality, route identifier-like tokens (SKUs, error codes, file paths, function names) through a lexical leg (BM25 or trigram) and fuse with dense results (RRF is a solid default — see `advise-rag`). Dense-only retrieval on identifiers fails unpredictably, and no amount of model shopping fixes it.
