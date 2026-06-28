# Retrieval Architectures

## Sparse Retrieval (BM25)

BM25 is a term-frequency / inverse-document-frequency ranking function. It scores chunks based on exact token overlap with the query.

**Strengths:**
- Excellent on keyword-heavy queries: error codes, product identifiers, proper nouns, technical terms
- No training required; fast and cheap to run
- Highly interpretable — you can see exactly which tokens drove the score
- Generalizes well across domains without fine-tuning (validated by BEIR benchmark)

**Weaknesses:**
- Vocabulary mismatch: "cardiac arrest" doesn't match "heart attack"
- No semantic understanding: can't handle paraphrase or conceptual queries
- Sensitive to typos and abbreviations

**When to use as your primary retriever:** Your queries are dominated by exact-match needs (log file search, code search, product catalog lookup, legal citation retrieval).

---

## Dense Retrieval (DPR and descendants)

Dense Passage Retrieval (Karpukhin et al., 2020) uses a bi-encoder: one encoder for the query, one for passages. Both produce fixed-size vectors; retrieval is maximum inner product search (MIPS) in that vector space.

**Strengths:**
- Handles semantic similarity: "cardiac arrest" matches "heart attack"
- Captures conceptual relationships, not just token overlap
- Scales well with ANN indexes (FAISS, ScaNN, HNSW)

**Weaknesses:**
- Fails on rare or out-of-vocabulary terms (product codes, error strings)
- Embedding quality bottlenecks retrieval quality — a bad embedding model produces bad retrieval
- BEIR benchmark showed DPR generalizes poorly out-of-domain without fine-tuning
- More expensive to run than BM25 at large scale

**When to use:** Queries are primarily conceptual, semantic, or paraphrase-heavy. When query vocabulary doesn't match document vocabulary.

**Embedding model selection:** General-purpose models (text-embedding-3-small, Cohere embed-v3) work for most use cases. Domain-specific fine-tuning (using hard negatives, contrastive loss) improves recall significantly for specialized corpora (medical, legal, code). Evaluate on your actual query distribution using BEIR-style zero-shot evaluation before committing to a model.

---

## Hybrid Retrieval + RRF

The practical default for most production RAG systems. Run BM25 and dense retrieval independently, then fuse their ranked lists.

**Reciprocal Rank Fusion (RRF)** is the standard fusion method (Cormack et al., 2009):

```
RRF_score(d) = Σ 1 / (k + rank_i(d))
```

Where `k=60` is the standard constant, `rank_i(d)` is the rank of document `d` in retriever `i`'s result list. Documents appearing high in multiple lists get boosted; documents missing from one list get the penalty of a low rank.

**Why RRF works:**
- Requires no training or score normalization
- Robust to differences in score distributions between retrievers
- Consistently outperforms individual retrievers across BEIR tasks
- Outperforms linear interpolation of scores in most experiments

**Implementation sketch:**
```python
def rrf_fusion(results_list: list[list[str]], k: int = 60) -> dict[str, float]:
    scores = {}
    for results in results_list:
        for rank, doc_id in enumerate(results):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
```

**When hybrid beats single-retriever:** Almost always for diverse query sets. The BEIR benchmark shows that the relative performance of sparse vs. dense retrieval varies dramatically by domain — hybrid with RRF hedges against this uncertainty.

---

## Reranking

Reranking is a second-stage step applied after initial retrieval. Retrieve 20–50 candidates, then run a cross-encoder reranker to re-score them and keep the top 5.

**Cross-encoders vs. bi-encoders:**
- Bi-encoders (used in dense retrieval) encode query and passage independently — fast, parallelizable
- Cross-encoders encode the query-passage pair together — much more accurate but O(n) latency per candidate

**When to add a reranker:**
- Initial retrieval precision is low (irrelevant chunks in top-5)
- You have budget for the additional latency (~100–300ms for a cross-encoder pass over 20 candidates)
- Query-passage relevance is nuanced and depends on fine-grained semantic interaction

**Off-the-shelf rerankers:** Cohere Rerank, Jina Reranker, BGE Reranker, Colbert v2. All work well; evaluate on your data before committing.

**Contextual compression:** An alternative to reranking — after retrieval, use an LLM to extract only the relevant sentence(s) from each chunk rather than passing the full chunk. Reduces noise in context and token cost. Works well when chunks are large and only partially relevant.

---

## Key Papers

- **DPR**: Karpukhin et al., "Dense Passage Retrieval for Open-Domain Question Answering" (2020) — https://arxiv.org/abs/2004.04906
- **BEIR**: Thakur et al., "BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of IR Models" (2021) — https://arxiv.org/abs/2104.08663
- **RRF**: Cormack et al., "Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods" (2009) — https://dl.acm.org/doi/10.1145/1571941.1572114
- **RAG Survey**: Gao et al., "Retrieval-Augmented Generation for Large Language Models: A Survey" (2023) — https://arxiv.org/abs/2312.10997
