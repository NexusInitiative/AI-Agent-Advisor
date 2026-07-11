---
name: advise-vector-db
description: |
  This skill should be used when the user asks "which vector database should I use",
  "advise on vector DB", "help with vector storage", "Pinecone vs Weaviate vs pgvector",
  "how should I store my embeddings", "HNSW vs IVF", "how do I scale similarity search",
  or needs guidance on vector database selection, metadata filtering, indexing, or operational trade-offs.
---

# Vector DB Advisor

Choose the simplest store that satisfies measured retrieval, filtering, availability, privacy, and operational requirements. A vector database cannot fix poor chunking, embeddings, or relevance — establish those first (`advise-rag`, `advise-embedding`). Most teams choose a vector DB before they have the query workload that would tell them which one they need.

## Step 1 — Write the Data and Query Contract

Ask or infer, and write down:

- **Scale:** vector count now and in 18 months; dimensions; growth from re-embeds and versioning (often 2–3× the naive estimate).
- **Traffic:** read QPS, write/update rate, batch vs. streaming ingest, acceptable p95 latency, recall target.
- **Filters:** which metadata filters run with every query (tenant, ACL, date, type), their cardinality and selectivity. Filtered ANN behaves very differently from unfiltered — this is the most under-specified requirement in practice.
- **Isolation & compliance:** tenant separation, per-user ACLs, residency, backup/retention.
- **Team reality:** who operates this at 3am, and what databases do they already run well?

Build a representative query set — queries *with their real filters* — before selecting anything. Product comparisons without your workload measure marketing, not fit. If the corpus is under a few hundred thousand vectors, note that now: the honest answer to "which vector DB?" at that scale is often "the database you already run, with exact search or a basic index."

---

## Step 2 — Pick the Store Category (Boring Wins Ties)

- **Relational extension (pgvector on Postgres):** the default when vectors are up to the low millions, metadata joins and transactions matter, and the team already operates Postgres. One system of record, real ACID, mature ops. Ceiling: very large corpora and extreme QPS.
- **Managed vector service (Pinecone-class):** when elasticity, availability SLAs, and zero index ops are worth per-vector pricing and data leaving your infra. Right for small teams scaling fast without DB expertise.
- **Self-hosted dedicated engine (Qdrant/Weaviate/Milvus-class):** when you need index control, custom deployment, or cost control at large scale *and* have the operational capacity to run a distributed stateful system.
- **Library-only (FAISS/hnswlib in-process):** static or rebuild-tolerant corpora, offline evaluation, single-node services. No CRUD story at scale — that's the trade.

Don't choose by feature checklist. Run a proof of concept on your real workload for the top two candidates; the differences that matter (filtered recall, ingest behavior, ops surprises) only show up there.

---

## Step 3 — Choose and Tune the Index Deliberately

- **Flat/exact search** for small corpora (≲ a few hundred thousand vectors, workload-dependent), offline evals, and as the recall ground truth for tuning everything else. If exact search meets latency, take it — perfect recall, zero tuning.
- **HNSW** (Malkov & Yashunin's graph-based method) as the ANN default: strong recall/latency at the cost of memory and build/update expense. Tune `efSearch` (query-time recall/latency), `M` and `efConstruction` (build-time quality/cost).
- **IVF, optionally with quantization (PQ/SQ):** when memory, not latency, is the binding constraint at large scale. Tune `nlist`/`nprobe`; quantization trades recall for footprint.

The ANN-Benchmarks results make the operating rule clear: rankings shift with dataset, dimensionality, filters, and hardware — **never claim an index or setting is universally best; benchmark against exact-search ground truth on your vectors.** Index parameters, embedding dimension, quantization, and filter selectivity interact; tune them jointly, reporting filtered and unfiltered workloads separately.

---

## Step 4 — Treat Metadata and Security as First-Class

- Store with every vector: stable ID, source/version, document timestamp, tenant namespace, ACL fields, and deletion state.
- **Authorization filters execute inside or before the search — never post-filter a candidate list that already crossed tenant boundaries.** Verify the engine enforces this under approximate search, then test it: similar content in two tenants, assert zero cross-retrieval.
- Model your real filter patterns during the POC. High-cardinality or low-selectivity filters can crater approximate recall or latency depending on the engine's filtered-search implementation.
- Use hybrid retrieval (dense + lexical) when exact tokens matter — see `advise-rag` for fusion; keep vector similarity, keyword ranking, filtering, and reranking independently measurable stages.

---

## Step 5 — Validate Operations Before Committing

The index benchmark is the easy half. Before production, test: bulk backfill time (also your disaster-recovery time), streaming updates and deletes (tombstone behavior — deleted items must stop appearing immediately), index rebuild duration at 2× current scale, backup/restore actually executed, failover, noisy-neighbor behavior under mixed read/write load, and cost projected at 18-month scale including replicas.

Monitor in production: sampled recall against exact search on a probe set, p95 latency, filter-error rate, index size and memory, write backlog, and failed deletes. Recall regressions are silent — only the probe set catches them.

Finally, plan the exit before the entrance: vectors are re-derivable from source text, so the durable assets are your documents, metadata, ACLs, and IDs. Any design that makes those exportable keeps every future migration (engine, index, or embedding model) a mechanical exercise instead of a hostage negotiation.

---

## Common Failure Modes and Fixes

| Symptom | Likely Cause | Fix |
|---|---|---|
| Great unfiltered recall, terrible with filters | Filtered-ANN implementation mismatch | Re-benchmark with real filters; tune or switch engines |
| Cross-tenant results appear | Post-search filtering | Enforce namespace/ACL inside the search path; add the two-tenant test |
| Deleted docs keep surfacing | Tombstones not compacted / eventual deletes | Verify delete semantics; add failed-delete monitoring |
| Latency spikes during ingest | Index rebuilds competing with queries | Separate ingest windows or engines with incremental indexes |
| Recall degraded slowly over months | Drift + quantization + no probe set | Sampled exact-search comparison as a standing monitor |
| Costs 5× the estimate at scale | Replicas, dimensions, and re-embeds ignored | Re-project with the Step 1 contract; consider dimension reduction (`advise-embedding`) |
| "Best" engine from a blog underperforms | Someone else's workload | POC on your queries, filters, and hardware |

---

## References

- **Index parameter tuning, POC benchmark protocol, and the operations checklist:** read [index-selection.md](references/index-selection.md) when benchmarking candidates or preparing production.
- **Verified sources with claims and caveats:** read [source-map.md](references/source-map.md) when citing evidence behind these recommendations.
