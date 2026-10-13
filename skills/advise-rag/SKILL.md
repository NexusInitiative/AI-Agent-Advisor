---
name: advise-rag
description: |
  This skill should be used when the user asks to "help me design my RAG pipeline",
  "what chunking strategy should I use", "my retrieval results are bad",
  "should I use dense or sparse retrieval", "how do I improve RAG accuracy",
  "help me pick a retrieval approach", "why is my RAG hallucinating",
  "when should I use GraphRAG", "how do I evaluate my RAG system",
  "my retrieved chunks aren't relevant", "should I use hybrid search",
  "do I need RAG or just a long context window", "should I use agentic RAG",
  or needs guidance on building, improving, or evaluating a retrieval-augmented generation
  system. When answers are wrong and the failing component is unknown, use advise-debug.
---

# RAG Advisor

**Find the failing stage, fix that stage, and add architecture only for a failure you measured.** RAG systems fail in distinguishable places; a team that cannot say which place has nothing to optimize.

## Step 1 — Diagnose before designing

Ask or infer:

- **Data:** source formats (PDF, code, HTML, tables), change rate, size, structure.
- **Queries:** keyword-heavy (codes, error strings, names) or conceptual; one passage or synthesis across documents or hops; short or analytical.
- **Failure to avoid:** hallucination, missed context, irrelevant retrievals, latency or cost, or leakage between users.

Then name the failing stage. A study of three RAG case studies catalogued seven failure points: missing content (FP1), the answer's document not ranked high enough (FP2), retrieved but dropped before the context (FP3), in context but not extracted (FP4), wrong format (FP5), wrong specificity (FP6), and incomplete answers (FP7). Its authors conclude that validation is only feasible in operation and that robustness evolves rather than being designed in, so instrument each stage from the start.

To tell the stages apart, run the same failing questions three ways: closed-book, with human-selected gold evidence, and through your retriever. If gold evidence fixes the answer, the fault is retrieval or selection; if it does not, the fault is generation, the evidence, or the prompt. For symptom-first recipes across all components, use `advise-debug`.

## Step 2 — Baseline first, and test whether you need RAG at all

Naive RAG, as the Gao et al. survey describes it, indexes chunks, retrieves the top-k by embedding similarity, and generates. Treat chunk size and k as hyperparameters to sweep, not defaults: one best-practices study found 256–512-token chunks scored best on a single-document test, and Anthropic found 20 chunks beat 5 or 10 in its tests and noted that more information can distract the model.

Compare against a long-context baseline. Li et al. found long context outperformed RAG on average when resourced, while RAG cost less; Anthropic suggests a knowledge base under about 200,000 tokens can simply go in the prompt. Choose by measured quality, cost, and freshness, and consider routing (Self-Route cut cost by 39% to 65% at comparable quality). See [architecture-selection.md](references/architecture-selection.md).

## Step 3 — Choose retrieval

- **Keyword-heavy queries:** start with BM25. It was a robust zero-shot baseline in BEIR and finds exact strings, such as an error code, that embeddings can miss.
- **Conceptual queries:** dense retrieval, but note that BEIR found dense and learned-sparse models often underperformed out of domain, and that single-vector embeddings provably cannot return every possible top-k set (Weller et al., ICLR 2026).
- **Mixed traffic: hybrid.** RRF hybrid beat pure lexical and pure semantic retrieval on most datasets, notably out of domain (Bruch et al.), and adding contextual BM25 to contextual embeddings cut Anthropic's top-20 failure rate from 3.7% to 2.9%. Elastic defaults the RRF constant to 60 and says it needs no tuning, but Bruch et al. found a convex combination tuned on a small labeled set beat RRF on NDCG. Start with RRF, then test a tuned combination once you have labeled queries.
- **Reranking:** BEIR found re-ranking and late-interaction models best on average at high compute cost; Anthropic's rerank of 150 candidates down to 20 cut failures from 2.9% to 1.9%. Measure the latency you add.
- **Query transformation:** Wang et al. recommended hybrid search with HyDE as their default retrieval but found query rewriting and decomposition did not help retrieval as much; Ma et al. improved QA with a trained rewriter. Test per query type.

Details and a fusion sketch: [retrieval-architectures.md](references/retrieval-architectures.md).

## Step 4 — Fix chunking and indexing

- **Chunks lose context.** Contextual Retrieval prepends 50–100 tokens of LLM-written context to each chunk before embedding and BM25 indexing. On Anthropic's mixed-domain tests the top-20 failure rate fell from 5.7% to 3.7% with contextual embeddings, 2.9% with contextual BM25 added, and 1.9% with reranking. Late chunking adds context without LLM calls by embedding the whole document first, but needs a long-context embedding model.
- **Do not assume semantic chunking pays.** Qu et al. found its extra cost was not justified by consistent gains over fixed-size chunking.
- **Granularity matters.** Proposition-level units beat passage-level units in dense retrieval (Dense X), and a tree of recursive summaries lifted long-document QA by 20% absolute on QuALITY with GPT-4 (RAPTOR).
- **Layout-heavy PDFs:** ColPali embeds page images and outperformed text-extraction pipelines on its ViDoRe benchmark.
- **Carry metadata** (IDs, titles, sections, dates, versions). Barnett et al. found adding file name and chunk number helped; you also need it for filters, citations, and debugging.

