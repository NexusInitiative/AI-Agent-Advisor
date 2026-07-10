# Index Selection

Benchmark exact search first to establish recall. Then measure HNSW or IVF/quantized candidates against the same vectors, filters, concurrency, and p95 latency. Apply tenant and authorization filters before returning candidates. Test deletion, backfill, backup/restore, rebuild duration, and index migration before choosing a store.
