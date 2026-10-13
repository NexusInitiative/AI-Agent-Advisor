# Chunking and Indexing

Chunking decides what the embedding model and the generator can see. A chunk that lacks context cannot be repaired downstream. Claims here are sourced in [source-map.md](source-map.md); items marked *(heuristic)* are design heuristics, not benchmarked results.

## Chunk size and overlap are hyperparameters

Wang et al. varied chunk size on one document (the first sixty pages of a Lyft annual report), with about 170 LLM-generated queries and LLM-computed faithfulness and relevancy. Scores were highest at 256 and 512 tokens, lower at 128 and 1024, and lowest at 2048, with a 20-token overlap. That is one small test, so read it as evidence that size matters and that mid-sized chunks are a reasonable first sweep, not as a rule. Larger chunks carry more context but cost more processing; smaller chunks can raise recall but lack context (the authors' own framing).

Sweep size and overlap on your corpus using candidate recall and final answer quality.

## Strategies and what the evidence says

| Strategy | What it does | Evidence |
|---|---|---|
| Fixed-size | Splits into equal token spans, usually with overlap | Qu et al. found the extra cost of semantic chunking was not justified by consistent gains over fixed-size chunking on retrieval and answer-generation tasks |
| Semantic | Splits at sentence or topic boundaries, sometimes using embedding similarity | Same study; keep it only if it wins on your data |
| Contextual (prepend context) | An LLM writes 50–100 tokens situating each chunk in its document; prepended before embedding and BM25 indexing | Anthropic: top-20 failure rate 5.7% to 3.7% (embeddings), 2.9% (with BM25), 1.9% (with reranking), averaged over codebases, fiction, ArXiv and science papers, on one embedding configuration |
| Late chunking | Embeds the full document with a long-context embedding model, then pools token vectors per chunk | Günther et al.: chunk embeddings capture surrounding context without LLM calls and improved retrieval across tasks; requires a long-context embedding model |
| Proposition-level | Indexes atomic, self-contained factual statements | Dense X: fine-grained units outperformed passages in dense retrieval, and fine-grained prompts improved QA at a fixed budget |
| Hierarchical summaries | Recursively clusters and summarizes chunks into a tree; retrieves across levels | RAPTOR: +20% absolute on QuALITY with GPT-4; on tasks needing whole-document understanding |

**Cost of contextual chunking.** Anthropic estimated $1.02 per million document tokens with prompt caching, under stated assumptions (800-token chunks, 8k-token documents, 100 tokens of context per chunk). The cost is paid at indexing time, not at query time. Recompute it with your own sizes and current prices.

## Structure-aware splitting *(heuristic)*

When a query refers to a unit that fixed windows cut apart (a function, a table row, a numbered clause), split on that unit and keep its header with it. This preserves the unit the user asks about; it has not been benchmarked here, so compare it with fixed-size chunking on your queries, as Qu et al. did for semantic chunking.

For layout-heavy PDFs where tables and figures carry the answer, compare your text-extraction pipeline with page-image retrieval (ColPali, ICLR 2025), which outperformed text-extraction pipelines on its benchmark.

## Metadata

Store with every chunk: a stable chunk ID, document ID and version, title, section path, page or position, and a timestamp. Uses:

- **Retrieval and reading.** Barnett et al. report that adding metadata such as file name and chunk number to the retrieved context helped the reader.
- **Citation checking.** You can confirm that a cited ID was actually supplied.
- **Debugging.** A bad answer can be traced to the chunk, document version, and index build that produced it.
- **Filtering and permissions.** Apply tenant and access filters at query time, before generation (see `advise-harness`).

```json
{
  "chunk_id": "annual-report-2023-acme#p14-c3",
  "doc_id": "annual-report-2023-acme",
  "doc_version": "2023-11-01",
  "section": "Q3 Financial Results",
  "page": 14,
  "index_build": "2026-10-01"
}
```

## Index design

Choosing an ANN index type, tuning recall against latency, and sizing a vector store are covered by `advise-vector-db`. In RAG terms, two points matter: measure whether approximate search is losing relevant chunks (compare against exact search on a sample), and test filtered queries separately from unfiltered ones.

## Re-indexing and versioning

- Keep raw documents and the chunking pipeline separate from the index, and store original text with each chunk so you can re-chunk without re-fetching.
- Version the embedding model with the index. Features from different models are not interchangeable unless trained for compatibility; the backward-compatible training paper (CVPR 2020, image-retrieval features) exists precisely because upgrading a model otherwise forces recomputing every stored vector ("backfilling").
- Barnett et al. report that RAG systems require continuous calibration; rerun your evaluation set after every change to chunking, the embedding model, or the index, and keep the previous build available for rollback.
