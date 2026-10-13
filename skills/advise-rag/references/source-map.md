# Source Map

Papers were checked against their abstracts and, wherever a figure or definition is quoted, against the full text; documentation and engineering posts were re-read on October 13, 2026. Venues are named only where the paper itself states one; otherwise the entry is an arXiv preprint. Rows tagged *(procedure)* are workflow recommendations grounded in the cited findings; *(heuristic)* marks a design heuristic that has not been benchmarked; *(derived)* marks a logical consequence. Vendor-reported numbers are marked as such.

## Diagnosis and baselines

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Seven RAG failure points (missing content, missed top-ranked documents, not in context, not extracted, wrong format, incorrect specificity, incomplete); validation is only feasible in operation; robustness evolves; RAG systems need continuous calibration; adding file name and chunk number to retrieved context helped the reader. | [Seven Failure Points When Engineering a RAG System](https://arxiv.org/abs/2401.05856) (CAIN 2024) | High | Lessons from three case studies; qualitative and small-scale. |
| Naive RAG indexes chunks, retrieves top-k, and generates; Advanced and Modular RAG extend it. | [RAG for LLMs: A Survey](https://arxiv.org/abs/2312.10997) | Medium | Survey (marked ongoing work); taxonomy, not a benchmark. |
| Three-way probe (closed-book, gold evidence, retrieved) to localize the stage *(procedure)*. | Grounded in the failure-point catalogue above and in [Anthropic: Demystifying evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | Medium | A controlled substitution; a probe suggests a stage, it does not prove a single cause. |
| Chunk size matters: faithfulness and relevancy were highest at 256 and 512 tokens and lowest at 2048 on one 60-page document with about 170 generated queries; hybrid search with HyDE recommended as default retrieval; query rewriting and decomposition did not improve retrieval as much; monoT5 recommended for reranking. | [Searching for Best Practices in RAG](https://arxiv.org/abs/2407.01219) | Medium | Preprint; small test with LLM-computed metrics; treat as a first sweep, not a rule. |
| 20 chunks outperformed 5 or 10; more information can distract the model; a knowledge base under about 200,000 tokens can go in the prompt. | [Anthropic: Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval) | Medium | Vendor-reported, own datasets and models; guidance, not a controlled study. |

## Long context versus retrieval

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Long context outperformed RAG on average when resourced (3.6% to 13.1% across three models) while RAG cost less; Self-Route cut cost by 39% to 65%; RAG and long-context predictions were identical for over 60% of queries. | [Retrieval Augmented Generation or Long-Context LLMs?](https://arxiv.org/abs/2407.16833) (EMNLP 2024 industry track) | High | Three 2024 models and public datasets. |
| Long context generally outperformed RAG on QA benchmarks (especially Wikipedia-based), summarization-based retrieval performed comparably, chunk-based lagged, and RAG had advantages for dialogue and general questions. | [Long Context vs. RAG for LLMs: An Evaluation and Revisits](https://arxiv.org/abs/2501.01880) | Medium | Preprint. |
| Models that claim 32K or more context often fail to maintain satisfactory performance at 32K on harder tasks (only half of 17 tested did), despite near-perfect needle-in-a-haystack scores. | [RULER](https://arxiv.org/abs/2404.06654) (COLM 2024) | High | Synthetic tasks; 2024 models. |
| Performance grew less reliable with longer inputs even on simple tasks across 18 models. | [Chroma: Context Rot](https://www.trychroma.com/research/context-rot) (July 14, 2025) | Medium | Technical report, not peer reviewed. |

## Retrieval

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| BM25 is a robust zero-shot baseline; re-ranking and late-interaction models were best on average at high computational cost; dense and learned-sparse models often underperformed out of domain. | [BEIR](https://arxiv.org/abs/2104.08663) (NeurIPS 2021 Datasets and Benchmarks) | High | 2021 models; 18 datasets. |
| An exact-string query such as an error code can be matched by BM25 and missed by embeddings. | [Anthropic: Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval) | Medium | Vendor illustration, not a measurement. |
| Dense Passage Retrieval encodes queries and passages with a bi-encoder. | [DPR](https://arxiv.org/abs/2004.04906) (EMNLP 2020) | High | Definition of the method. |
| The number of distinct top-k sets a single-vector embedding can return is limited by its dimension; state-of-the-art models fail on the LIMIT dataset. | [On the Theoretical Limitations of Embedding-Based Retrieval](https://arxiv.org/abs/2508.21038) (ICLR 2026) | High | Applies to single-vector retrieval; multi-vector and sparse approaches differ. |
| RRF hybrid outperformed pure-lexical and pure-semantic retrieval on most datasets and was particularly effective out of domain; RRF was sensitive to its parameters and a tuned RRF generalized poorly out of domain; a convex combination (one parameter, sample efficient) outperformed RRF on NDCG on every dataset tested. | [An Analysis of Fusion Functions for Hybrid Retrieval](https://arxiv.org/abs/2210.11934) | High | Preprint; datasets and retrievers they evaluated. |
| `rank_constant` defaults to 60 and RRF "requires no tuning". | [Elastic: Reciprocal rank fusion](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) | Medium | Product documentation that disagrees on tuning with the analysis above; version-sensitive. |
| Adding BM25 to contextual embeddings cut top-20 failures from 3.7% to 2.9%; reranking 150 candidates to 20 cut them to 1.9%. | [Anthropic: Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval) | Medium | Vendor-reported; averaged over codebases, fiction, ArXiv and science papers with Gemini Text 004 embeddings and a Cohere reranker. |
| ColBERT scores with token-level late interaction; ColPali embeds page images and largely outperformed text-extraction retrieval pipelines on ViDoRe. | [ColBERT](https://arxiv.org/abs/2004.12832) (SIGIR 2020), [ColPali](https://arxiv.org/abs/2407.01449) (ICLR 2025) | High | The authors' own benchmark. |
| HyDE outperformed an unsupervised dense retriever and approached fine-tuned retrievers; query rewriting improved open-domain QA. | [HyDE](https://arxiv.org/abs/2212.10496), [Query Rewriting for Retrieval-Augmented LLMs](https://arxiv.org/abs/2305.14283) (EMNLP 2023) | Medium | Authors' benchmarks; Wang et al. found rewriting and decomposition less helpful. |

## Chunking and indexing

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Contextual Retrieval: top-20 failure rate 5.7% to 3.7% (contextual embeddings), 2.9% (with BM25), 1.9% (with reranking); 50–100 tokens of context per chunk; about $1.02 per million document tokens with prompt caching under stated assumptions. | [Anthropic: Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval) | Medium | Vendor-reported; cost depends on chunk and document sizes and current prices. |
| Semantic chunking's extra cost was not justified by consistent gains over fixed-size chunking. | [Is Semantic Chunking Worth the Computational Cost?](https://arxiv.org/abs/2410.13070) | Medium | Preprint; three retrieval-related tasks. |
| Late chunking embeds the whole document first and pools per chunk, improving retrieval without extra LLM calls; needs a long-context embedding model. | [Late Chunking](https://arxiv.org/abs/2409.04701) | Medium | Preprint. |
| Proposition-level units outperformed passages in dense retrieval and improved QA at a fixed budget. | [Dense X Retrieval](https://arxiv.org/abs/2312.06648) | Medium | Preprint. |
| A tree of recursive summaries improved long-document QA (+20% absolute on QuALITY with GPT-4). | [RAPTOR](https://arxiv.org/abs/2401.18059) | Medium | Preprint; authors' benchmarks. |
| Structure-aware splitting (by function, row, clause) preserves the unit a query refers to *(heuristic)*. | None; compare with fixed-size chunking as in the semantic-chunking study above | Low | Not benchmarked here; test on your queries. |
| Upgrading an embedding model forces recomputing all stored vectors ("backfilling") unless the new features are trained to be compatible with the old. | [Towards Backward-Compatible Representation Learning](https://arxiv.org/abs/2003.11942) (CVPR 2020) | Medium | Image-retrieval features; used as an analogy for text embeddings. |

## Context assembly and generation

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Quality first rose and then fell as retrieved passages increased with a strong retriever; hard negatives from stronger retrievers can mislead more than weaker ones; retrieval reordering helps without training. | [Long-Context LLMs Meet RAG](https://arxiv.org/abs/2410.05983) | Medium | Preprint; the weak BM25 retriever showed a continued increase or slight decrease. |
| Accuracy is highest for information at the beginning or end of the context and lowest in the middle. | [Lost in the Middle](https://arxiv.org/abs/2307.03172) (TACL) | High | Earlier models; test placement on yours. |
| Retrieval can lower accuracy; an NLI filter prevented the drop but discarded relevant passages; fine-tuning on mixed relevant and irrelevant contexts made models robust with as few as 1,000 examples. | [Making Retrieval-Augmented Language Models Robust to Irrelevant Context](https://arxiv.org/abs/2310.01558) | Medium | Preprint; five open-domain QA benchmarks. |
| Training with distractor documents (and cited verbatim evidence) improved in-domain RAG. | [RAFT](https://arxiv.org/abs/2403.10131) | Medium | Preprint; PubMed, HotpotQA, Gorilla datasets. |
| Strong models often answered rather than abstained when context was insufficient; adding context reduced abstention; selective generation raised the correct share of answered questions by 2–10%; 55.4% of instances in the Musique setup shown had insufficient context. | [Sufficient Context](https://arxiv.org/abs/2411.06037) (ICLR 2025) | High | Specific datasets and models. |
| Models overrode their own correct prior answers over 60% of the time when retrieved content was wrong (1,294 questions, six domains, six LLMs); adoption rose as prior confidence fell and fell as the content deviated more from the truth. | [ClashEval](https://arxiv.org/abs/2404.10198) (NeurIPS 2024 Datasets and Benchmarks) | High | Benchmark of perturbed documents. |
| 51.5% of sentences were fully supported by citations and 74.5% of citations supported their sentence in four generative search engines; even the best models lacked complete citation support about 50% of the time on ELI5. | [Evaluating Verifiability in Generative Search Engines](https://arxiv.org/abs/2304.09848) (Findings of EMNLP 2023), [ALCE](https://arxiv.org/abs/2305.14627) (EMNLP 2023) | High | 2023 systems. |

## Advanced patterns

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Self-RAG trains a model to emit reflection tokens (Retrieve: yes/no/continue; IsRel: relevant/irrelevant; IsSup: fully/partially/no support; IsUse: 1–5) and outperformed ChatGPT and retrieval-augmented Llama2-chat on QA, reasoning and fact verification. | [Self-RAG](https://arxiv.org/abs/2310.11511) | High | Token definitions verified in the paper; requires training. |
| Adaptive-RAG routes by predicted query complexity; FLARE retrieves when upcoming content has low-confidence tokens. | [Adaptive-RAG](https://arxiv.org/abs/2403.14403) (NAACL 2024), [FLARE](https://arxiv.org/abs/2305.06983) (EMNLP 2023) | Medium | Authors' benchmarks. |
| CRAG scores retrieval and triggers Correct (refine), Incorrect (discard and web-search), or Ambiguous (combine both) actions. | [CRAG](https://arxiv.org/abs/2401.15884) | High | Action definitions verified in the paper; results on four datasets. |
| IRCoT improved retrieval by up to 21 points and QA by up to 15 points (GPT-3, four datasets); HippoRAG outperformed prior methods by up to 20%, with single-step retrieval matching or beating IRCoT at 10–30 times lower cost and 6–13 times higher speed; existing RAG methods were unsatisfactory on multi-hop queries. | [IRCoT](https://arxiv.org/abs/2212.10509) (ACL 2023), [HippoRAG](https://arxiv.org/abs/2405.14831) (NeurIPS 2024), [MultiHop-RAG](https://arxiv.org/abs/2401.15391) | Medium | Authors' benchmarks. |
| GraphRAG won 72–83% (podcast) and 72–80% (news) of LLM-judged comparisons on comprehensiveness against vector RAG, and 75–82% and 62–71% on diversity, at roughly 1–1.7 million tokens; empowerment was mixed; the abstract says baseline RAG fails on global questions and reports no near-zero scores. | [From Local to Global: A Graph RAG Approach](https://arxiv.org/abs/2404.16130) | High | Two datasets; LLM-judged win rates. |
| In the authors' legal-dataset comparison, GraphRAG's retrieval used about 610,000 tokens against under 100 tokens and one API call for LightRAG. | [LightRAG](https://arxiv.org/abs/2410.05779) | Medium | Self-reported on one dataset. |
| RAG and GraphRAG showed no consistent winner (RAG on single-hop and detail questions, GraphRAG on multi-hop); GraphRAG-based global search could lose detail; LLM-judged summarization showed strong position effects; GraphRAG significantly increased prompt length. | [RAG vs. GraphRAG](https://arxiv.org/abs/2502.11371), [GraphRAG-Bench](https://arxiv.org/abs/2506.05690) (ICLR 2026) | High | Independent evaluations on their benchmarks. |
| Agents used about 4 times and multi-agent systems about 15 times the tokens of a chat; token usage explained 80% of BrowseComp performance variance; multi-step search replaces static retrieval. | [Anthropic: Multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system) (June 13, 2025) | Medium | Vendor-reported for one workload. |
| Search-R1 improved results by 41% (Qwen2.5-7B) and 20% (Qwen2.5-3B) over RAG baselines under the same setting using reinforcement learning; an agentic RAG survey gives a taxonomy and open challenges. | [Search-R1](https://arxiv.org/abs/2503.09516), [Agentic RAG survey](https://arxiv.org/abs/2501.09136) | Medium | Preprints. |
| FiD obtained state-of-the-art results on Natural Questions and TriviaQA and improved significantly with more retrieved passages. | [FiD](https://arxiv.org/abs/2007.01282) | High | Encoder-decoder models; contrast with the long-context finding above. |

## Security

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Vector and embedding weaknesses include inadequate access controls, embedding inversion, and data poisoning; mitigations include fine-grained, permission-aware vector stores and logical partitioning. | [OWASP Top 10 for LLM Applications 2025, LLM08](https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/) | Medium | Industry standards document, not a study. |
| 92% of 32-token inputs were recovered exactly from their embeddings. | [Text Embeddings Reveal (Almost) As Much As Text](https://arxiv.org/abs/2310.06816) (EMNLP 2023) | High | Two embedding models; short inputs. |
| Injecting five malicious texts per target question into a corpus of millions achieved 90% attack success; several defenses were insufficient. | [PoisonedRAG](https://arxiv.org/abs/2402.07867) (USENIX Security 2025) | High | Attack under the paper's threat model. |
| Poisoning memory or a RAG knowledge base achieved over 80% average attack success at a poison rate below 0.1%. | [AgentPoison](https://arxiv.org/abs/2407.12784) | Medium | Preprint; three agent types. |
| Instructions injected into retrieved data can hijack LLM-integrated applications. | [Not what you've signed up for](https://arxiv.org/abs/2302.12173) | High | Demonstrated against real and synthetic applications. |

## Evaluation

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Query-document relevance labels correlated only weakly with downstream RAG performance; eRAG scored each retrieved document by generator success and correlated better (Kendall's tau up to 0.494 higher). | [Evaluating Retrieval Quality in RAG](https://arxiv.org/abs/2404.13781) | Medium | Preprint. |
| RAGTruth: nearly 18,000 annotated responses; four hallucination types (evident and subtle conflict; evident and subtle introduction of baseless information); baseless information was more prevalent than conflict, especially in QA. | [RAGTruth](https://arxiv.org/abs/2401.00396) (ACL 2024) | High | Three tasks, six models of 2023; type definitions verified in the paper. |
| RGB evaluates noise robustness, negative rejection, information integration and counterfactual robustness; models struggled significantly with negative rejection, integration and false information. | [Benchmarking LLMs in RAG](https://arxiv.org/abs/2309.01431) (AAAI 2024) | High | Six 2023 LLMs. |
| RAGAS defines faithfulness, answer relevance and context relevance without ground-truth annotations and validates them on WikiEval. | [RAGAS](https://arxiv.org/abs/2309.15217) | Medium | Preprint; metrics are LLM-computed; the library adds further metrics. |
| ARES fine-tunes lightweight LM judges on synthetic data and uses prediction-powered inference with a small human-annotated set (a few hundred annotations). | [ARES](https://arxiv.org/abs/2311.09476) (NAACL 2024) | High | Eight KILT/SuperGLUE/AIS tasks. |
| RAGChecker provides fine-grained diagnostic metrics and correlates better with human judgments than the other metrics compared. | [RAGChecker](https://arxiv.org/abs/2408.08067) | Medium | Preprint; eight RAG systems. |
| Survey of RAG evaluation metrics and benchmarks. | [Evaluation of Retrieval-Augmented Generation: A Survey](https://arxiv.org/abs/2405.07437) | Medium | Survey. |
| Judges show position, verbosity and self-enhancement bias; position bias varies with the judge and with the quality gap between answers. | [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685) (NeurIPS 2023 Datasets and Benchmarks), [Judging the Judges](https://arxiv.org/abs/2406.07791) (AACL-IJCNLP 2025) | High | Earlier models. |
| Treat evaluations as experiments with standard errors, paired differences and planned sample sizes; repeated adaptive reuse of a dataset breaks the assumption behind standard inference. | [Adding Error Bars to Evals](https://arxiv.org/abs/2411.00640), [Preserving Statistical Validity in Adaptive Data Analysis](https://arxiv.org/abs/1411.2664) | High | Method and theory papers; no fixed sample count is established by any cited source. |
