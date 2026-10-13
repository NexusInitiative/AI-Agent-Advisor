# Retrieval Architectures

Every statement here is tied to a source in [source-map.md](source-map.md). Where evidence is vendor-reported or comes from a single benchmark, the text says so. None of it replaces measuring on your own queries.

## Sparse retrieval (BM25)

BM25 scores documents by lexical overlap with the query, adjusted for term frequency and document length. In BEIR, an 18-dataset zero-shot benchmark, BM25 was a robust baseline. Anthropic's illustration of why it still matters: a query for an exact error code such as "TS-999" can be matched literally by BM25 while an embedding model may surface content about error codes in general.

Its limit is vocabulary mismatch: a query and a document that use different words for the same idea will not overlap lexically.

**Use as a primary retriever** when queries are dominated by exact strings (identifiers, error codes, names, citations). **Always keep it as a baseline** so you can tell whether a dense or hybrid upgrade is actually helping.

## Dense retrieval

Dense Passage Retrieval (Karpukhin et al., EMNLP 2020) encodes queries and passages into vectors with a bi-encoder and retrieves by vector similarity. It matches meaning across different wording. Two measured limits:

- **Out-of-domain generalization.** BEIR found dense and learned-sparse retrievers were computationally efficient but often underperformed other approaches, highlighting room to improve generalization.
- **A structural ceiling.** Weller et al. (ICLR 2026) show that the number of distinct top-k document sets a single-vector embedding can return is limited by its dimension, and that even state-of-the-art models fail on LIMIT, a dataset of simple queries built to test this. If relevance is combinatorial (many documents jointly relevant to arbitrary query combinations), single-vector retrieval can fail regardless of training data.

Embedding model choice, dimensionality, and evaluation belong to `advise-embedding`.

## Hybrid retrieval and fusion

Run lexical and dense retrieval independently, then fuse. Evidence for doing so:

- Bruch et al. found RRF-based hybrid retrieval outperformed pure-lexical and pure-semantic retrieval on most datasets, and was particularly effective out of domain.
- Anthropic's Contextual Retrieval tests added BM25 to contextual embeddings and cut the top-20 failure rate from 3.7% to 2.9%.
- Wang et al. recommended hybrid search (BM25 plus dense) as the efficient default, with HyDE added when latency allows.

**Choosing the fusion method.** Reciprocal Rank Fusion scores a document as `sum over retrievers of 1 / (c + rank)`. Elastic documents `rank_constant` (the `c`) with a default of 60 and states that RRF requires no tuning. Bruch et al. report the opposite emphasis: RRF was sensitive to its parameters, a tuned RRF generalized poorly out of domain, and a convex combination of normalized scores (one parameter, tuned on a small labeled set) significantly outperformed RRF on NDCG on every dataset they tested. Practical reading: begin with RRF because it needs no labels; once you have a small labeled set (Bruch et al. report the convex combination is sample efficient), compare it with a tuned convex combination on held-out queries.

```python
def rrf_fusion(results_list: list[list[str]], c: int = 60) -> dict[str, float]:
    """Reciprocal Rank Fusion. Elastic's documented default for c is 60."""
    scores: dict[str, float] = {}
    for results in results_list:
        for rank, doc_id in enumerate(results, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (c + rank)
    return dict(sorted(scores.items(), key=lambda kv: kv[1], reverse=True))
```

Native hybrid search in your vector store avoids running two systems; engine selection is covered by `advise-vector-db`.

## Reranking

A second stage re-scores the top candidates with a model that reads the query and passage together.

- BEIR found re-ranking and late-interaction models best on average in zero-shot retrieval, at high computational cost.
- Anthropic retrieved 150 candidates, reranked them with a Cohere reranker, and passed 20 to the generator; reranking took the failure rate from 2.9% to 1.9%.
- Wang et al. recommended monoT5 as a comprehensive reranking choice in their comparison.

Cost is not predictable from a paper: measure added latency and spend on your candidate counts. Compare recall of the evidence in the final context before and after, not only a ranking metric.

## Late interaction and visual documents

ColBERT (SIGIR 2020) scores with token-level interaction between query and document vectors. ColPali (ICLR 2025) applies the idea to page images, embedding document pages directly with a vision-language model, and outperformed text-extraction retrieval pipelines on its ViDoRe benchmark. Consider it when tables, figures, and layout carry the answer and OCR or parsing is the weak link. Compare against your parsing pipeline on your documents; the benchmark is the authors' own.

## Query transformation

- **HyDE** (Gao et al.) has an LLM write a hypothetical answer document, embeds that instead of the query, and retrieves real neighbors; it outperformed an unsupervised dense retriever and approached fine-tuned retrievers across tasks.
- **Rewrite-Retrieve-Read** (Ma et al., EMNLP 2023) rewrites the query before retrieval and improved open-domain QA, including with a small trained rewriter.
- In Wang et al.'s comparison, hybrid search with HyDE was recommended, while query rewriting and decomposition did not improve retrieval as much.

Treat each as a hypothesis for a specific query type, such as vague conversational queries or multi-part questions, and measure candidate recall with and without it.
