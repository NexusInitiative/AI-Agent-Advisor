# Recipes: Retrieval and Grounding (R1–R8)

Each recipe gives the symptom, the test that discriminates between causes, causes ranked with fixes, how to verify, and what not to do. Sources are in [source-map.md](source-map.md); design depth lives in `advise-rag`. Items marked *(procedure)* are workflow steps rather than findings.

## R1. The answer is in the corpus, but the system answers wrongly or says it doesn't know

**Test.** For each failing question, check three things in order: was the answer-bearing chunk in the retrieved candidates, did it survive reranking and the context budget, and did the model use it? These are failure points FP2 (missed top-ranked documents), FP3 (not in context after consolidation), and FP4 (in context, not extracted) in Barnett et al.

**Causes and fixes.**

0. *Ingestion lost the answer (check first).* Open the parsed text of the answer-bearing page or table: if the number or sentence is garbled, split from its header, or missing, no retrieval change can help. Text-extraction pipelines for visually rich documents are described as lengthy and brittle, and embedding page images directly (ColPali) outperformed text-extraction retrieval pipelines on the ViDoRe benchmark; compare it with your parser on the failing pages.
1. *Not in the candidates (FP2).*
   - The chunk lost its context: contextual retrieval cut the top-20 failure rate from 5.7% to 3.7%, or 2.9% with contextual BM25 (Anthropic, vendor-reported); late chunking is a no-LLM alternative that needs a long-context embedding model.
   - Exact terms are missed by embeddings: add BM25 and fuse (hybrid beat pure lexical and pure semantic retrieval on most datasets in Bruch et al.).
   - Query wording is the problem: test HyDE or query rewriting, but note one comparison found rewriting and decomposition helped retrieval less than hybrid search with HyDE.
   - Many documents must be jointly relevant to arbitrary queries: single-vector embeddings have a dimension-bound limit on the top-k sets they can return (Weller et al.); add lexical, multi-vector, or reranking stages.
2. *Dropped before the context (FP3).* Candidate depth or the reranker cut-off is too tight. Anthropic reranked 150 candidates down to 20 and cut failures from 2.9% to 1.9%.
3. *In context, not used (FP4).* Noise or contradictions in the context are the cause Barnett et al. give. Quality can fall as passages are added, and hard negatives from a stronger retriever can mislead more than those from a weaker one (Jin et al.); reordering helped without training. Information in the middle of long contexts is used less (Lost in the Middle). Fine-tuning on mixed relevant and irrelevant contexts made models robust with about 1,000 examples (Yoran et al.).

**Verify.** Recompute candidate recall and final-context evidence recall on a labeled set, then answer correctness, using paired comparisons.

**Do not** swap the generator model before localizing the stage, and do not increase k blindly.

## R2. Confident answer when the corpus doesn't contain it

**Test.** Ask questions the corpus cannot answer (FP1) and check whether the system abstains. Classify whether the retrieved context is sufficient.

**Causes and fixes.**

1. *Models answer rather than abstain.* Strong models often gave incorrect answers instead of abstaining when context was insufficient, and adding context reduced abstention; in the Musique setup shown, 55.4% of instances had insufficient context (Sufficient Context, ICLR 2025). A sufficiency signal used to decide whether to answer raised the correct share of answered questions by 2–10%.
2. *The contract has no failure behavior.* Specify a parseable `NOT_FOUND` outcome and test it *(procedure; see `advise-prompting`)*.
3. *The corpus is incomplete.* CRAG scores retrieval and, when it judges it incorrect, discards it and falls back to web search; adopt only if external search is permitted.
4. *Evaluation incentives.* Benchmarks that reward guessing over acknowledging uncertainty push models to guess (Kalai et al.), so do not copy a guess-rewarding metric into your own eval.

**Verify.** Report correctness and coverage on answerable and unanswerable sets together, so abstaining cannot look better by declining hard questions.

**Do not** count "I don't know" as a success on answerable questions.

## R3. The answer contradicts or adds to the retrieved text

**Test.** Check each claim against the supplied context and classify it using RAGTruth: evident or subtle *conflict*, or evident or subtle *baseless information*.

**Causes and fixes.**

1. *Baseless additions* were more prevalent than conflicts, especially in question answering (RAGTruth). Require claims to be traceable to a supplied span, and test explicitly whether true-but-unsupported statements count as failures in your product.
2. *Prior versus context.* Models overrode correct priors with wrong retrieved content over 60% of the time, more often when less confident in the prior and less often when the content was implausible (ClashEval). If the context is wrong, fix the source: gating, freshness, and provenance. Knowledge conflicts can be context-memory, inter-context, or intra-memory (Xu et al. survey), so check which one occurs.
3. *Structured data misread.* Some models treated null as false in RAGTruth's data-to-text task; test null handling.