Details: [chunking-and-indexing.md](references/chunking-and-indexing.md).

## Step 5 — Assemble context and constrain generation

- **More passages is not monotonically better.** With a strong retriever, quality rose and then fell as passages were added, and hard negatives from stronger retrievers could mislead more than those from weaker ones (Jin et al.). Retrieval reordering helped without training.
- **Position effects.** Accuracy was highest for information at the start or end of the context and lowest in the middle (Lost in the Middle, earlier models); test placement on your model.
- **Irrelevant context hurts.** Retrieval sometimes lowered accuracy; an NLI filter prevented the drop but discarded relevant passages, while fine-tuning on a mix of relevant and irrelevant contexts made models robust with as few as 1,000 examples (Yoran et al.). RAFT trains the same way with distractor documents.
- **Add a sufficiency check and permit abstention.** Models often answered rather than abstained when context was insufficient, and adding context reduced abstention; routing with a sufficiency signal raised the correct share of answered questions by 2–10% (Sufficient Context, ICLR 2025).
- **Retrieved text is not automatically right.** Models overrode their correct prior answers more than 60% of the time when the retrieved content was wrong (ClashEval).
- **Verify citations.** Check that cited sources were supplied and that they support the claim; audits found 51.5% of sentences fully supported and 74.5% of citations supporting their sentence (Liu et al.).

## Step 6 — Escalate architecture only for a measured failure

| Measured failure | Candidate | Evidence and caveat |
|---|---|---|
| Retrieval helps only some queries | Adaptive retrieval: Adaptive-RAG, Self-RAG, FLARE | Each reports gains over fixed retrieve-then-read; Self-RAG needs a trained model |
| Retrieved set wrong or corpus incomplete | CRAG: evaluator picks refine, discard-and-web-search, or both | Needs an evaluator and a search fallback |
| Multi-hop questions | Iterative retrieval (IRCoT) or graph-indexed HippoRAG | IRCoT gained up to 21 retrieval and 15 QA points; MultiHop-RAG found standard RAG unsatisfactory |
| Whole-corpus "themes" questions | GraphRAG community summaries | 72–83% LLM-judged win rate on comprehensiveness at ~1M-token corpora; independent studies found no consistent winner and higher prompt cost |
| Open-ended research needing many searches | Agentic multi-step search | Token use explained 80% of variance in Anthropic's analysis; about 15 times chat tokens |

Do not start here. Details and costs: [advanced-patterns.md](references/advanced-patterns.md).

## Step 7 — Secure the corpus

Enforce permissions at retrieval time, not after generation: OWASP lists inadequate access control and permission-unaware vector stores among vector and embedding weaknesses. Embeddings are not anonymization (92% of 32-token inputs were recovered exactly), a few poisoned documents can steer answers (90% attack success with five injected texts in a corpus of millions), and instructions inside retrieved text can hijack applications. Refer runtime controls to `advise-harness`.

## Step 8 — Evaluate by stage

Measure candidate recall, final-context evidence recall, answer correctness, claim support, citation support, and abstention separately. Conventional retrieval relevance labels correlated weakly with downstream RAG quality (eRAG), so include an answer-level check. RAGTruth classifies hallucinations as conflicts or baseless information, each evident or subtle; baseless information was more common. Stress-test noise robustness, negative rejection, information integration, and counterfactual robustness (RGB). Set sample sizes from uncertainty, not a fixed count. See [evaluation.md](references/evaluation.md).

## Common failures

| Symptom | Likely stage | First fix |
|---|---|---|
| Answer exists but is never retrieved | FP2: context lost in chunk, weak first-stage | Contextual retrieval, hybrid, rerank; measure candidate recall |
| Right chunks retrieved, answer ignores them | FP3/FP4: dropped at selection, or noise and hard negatives | Fewer, better passages; reorder; check selection |
| Fluent answer with no supporting evidence | FP1 or insufficient context | Sufficiency check and explicit abstention |
| Answer contradicts the sources | Knowledge conflict or baseless addition | Source gating, claim-level support check |
| Cross-document questions fail | Multi-hop or global question | Step 6 |

## References

- [retrieval-architectures.md](references/retrieval-architectures.md): sparse, dense, hybrid fusion, reranking, query transformation.
- [chunking-and-indexing.md](references/chunking-and-indexing.md): chunking evidence, metadata, re-indexing.
- [advanced-patterns.md](references/advanced-patterns.md): adaptive, corrective, multi-hop, graph, and agentic retrieval.
- [architecture-selection.md](references/architecture-selection.md): long context versus RAG and the escalation ladder.
- [evaluation.md](references/evaluation.md): stage-wise metrics, taxonomies, frameworks, sample sizing.
- [source-map.md](references/source-map.md): every claim above with its source, venue, and scope.
