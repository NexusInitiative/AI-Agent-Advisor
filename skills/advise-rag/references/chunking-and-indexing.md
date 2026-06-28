# Chunking and Indexing

## Why Chunking Matters More Than Most Teams Think

The embedding model encodes a fixed-size vector for each chunk. If a chunk lacks sufficient context to be meaningfully embedded, no retrieval architecture can save you. Chunking is often treated as a preprocessing detail — it's actually a core architectural decision.

---

## Chunking Strategies

### Fixed-Size Chunking

Split documents into chunks of N tokens with M tokens of overlap between consecutive chunks.

- **Default parameters:** 512 tokens, ~50 tokens overlap (≈10%)
- **Pros:** Simple, fast, predictable chunk count, easy to reason about
- **Cons:** Splits mid-sentence, mid-paragraph, or mid-table; loses structural context
- **Use when:** Getting started, testing baseline performance, structured data with consistent density

### Semantic Chunking

Split at natural semantic boundaries: sentence breaks, paragraph breaks, section headers. Optionally use an embedding similarity threshold to merge or split segments.

- **Pros:** Chunks correspond to coherent ideas, better for embedding quality
- **Cons:** Variable chunk size complicates indexing; slower preprocessing
- **Use when:** Prose-heavy documents (reports, articles, books), where paragraph structure reflects semantic units

### Hierarchical / Multi-Granularity Chunking

Index chunks at multiple granularities: sentence-level, paragraph-level, document-level. Retrieve at fine granularity, but return the surrounding parent chunk for context.

- **Pros:** Retrieval precision at sentence level, generation context at paragraph level
- **Cons:** Larger index, more complex retrieval pipeline
- **Use when:** Users ask pinpoint questions but need surrounding context to generate good answers ("what was the Q3 revenue?" in a financial report)

### Contextual Chunking (Anthropic Approach)

Before embedding, prepend a short context description to each chunk using an LLM call:

```
Context: This chunk is from a 2023 annual report for Acme Corp, in the section
"Q3 Financial Results." It describes quarterly revenue breakdown by product line.

[original chunk text follows]
```

Anthropic's contextual retrieval engineering post reported a 49% reduction in retrieval failures using this technique, and further gains when combined with BM25. The LLM-generated context anchors the chunk to its document-level meaning, preventing the common failure where a chunk that's meaningful in context becomes meaningless in isolation.

**Cost:** One LLM call per chunk at indexing time. Use prompt caching to reduce cost when re-indexing overlapping document sets. At indexing time this is acceptable; the cost does not affect query latency.

### Document-Specific Strategies

| Document Type | Recommended Strategy |
|---|---|
| Long prose (reports, books) | Semantic or contextual chunking by paragraph/section |
| Code | Chunk by function, class, or method — never by token count |
| Tables / structured data | One row or entity per chunk; embed column headers with each row |
| HTML / web pages | Strip boilerplate first; chunk by `<p>` or `<section>` tags |
| PDFs | Extract text with layout awareness; chunk by visual section |
| Emails / short docs | Entire document as one chunk; no splitting needed |
| Mixed corpora | Detect document type; apply strategy per type |

---

## Metadata: The Underused Multiplier

Every chunk should carry structured metadata alongside its text. Metadata enables:
- **Filtered retrieval:** "Only search within documents published after 2023"
- **Citation:** Surface the source document, section, and page in the generated response
- **Reranking signals:** Use metadata features as additional scoring signals
- **Debugging:** Trace retrieved chunks back to their source when diagnosing failures

**Minimum metadata per chunk:**
```json
{
  "doc_id": "annual-report-2023-acme",
  "doc_title": "Acme Corp Annual Report 2023",
  "section": "Q3 Financial Results",
  "page": 14,
  "chunk_index": 3,
  "created_at": "2023-11-01"
}
```

Add domain-specific metadata as needed: author, category, product line, jurisdiction, language, confidence score.

---

## Index Design

### Vector Index Options

| Index Type | Scale | Recall | Speed | Notes |
|---|---|---|---|---|
| Flat (exact) | <1M chunks | 100% | Slow at scale | Good for dev/testing |
| HNSW | 1M–100M | 95–99% | Fast | Default for most systems (used in pgvector, Weaviate, Qdrant) |
| IVF | >10M | 90–98% | Tunable | Requires training; good for very large corpora |
| ScaNN | >100M | 97–99% | Very fast | Google's production-grade ANN |

### Hybrid Index Setup

Run a separate BM25 index (Elasticsearch, OpenSearch, or BM25s) alongside your vector index. At query time, retrieve from both, fuse with RRF. Most vector databases (Weaviate, Qdrant, Elasticsearch) now offer built-in hybrid search — use native hybrid if available to avoid maintaining two separate systems.

### Re-indexing Strategy

Plan for re-indexing from the start:
- Keep your raw documents and chunking pipeline separate from your index
- Version your embedding model — changing models invalidates all existing embeddings
- Use incremental indexing for live corpora; avoid full re-index on every update
- Store original document text alongside embeddings so you can re-chunk without re-fetching source data

---

## Key References

- **Anthropic Contextual Retrieval**: https://www.anthropic.com/engineering/contextual-retrieval
- **RAG Survey (Gao et al.)** — Section 3 on Advanced RAG indexing strategies: https://arxiv.org/abs/2312.10997
- **Original RAG paper (Lewis et al., 2020)**: https://arxiv.org/abs/2005.11401
