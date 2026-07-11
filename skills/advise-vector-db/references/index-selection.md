# Index Selection Reference

Use this file when benchmarking index candidates, tuning parameters, or running the pre-production operations checklist.

## Benchmark Protocol

1. **Ground truth first:** run exact (flat) search over your real vectors for the full query set, with real filters. This defines recall@k = 1.0 and the latency bar to beat.
2. **Same everything:** candidates get identical vectors, filters, k, hardware, and concurrency. Warm caches consistently.
3. **Measure per candidate:** recall@k vs. ground truth, p50/p95 latency at target concurrency, build time, memory/index size, and ingest throughput while querying.
4. **Filtered and unfiltered separately.** Also sweep filter selectivity (0.1%, 1%, 10%, 50% of corpus) — engines diverge hardest here.
5. Plot recall vs. p95 latency; choose on the curve, not on defaults. ANN-Benchmarks methodology is the reference shape for this exercise.

## Parameter Tuning Cheat Sheet

**HNSW** (memory-resident graph):

| Parameter | Effect | Guidance |
|---|---|---|
| `M` (links/node) | Build memory + quality | 16–48 typical; higher for high dimensions or high recall targets |
| `efConstruction` | Build time vs. graph quality | 100–400; raise until recall stops improving on your set |
| `efSearch` | Query-time recall vs. latency | Tune last, per query class; must be ≥ k |

Updates and deletes degrade HNSW graphs over time — plan periodic rebuilds or use engines with repair.

**IVF (+ quantization)** (memory-constrained scale):

| Parameter | Effect | Guidance |
|---|---|---|
| `nlist` (clusters) | Partition granularity | ~√N to 4√N as a starting range; retrain centroids when distribution shifts |
| `nprobe` | Clusters searched: recall vs. latency | Sweep 1→nlist; the knee is your setting |
| PQ/SQ settings | Footprint vs. recall | Evaluate jointly with embedding dimension (`advise-embedding`) — losses compound |

**Rule:** re-tune after any change to embedding model, dimensions, corpus size (>2×), or filter patterns. Yesterday's knee moves.

## Filtered Search Notes

Engines implement filtering as pre-filter (search only matching vectors), post-filter (search then discard), or hybrid. Post-filtering with approximate search silently reduces effective k and recall for selective filters — ask which strategy your engine uses per query and verify with the selectivity sweep. Authorization filters must be pre- or in-search under all configurations; write a test that plants near-identical content in two tenants and asserts zero leakage at high `efSearch`/`nprobe`.

## Pre-Production Operations Checklist

- [ ] Bulk backfill executed at full scale; duration recorded (= your DR window)
- [ ] Streaming upserts under query load: latency impact measured
- [ ] Deletes verified: item unfindable immediately after delete, including under replicas
- [ ] Rebuild at 2× scale rehearsed; queries served during rebuild
- [ ] Backup taken and actually restored into a fresh environment
- [ ] Failover/node-loss drill (self-hosted) or SLA + incident history reviewed (managed)
- [ ] Cost projected at 18-month scale: vectors × dimensions × replicas + query compute
- [ ] Probe set wired up: sampled production queries compared against exact search on a schedule, alerting on recall drop

## Migration Between Engines or Index Types

Dual-write or snapshot-restore into the new engine, replay the benchmark, shadow live traffic, then cut over behind a flag. Vectors are re-embeddable — the metadata, ACLs, and IDs are the part you must not lose. Keep the old engine until the probe set has passed in production for a defined period.
