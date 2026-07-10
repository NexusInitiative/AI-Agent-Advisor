---
name: advise-embedding
description: |
  This skill should be used when the user asks to "advise on embeddings", "what embedding model should I use",
  "help with embedding strategy", "how do I create good embeddings", "text embedding guidance",
  "which similarity metric should I use", "should I normalize embeddings", "why is semantic search bad",
  or needs guidance on embedding models, indexing inputs, dimensions, or retrieval evaluation.
---

# Embedding Advisor

Choose an embedding model against the actual retrieval or similarity task, language mix, modalities, latency, privacy, and storage budget. Do not choose the top aggregate benchmark score without checking the benchmark's task and domain match.

## Establish a baseline

Create a small labeled set of production-like queries and relevant items. Start with the model's documented query/document formatting and recommended metric. For most modern text embeddings, normalize vectors when using cosine similarity; ensure the index metric and query-time calculation agree. Measure recall@k, MRR/NDCG, latency, embedding cost, index size, and failures by language, document type, and query class.

## Improve the representation before changing models

Embed coherent units, not arbitrary token windows. Preserve document title, section, entity, time, permissions, and source metadata separately for filtering and display. Use model-supported context limits; truncation can silently erase the relevant part. If the model distinguishes query and document instructions, apply them consistently. Re-embed the full corpus when model, dimensions, normalization, or preprocessing changes; never mix incompatible vector spaces.

Use a general model as the default. Prefer multilingual or multimodal models only when those inputs are real requirements. Consider domain adaptation only after a general baseline fails on a sufficiently large, clean evaluation set. For exact identifiers, codes, and names, pair dense embeddings with lexical retrieval rather than expecting embeddings to replace keyword search.

## Control dimension and cost

Lower dimensions reduce storage, memory, transfer, and search cost but can reduce retrieval quality; select them with the same labeled evaluation. Quantization and approximate search are index decisions and must be evaluated jointly with the embedding model. Do not compare models at unequal preprocessing, chunking, or retrieval settings.

## Troubleshoot

| Symptom | Likely fix |
|---|---|
| Relevant item never appears | Improve chunking/context, inspect labels, then test a better model |
| Similar but wrong items rank high | Add metadata filters, hybrid retrieval, or reranking |
| Results vary by language | Use a verified multilingual model and per-language evals |
| Index migration breaks results | Re-embed and rebuild rather than mixing dimensions/models |

For retrieval architecture see `advise-rag`; for storage/index selection see `advise-vector-db`.

## Sources

- [MTEB paper](https://aclanthology.org/2023.eacl-main.148/)
- [MTEB documentation](https://docs.mteb.org/)
- [OpenAI embeddings guide](https://platform.openai.com/docs/guides/embeddings)
