# Architecture Selection

Use this file to pick the least complex architecture that fixes a failure you have measured. Evidence and caveats are in [source-map.md](source-map.md). Costs below come from vendor or author reports on specific workloads; recompute them for yours.

## Start by asking whether retrieval is needed

| Option | When the evidence favors it | What to measure |
|---|---|---|
| Put the corpus in the prompt | Small corpora: Anthropic says a knowledge base under about 200,000 tokens (about 500 pages) can be included directly, and prompt caching makes that cheaper and faster | Answer quality, cost per query with and without caching, freshness |
| Long-context model over the corpus | Z. Li et al. (EMNLP 2024 industry track): long context outperformed RAG on average when resourced, by 3.6% to 13.1% across three models. X. Li et al. (2025 preprint): long context generally outperformed RAG on QA benchmarks, especially Wikipedia-based questions, while summarization-based retrieval performed comparably | Quality on your questions, token cost, latency |
| RAG | Lower cost than long context (Z. Li et al.); X. Li et al. found RAG advantageous for dialogue-based and general-question queries | Candidate recall, final-context evidence recall, answer quality |
| Route between them | Self-Route let the model decide from retrieved context whether to answer or escalate to long context, cutting cost 39% to 65% at comparable performance; the two methods gave identical predictions for over 60% of queries | Routing accuracy, cost, quality at your traffic mix |

Long-context questions are also quality questions, not just capacity ones: RULER found that although models claimed 32K or more tokens of context, only half of those tested maintained satisfactory performance at 32K, and Chroma's Context Rot report (a technical report, not peer reviewed) found performance grew less reliable as inputs lengthened even on simple tasks. Test long context on realistic tasks before concluding it replaces retrieval.

## Match the architecture to the measured failure

| What you measured | Try first | Escalate to | Do not use when |
|---|---|---|---|
| Right document exists but is not retrieved | Contextual retrieval, hybrid search, reranking | Query rewriting or HyDE (test per query type); late-interaction or visual retrieval for layout-heavy pages | The evidence is not in the corpus at all (FP1); retrieval changes cannot help |
| Retrieval fine, answers ignore evidence or add claims | Fewer, better-ordered passages; abstention rule; sufficiency check | Fine-tuning for distractor robustness (Yoran et al.; RAFT) | You have no labeled failures to train on |
| Easy and hard queries both hurt by one fixed pipeline | Route by complexity | Adaptive-RAG classifier, Self-RAG, or FLARE | Almost all queries need the same retrieval |
| Corpus incomplete or retrieval unreliable | Sufficiency check with abstention | CRAG with a search fallback | No permitted external search |
| Multi-hop questions fail | Query decomposition tested against a baseline | IRCoT iterative retrieval; HippoRAG | Questions are single-passage |
| "Summarize themes across the corpus" fails | Hierarchical summaries (RAPTOR) | GraphRAG or LightRAG | Questions are local factual lookups; corpus changes constantly |
| Open-ended research needs many searches | A multi-step retrieval loop with a hard step budget | Multi-agent search | The task value does not justify roughly 15 times chat tokens |

## Cost reality check

- **Graph indexes.** GraphRAG spends LLM calls to extract entities and summarize communities at index time; independent benchmarking found GraphRAG significantly increases prompt length compared with vanilla RAG. LightRAG's authors report much cheaper retrieval on their dataset, which is self-reported.
- **Agentic search.** Anthropic reports about 4 times chat tokens for an agent and about 15 times for multi-agent systems, and that token usage explained 80% of performance variance on BrowseComp. More spend bought more performance there, so decide whether the task is worth it.
- **Contextual chunking.** Anthropic estimated $1.02 per million document tokens with prompt caching under its stated assumptions; a one-time indexing cost.
- **Reranking.** BEIR found the best zero-shot systems were re-ranking and late-interaction models, at high computational cost; the latency you pay depends on candidate count and model, so measure it.

## Avoid these inferences

- A paper's win on its benchmark is not a win on your corpus: Han et al. found no consistent winner between RAG and GraphRAG, and the GraphRAG-Bench authors note that recent studies report GraphRAG frequently underperforming vanilla RAG on real-world tasks.
- Adding more retrieved passages is not a free recall boost (Jin et al.).
- LLM-judged comparisons can be confounded by presentation order (Han et al. observed strong position effects in summarization judging); swap order when you compare architectures.