**Verify.** Claim-support rate and RAGTruth-type counts on the failing set before and after.

**Do not** rely on the model verifying itself with no new evidence. Sampling-consistency checks (SelfCheckGPT) and verification-question methods (Chain-of-Verification) are published options to test, not guarantees.

## R4. Multi-part, multi-document, or multi-hop questions fail

**Test.** Break the question into parts and check whether each needed fact is retrievable alone. Barnett et al. list incomplete answers as FP7 and suggest asking such questions separately.

**Causes and fixes.**

1. *What to retrieve depends on earlier steps.* Interleaving retrieval with reasoning (IRCoT) improved retrieval by up to 21 points and QA by up to 15 points on four multi-hop datasets; MultiHop-RAG found standard RAG unsatisfactory on multi-hop queries.
2. *Whole-corpus questions.* GraphRAG-style community summaries won 72–83% of LLM-judged comprehensiveness comparisons against vector RAG; RAPTOR's summary tree helped long documents. Independent studies found no consistent winner, with standard RAG better on single-hop detail questions.
3. *Too many passages* (see R1).

**Verify.** Evaluate on a multi-hop slice, not only the aggregate.

**Do not** adopt a graph index for single-passage lookup, where standard RAG did as well or better.

## R5. Stale or conflicting sources

**Test.** For each failing answer, list the retrieved chunks with document version and date, and check whether two chunks disagree.

**Causes and fixes.**

1. *Outdated documents remain indexed, or versions are mixed.* Store document version and date with every chunk (Barnett et al. found metadata helped the reader), supersede old versions on re-index, and make the preference rule explicit *(procedure)*.
2. *Inter-context conflict* is a recognized category (Xu et al.). Return a `CONFLICTING_EVIDENCE` status instead of letting the generator choose silently *(procedure)*.
3. *Rare facts depend on retrieval.* Accuracy on long-tail facts tracks how often they appear in pretraining data, and retrieval reduces that dependence (Kandpal et al.); do not expect the model's memory to cover stale-or-missing documents.

**Verify.** Add stale-versus-current pairs to the evaluation set, in the style of ClashEval's perturbed documents.

## R6. Citations are wrong or unsupported

**Test.** For every citation, check that the cited ID was supplied, then check that the cited passage supports the claim. ALCE measures citation recall (is the output entirely supported by its citations) and precision, using an NLI model to check entailment.

**Causes and fixes.** Citation quality is a distinct failure from answer correctness: audits found 51.5% of sentences fully supported by their citations and 74.5% of citations supporting their sentences in four generative search engines, and the best models lacked complete citation support about 50% of the time on ELI5. Use chunk IDs in the contract, verify membership in code, run an entailment check on high-stakes claims, and allow several citations for synthesized claims.

**Do not** treat the presence of a citation as evidence of support.

## R7. Another user's data appears, or injected text steers answers

**Test.** Query as user A for content only user B may see. Plant an instruction inside an indexed document and see whether behavior changes.

**Causes and fixes.**

1. *Permissions are not enforced at retrieval.* OWASP lists inadequate access controls among vector and embedding weaknesses and recommends permission-aware vector stores and logical partitioning. Filter before generation, not after.
2. *Embeddings are not anonymized.* 92% of 32-token inputs were recovered exactly from their embeddings (Morris et al.).
3. *Poisoned documents.* Five injected texts per target question achieved 90% attack success in a corpus of millions (PoisonedRAG); poisoning memory or a knowledge base reached over 80% average success at a poison rate under 0.1% (AgentPoison).
4. *Indirect prompt injection.* Instructions placed in retrieved data can hijack applications (Greshake et al.).

**Fix and verify.** Enforce authorization in the executor and retrieval layer (`advise-harness`), and keep these cases in the evaluation set.

**Do not** rely on delimiters or on telling the model to ignore instructions in documents.

## R8. Quality dropped after a re-index, embedding change, or chunking change

**Test.** Run the frozen evaluation set on the old and new index, paired, and compare candidate recall first.

**Causes and fixes.** The usual suspects, in order *(procedure)*: embeddings from two models mixed in one index (features from different models are not directly comparable unless trained to be backward-compatible, which is why model upgrades force backfilling); changed chunk boundaries that split answer spans; lost metadata or permission fields; a changed generator or model version (hosted-model behavior can change over time, per Chen et al.). Re-embed everything into a new index, shadow-test it, and keep the previous build for rollback. Barnett et al. conclude that RAG systems require continuous calibration, so rerun the evaluation after each such change.
