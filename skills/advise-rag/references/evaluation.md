# RAG Evaluation

Measure each stage separately, because retrieval and generation fail independently and a good final-answer score can hide a broken stage. Sources are in [source-map.md](source-map.md). This file deliberately gives no pass/fail thresholds: none of the cited work establishes a universal cutoff, so compare candidates against your own baseline with uncertainty.

## What to measure at each stage

| Stage | Question | Notes |
|---|---|---|
| Candidate retrieval | Is the evidence in the top-N candidates? | Needs labeled evidence; the failure point is FP2 in Barnett et al. |
| Selection and context assembly | Did the evidence survive reranking and the context budget? | FP3: retrieved but dropped before the generator |
| Generation | Are claims supported, complete, correctly formatted, and appropriately specific? | FP4 to FP7 |
| Citation | Were the cited sources supplied, and do they support the claim? | ALCE; Liu et al. |
| Abstention | When context is insufficient, does the system decline? | Sufficient Context |
| Whole system | Does the user get the right outcome at acceptable cost and latency? | Report with the counts behind each rate |

**Retrieval labels may mislead.** Salemi and Zamani found that evaluating a retriever against query-document relevance labels correlated only weakly with the RAG system's downstream performance. Their eRAG method instead scores each retrieved document by how well the generator answers with it alone, and achieved higher correlation with downstream performance (Kendall's tau improvements of 0.168 to 0.494 over baselines) while using up to 50 times less GPU memory than end-to-end evaluation. Practical reading: supplement relevance judgments with an answer-level check on whether the retrieved set lets the generator succeed.

## Hallucination taxonomy: RAGTruth

RAGTruth (ACL 2024) annotated nearly 18,000 naturally generated RAG responses at word level across question answering, data-to-text writing, and news summarization. It defines four types in two families:

- **Conflict:** *evident conflict* (direct contradiction of the provided information, easily verified, such as clear factual errors, misspelled names, or incorrect numbers) and *subtle conflict* (a departure that alters the contextual meaning, often by substituting terms with different implications or severity).
- **Baseless information:** *evident introduction of baseless information* (fabricated or hallucinated details lacking support) and *subtle introduction of baseless information* (inferred details, insights, or sentiments that go beyond the provided information and cannot be verified).

Baseless information was significantly more prevalent than conflict, especially in question answering, and the more severe "evident" forms made up a significant portion of both. In its strict RAG setting the authors also labeled true-but-unsupported statements as hallucinations. Instrument for both families, not just contradiction, and decide explicitly whether unsupported-but-true statements count as failures in your product. The paper notes one data-handling pitfall: some models read null values in structured data as false.

## Failure behaviors to test on purpose

- **Noise robustness, negative rejection, information integration, counterfactual robustness.** These are the four abilities the RGB benchmark (AAAI 2024) evaluates; the authors found models showed some noise robustness but struggled significantly with negative rejection, information integration, and false information.
- **Multi-hop queries.** MultiHop-RAG found existing RAG methods unsatisfactory on them; include multi-hop questions if your users ask them.
- **Insufficient context.** Sufficient Context found a high share of benchmark instances lacked sufficient context (55.4% on the Musique setup shown), and that models hallucinated more than they abstained.
- **Conflicting evidence.** ClashEval tested 1,294 questions across six domains with six models and found models adopted incorrect retrieved content, overriding correct prior knowledge, over 60% of the time; adoption fell as the content deviated more from the truth and rose when the model was less confident in its prior.
- **Noisy or adversarial documents.** Include injected-instruction and poisoned-document cases (see the security step in the main skill).

## Automated frameworks

- **RAGAS** (Es et al., 2023) defines three reference-free metrics: *faithfulness* (claims in the answer inferable from the context), *answer relevance* (the answer addresses the question), and *context relevance* (the context contains only what is needed). It validated them against human judgments on a dataset it introduced (WikiEval). The RAGAS library documents additional metrics; treat library metric definitions as implementation-specific.
- **ARES** (NAACL 2024) generates synthetic training data, fine-tunes lightweight LM judges for context relevance, answer faithfulness, and answer relevance, and uses prediction-powered inference with a small set of human-annotated points to correct judge errors; the authors report accurate evaluation using only a few hundred human annotations.
- **RAGChecker** (Ru et al., preprint) provides fine-grained diagnostic metrics for both retrieval and generation modules and reports better correlation with human judgments than other metrics it compared.
- A survey of RAG evaluation (Yu et al.) catalogs retrieval and generation metrics and benchmark limitations.

All of these rely on LLM judges or learned classifiers, so validate them on a sample of your own outputs rather than treating scores as ground truth.

## LLM-judge cautions

Judges show position, verbosity, and self-enhancement bias and limited reasoning ability (Zheng et al., NeurIPS 2023 Datasets and Benchmarks); position bias varies by judge and by the quality gap between answers (Shi et al.). In the GraphRAG comparison by Han et al., LLM-judged summarization was highly sensitive to the order in which candidate summaries were presented. Swap and average answer order, pin the judge version and rubric, and spot-check disagreements with a human.

## Dataset and sample size

Sample real user questions, add questions the corpus cannot answer, and label expected evidence for a subset so you can score retrieval. Do not use a fixed count as a launch criterion: no cited source establishes one. Instead, report standard errors and use paired comparisons between candidates on the same questions, following Miller's treatment of evaluations as statistical experiments. Keep a protected held-out set; after repeated selection on one set, its estimates stop being valid for the reasons given in the adaptive data-analysis literature.

## Monitoring and regression

Barnett et al. conclude that validation of a RAG system is only feasible in operation and that RAG systems require continuous calibration. Rerun the evaluation after any change to chunking, the embedding model, the index, retrieval parameters, or the generator, and keep per-stage metrics so a regression can be assigned to a stage. When metrics move, look at actual failing examples before changing anything; use `advise-debug` for the symptom-to-fix recipes.
