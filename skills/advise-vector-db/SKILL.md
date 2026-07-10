---
name: advise-vector-db
description: |
  This skill should be used when the user asks to "which vector database should I use",
  "advise on vector DB", "help with vector storage", "Pinecone vs Weaviate vs pgvector",
  "how should I store my embeddings", "HNSW vs IVF", "how do I scale similarity search",
  or needs guidance on vector database selection, metadata filtering, indexing, or operational trade-offs.
---

# Vector DB Advisor

Choose the simplest store that satisfies measured retrieval, filtering, availability, privacy, and operational requirements. A vector database cannot fix poor chunking, embeddings, or relevance judgments; establish those first.

## Start with the data and query contract

Ask corpus size and growth, vector dimensions, read/write rate, acceptable p95 latency, recall target, filter patterns, tenant isolation, durability, regions, backup needs, budget, and existing database expertise. Build a representative query set with required filters before selecting a product.

Use a relational database extension when vectors are modest in scale, metadata joins and transactions matter, and the team already operates the database. Use a managed vector service when operational simplicity, elasticity, or availability is more valuable than direct index tuning. Use a dedicated self-hosted engine when you need control, custom deployment, or have the operational capacity. Do not choose by vendor feature checklist alone; run a proof of concept against the real workload.

## Choose an index deliberately

- Use exact/flat search for small corpora, offline evaluation, or when recall is non-negotiable and latency permits.
- Use HNSW for strong low-latency recall when memory and build/update cost are acceptable.
- Use IVF or compressed indexes when corpus size or memory requires a tunable recall/latency trade-off.

Index parameters, embedding dimension, quantization, filter selectivity, and hardware interact. Tune with recall@k and latency together; report filtered and unfiltered workloads separately. Rebuild or migrate safely when changing embedding space or index type.

## Treat metadata and security as first-class

Store stable IDs, source/version, document timestamps, ownership or tenant namespace, access-control fields, and deletion state. Apply authorization filters before or inside retrieval, never after returning cross-tenant candidates. Model the filter patterns you will query; arbitrary high-cardinality filters can dominate latency or reduce approximate recall.

Use hybrid retrieval when exact tokens, product codes, or names matter. Keep vector similarity, keyword ranking, filtering, and reranking as independently measurable stages.

## Validate operations

Test ingest/backfill, updates, deletes, backup/restore, disaster recovery, index rebuild time, noisy-neighbor behavior, cost at growth, and cross-tenant isolation. Monitor recall samples, latency, filter error rate, index size, write backlog, and failed deletes. Never claim an ANN setting is universally best; benchmark it.

For embeddings see `advise-embedding`; for RAG quality see `advise-rag`.

## Sources

For index and operational evaluation criteria, read [index-selection.md](references/index-selection.md) and [source-map.md](references/source-map.md).

- [ANN-Benchmarks paper](https://arxiv.org/abs/1807.05614)
- [HNSW paper](https://arxiv.org/abs/1603.09320)
- [pgvector documentation](https://github.com/pgvector/pgvector)
