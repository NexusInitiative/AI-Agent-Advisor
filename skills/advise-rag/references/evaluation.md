# RAG Evaluation

Evaluation is the part of RAG most teams skip until something goes wrong in production. Set up measurement before you optimize — otherwise you're flying blind.

---

## The Two Layers of RAG Evaluation

RAG has a retrieval component and a generation component. They fail independently and require different metrics. Evaluate both.

```
Query → [Retrieval] → Retrieved Context → [Generator] → Answer
          ↑                                    ↑
   Retrieval metrics                   Generation metrics
```

A common mistake: good retrieval + bad generation → hallucination. Bad retrieval + good generation → hallucination or refusal. You need to know which component is failing.

---

## Retrieval Metrics

### Context Precision

Of the chunks returned in the top-K, what fraction are actually relevant to the query?

- High precision: few irrelevant chunks passed to the generator
- Low precision: generator has to ignore noise; "Lost in the Middle" effects degrade generation

### Context Recall

Of all relevant chunks in the entire corpus, what fraction were retrieved?

- High recall: the answer exists in the retrieved context
- Low recall: the answer was in the corpus but wasn't retrieved; generation will hallucinate or refuse

### NDCG (Normalized Discounted Cumulative Gain) and MRR (Mean Reciprocal Rank)

Rank-aware metrics: relevant chunks appearing earlier in the retrieved list score higher than relevant chunks appearing later. Use these when the order of retrieved chunks matters (which it does — see "Lost in the Middle").

### How to Compute Retrieval Metrics

You need relevance judgments: for a set of queries, which chunks are relevant? Options:

1. **Human annotation:** Most accurate; expensive and slow
2. **Synthetic queries from chunks:** Use an LLM to generate questions that each chunk would answer; use those as your eval set (ARES approach)
3. **RAGAS context metrics:** Estimate relevance using an LLM judge directly — no human labels required, but introduces LLM judge bias

---

## Generation Metrics

### Faithfulness (RAGAS)

Does the generated answer contradict or fabricate information not present in the retrieved context?

- Decompose the answer into individual claims
- For each claim, check whether it is supported by the retrieved context
- Faithfulness = supported claims / total claims

This is your primary hallucination metric. Low faithfulness means the model is generating beyond what the context supports.

### Answer Relevance (RAGAS)

Does the generated answer actually address the question asked?

- High answer relevance: the answer directly addresses the query
- Low answer relevance: the answer is technically faithful but doesn't answer what was asked (common when the generator pivots to something easier to answer from context)

### RAGTruth Hallucination Taxonomy

The RAGTruth corpus (Wu et al., 2024) categorized hallucinations in RAG outputs into three types:

1. **Unsupported additions:** The answer adds facts not present in the retrieved context (most common)
2. **Contradictions:** The answer directly contradicts the retrieved context
3. **Numerical errors:** Numbers, dates, or quantities are wrong even when the text is correct

Instrument your eval to specifically track these three patterns. Unsupported additions are often subtle and hard to catch with simple string matching — use an LLM judge with explicit instructions to check for each type.

---

## Automated Evaluation Frameworks

### RAGAS

**Paper:** Es et al., "RAGAS: Automated Evaluation of Retrieval Augmented Generation" (2023) — https://arxiv.org/abs/2309.15217

**What it provides:**
- Faithfulness, Answer Relevance, Context Precision, Context Recall
- Reference-free: no ground-truth answers required
- Computes metrics using an LLM judge over the (query, retrieved context, generated answer) triple

**Strengths:** Easy to integrate; widely used; no manual labeling needed for generation metrics  
**Weaknesses:** Inherits LLM judge biases; metrics are estimates, not ground truth

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall

results = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
```

### ARES

**Paper:** Saad-Falcon et al., "ARES: An Automated Evaluation Framework for Retrieval-Augmented Generation Systems" (2023) — https://arxiv.org/abs/2311.09476

**What it provides:**
- Generates synthetic training data from your corpus
- Fine-tunes lightweight classifier judges on that synthetic data
- Produces confidence intervals on evaluation results (statistical rigor RAGAS lacks)

**When to prefer ARES over RAGAS:** When you need statistical confidence on your eval results; when you can invest in building domain-specific synthetic datasets; when you want judges that don't rely on GPT-4.

---

## LLM-as-Judge: Benefits and Biases

All automated RAG evaluation ultimately relies on an LLM to judge quality. Know the biases before you trust the scores.

### G-Eval

**Paper:** Liu et al., "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment" (2023) — https://arxiv.org/abs/2303.16634

G-Eval uses chain-of-thought prompting + form-filling to get GPT-4 to evaluate generated text quality. Key finding: LLM judges correlate better with human judgments when given explicit rubrics and step-by-step evaluation instructions vs. direct scoring.

**How to use G-Eval for RAG:** Define explicit scoring rubrics for each dimension (faithfulness, relevance, completeness). Ask the judge to reason step-by-step before assigning a score. Score on a numeric scale (1–5) rather than binary.

### Known Judge Biases (MT-Bench and Chatbot Arena)

**Paper:** Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (2023) — https://arxiv.org/abs/2306.05685

Key findings:
- **Position bias:** LLM judges favor responses presented first in pairwise comparison, regardless of quality
- **Verbosity bias:** Longer responses score higher independent of actual quality or correctness
- **Self-enhancement bias:** Models tend to rate their own outputs higher

**Mitigations:**
- Always randomize option order in pairwise evaluations; average scores across both orderings
- Use reference-anchored scoring (score against a known-good reference) rather than relative pairwise comparison when possible
- Penalize verbosity explicitly in your rubric: "Do not give higher scores to longer responses unless length is justified by the content"
- Use rubric-based absolute scoring rather than pairwise preference when you need to track progress over time

### Prometheus 2

**Paper:** Kim et al., "Prometheus: Inducing Fine-grained Evaluation Capability in Language Models" (2023) — https://arxiv.org/abs/2310.08491

Prometheus 2 is an open-source evaluator model fine-tuned specifically for quality assessment using custom rubrics. It achieves near-GPT-4-judge performance without requiring an OpenAI API dependency.

**Use Prometheus 2 when:** You need open-source evaluation (cost, data privacy, or reliability concerns); your rubrics are domain-specific and benefit from a fine-tuned evaluator.

---

## Minimum Viable Eval Setup

Before shipping any RAG system:

### Eval Dataset
- 50–100 representative queries from actual or expected user queries
- Include edge cases: short factual queries, long analytical queries, queries the corpus can't answer
- Label expected answers for at least 20–30 of them (for faithfulness calibration)

### Retrieval Eval
- Run your 50–100 queries through retrieval
- For each query: rate top-5 retrieved chunks as relevant / not relevant (or use RAGAS context metrics)
- Record Context Precision and Context Recall
- Set a baseline; any pipeline change should maintain or improve these

### Generation Eval
- Run retrieved context + query through your generator for all 50–100 queries
- Score Faithfulness using RAGAS or manual review of a sample
- Check for RAGTruth hallucination patterns on failed cases

### Regression Test
- Run this eval suite on every meaningful change to chunking, retrieval, or generation
- Track metrics over time; alert on regressions above a threshold (e.g., > 5% drop in faithfulness)

---

## Diagnostic Questions When Metrics Are Bad

| Metric | Low Score | Diagnosis |
|---|---|---|
| Context Precision | < 0.6 | Retrieval returning irrelevant chunks; try hybrid search, better embeddings, reranking |
| Context Recall | < 0.7 | Relevant content not being retrieved; check chunking, add contextual retrieval |
| Faithfulness | < 0.8 | Generator hallucinating; add sufficiency check, reduce context noise, shorten chunks |
| Answer Relevance | < 0.8 | Generator pivoting to easier-to-answer content; check prompt instructions |

---

## Key Papers

- **RAGAS**: https://arxiv.org/abs/2309.15217
- **ARES**: https://arxiv.org/abs/2311.09476
- **RAGTruth**: https://aclanthology.org/2024.acl-long.585/
- **G-Eval**: https://arxiv.org/abs/2303.16634
- **MT-Bench / LLM-as-Judge**: https://arxiv.org/abs/2306.05685
- **Prometheus 2**: https://arxiv.org/abs/2310.08491
- **Lost in the Middle**: https://arxiv.org/abs/2307.03172
- **Sufficient Context**: https://arxiv.org/abs/2411.06037
