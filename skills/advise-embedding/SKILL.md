---
name: advise-embedding
description: |
  This skill should be used when the user asks to "advise on embeddings", "what embedding model should I use",
  "help with embedding strategy", "how do I create good embeddings", "text embedding guidance",
  "which similarity metric should I use", "should I normalize embeddings", "why is semantic search bad",
  or needs guidance on embedding models, indexing inputs, dimensions, or retrieval evaluation.
---

# Embedding Advisor

## Step 1 — Diagnose Before Choosing a Model

Ask or infer before recommending anything:

**About the task:** Is this retrieval (query → document), similarity/dedup (document → document), clustering, classification features, or reranking input? Models tuned for retrieval asymmetry behave differently from symmetric-similarity models, and the right choice follows the task.

**About the data:** Languages? Code, prose, tables, or mixed? Typical unit length vs. the model's context limit? Do exact identifiers matter (SKUs, error codes, function names)?

**About constraints:** Latency and throughput targets, embedding + storage budget, privacy (can text leave your infra?), and corpus size — dimensions × vectors is your storage bill.

The MTEB benchmark's core finding (Muennighoff et al.) is the operating assumption here: **no embedding model dominates across tasks**. A model at the top of an aggregate leaderboard can lose on your domain. Leaderboards select candidates; your labeled data selects the winner.

---

## Step 2 — Build the Labeled Baseline First

Before comparing models, create a small evaluation set — this is the single highest-leverage investment:

1. Collect 100–300 production-like queries (or realistic drafts if pre-launch), stratified by language, document type, and query class.
2. Label relevant items per query. Even graded labels on the top candidates from a quick baseline beat no labels.
3. Pick one general-purpose model as the baseline, using the model's documented query/document formatting exactly (many models require distinct query vs. document instructions or prefixes — inconsistent application quietly degrades quality).
4. Measure recall@k, MRR or NDCG, p95 latency, embedding cost, and index size. Break results out by language and query class — aggregates hide per-slice failures.

**On metrics and normalization:** use the similarity metric the model documents. For most modern text-embedding models, normalize vectors and use cosine (equivalently, dot product on unit vectors). Whatever you choose, the index metric and query-time computation must agree — a cosine-trained model behind a raw-dot-product index is a classic silent quality bug.

---

## Step 3 — Improve the Representation Before Changing Models

Most "bad embeddings" are bad inputs. In order of typical payoff:

1. **Embed coherent units.** Chunks should be self-contained thoughts, not arbitrary token windows. A chunk whose meaning depends on unseen context embeds to a vague vector (see `advise-rag` for chunking, including contextual enrichment).
2. **Respect the context limit.** Text beyond the model's limit is silently truncated — often deleting exactly the relevant part. Split or summarize instead.
3. **Keep metadata out of the vector, in the record.** Title, section, entity, timestamp, permissions, and source belong as separate fields for filtering and display; concatenating them into embedded text pollutes similarity.
4. **Pair dense with lexical retrieval for exact tokens.** Embeddings generalize meaning; they are unreliable for product codes, error strings, and names. Hybrid dense+BM25 is the standard fix, not a bigger embedding model.
5. **Never mix vector spaces.** Any change to model, dimensions, normalization, or preprocessing requires re-embedding the full corpus and rebuilding the index. Mixed spaces produce plausible-looking nonsense rankings.

Only after these are clean, run the model bake-off: hold preprocessing, chunking, formatting, index settings, and reranking fixed; vary only the model. Prefer a general model by default; choose multilingual or multimodal models only when those inputs are real requirements; consider domain fine-tuned embeddings only after a general baseline demonstrably fails on a sufficient, clean eval set.

---

## Step 4 — Control Dimensions and Cost Deliberately

Lower dimensions cut storage, memory, transfer, and search latency roughly linearly — and can cost retrieval quality. Decide with the same labeled eval, not intuition:

- Providers expose shortened dimensions (e.g., OpenAI's `dimensions` parameter); models trained with Matryoshka Representation Learning are designed to truncate gracefully. Measure recall@k at each candidate dimension and pick the knee of the curve.
- Quantization (int8, binary) and ANN index settings trade recall for resources at the *index* layer; evaluate them jointly with the embedding choice, since a strong model can mask a lossy index and vice versa. See `advise-vector-db` for index selection.
- Compare models at equal settings only — different chunking or reranking between candidates invalidates the comparison.

Budget check: vectors × dimensions × 4 bytes (float32) is your baseline memory footprint; at tens of millions of vectors, dimension choice dominates infrastructure cost.

---

## Step 5 — Plan Migrations Like Schema Changes

Embedding models are versioned dependencies. When migrating: re-embed everything into a new index, shadow-test the new index on the eval set plus sampled live queries, cut over behind a flag, and keep the old index until the new one wins on metrics. Record the model ID, dimensions, normalization, and preprocessing version alongside every index so "which space is this vector in?" always has an answer.

Two migration triggers teams miss: provider deprecation notices (embedding models get retired — a corpus you cannot re-embed becomes stranded, so keep source text, not just vectors), and silent preprocessing drift (a tokenizer or cleaning change upstream shifts the effective input distribution; pin preprocessing versions with the index).

---

## Common Failure Modes and Fixes

| Symptom | Likely Cause | Fix |
|---|---|---|
| Relevant item never retrieved | Chunk lacks context or exceeded model limit | Fix chunking/enrichment first; then test stronger models |
| Similar-but-wrong items rank high | Symmetric similarity where task is asymmetric; missing filters | Use documented query/doc instructions; add metadata filters, hybrid retrieval, reranking |
| Exact codes/names not found | Dense-only retrieval | Add lexical (BM25) leg and fuse rankings |
| Quality varies wildly by language | Monolingual model on multilingual data | Use a verified multilingual model; keep per-language eval slices |
| Rankings became nonsense after upgrade | Mixed vector spaces | Full re-embed + rebuild; version the space |
| Great benchmark model, mediocre in prod | Domain mismatch with leaderboard tasks | Trust your labeled eval over aggregate MTEB scores |

---

## References

- **Eval-set construction, bake-off protocol, and migration checklist:** read [embedding-evaluation.md](references/embedding-evaluation.md) when running a model comparison or migration.
- **Verified sources with claims and caveats:** read [source-map.md](references/source-map.md) when citing evidence or re-checking provider-specific parameters.
