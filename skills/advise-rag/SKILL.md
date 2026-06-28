---
name: advise-rag
description: |
  This skill should be used when the user asks to "help me design my RAG pipeline",
  "what chunking strategy should I use", "my retrieval results are bad",
  "should I use dense or sparse retrieval", "how do I improve RAG accuracy",
  "help me pick a retrieval approach", "why is my RAG hallucinating",
  "when should I use GraphRAG", "how do I evaluate my RAG system",
  "my retrieved chunks aren't relevant", "should I use hybrid search",
  "how do I reduce RAG hallucinations", or needs guidance on building,
  improving, or debugging a retrieval-augmented generation system.
---

# RAG Advisor

## Step 1 — Diagnose Before Designing

Never recommend an architecture before you understand the problem. Ask or infer:

**About the data:**
- What is the source? (PDFs, code, databases, HTML, mixed formats?)
- How often does it change? (Static corpus vs. live updates)
- How large? (Thousands of documents vs. millions of chunks)
- Is it structured, semi-structured, or free prose?

**About the queries:**
- Are queries keyword-heavy (product codes, error strings, names) or conceptual ("how does X relate to Y")?
- Do queries require synthesizing across many documents, or finding a single passage?
- Are queries short and factual, or long and analytical?

**About the failure mode they most want to avoid:**
- Hallucination (generating facts not in the source)
- Missed context (right answer exists but retrieval doesn't surface it)
- Irrelevant retrievals (retrieval returns chunks that don't help)
- Latency (retrieval adds too much time)

The answers to these questions determine the architecture. Don't skip this step — the biggest RAG mistakes happen when teams choose an architecture before understanding what they're actually building.

---

## Step 2 — Start With the Naive RAG Baseline

Before adding complexity, establish a working baseline:

1. Chunk your documents (start with fixed-size: 512 tokens, ~10% overlap)
2. Embed chunks with a general-purpose embedding model
3. Store in a vector index
4. At query time: embed the query, retrieve top-5 chunks by cosine similarity, pass to the generator

This is "Naive RAG" as defined in the Gao et al. survey. It has known weaknesses — poor keyword matching, no retrieval quality check, context ordering problems — but it tells you whether retrieval is even your bottleneck. Most teams skip this and jump to hybrid search and rerankers, then can't tell what's actually helping.

**Run the baseline first. Measure it. Then improve what's actually broken.**

---

## Step 3 — Choose a Retrieval Architecture

Once you have baseline metrics, choose your retrieval approach based on query type:

**If queries are keyword-heavy** (error messages, product codes, proper nouns, exact strings):
- BM25 (sparse retrieval) often outperforms dense retrieval here
- The BEIR benchmark showed that no single retriever dominates across domains — sparse methods win on keyword-heavy tasks
- Start with BM25 as a baseline before adding dense retrieval

**If queries are conceptual or semantic** ("explain the relationship between X and Y", "what are the implications of Z"):
- Dense retrieval (DPR-style) wins — it matches meaning rather than tokens
- Use a strong embedding model; retrieval quality is bottlenecked by embedding quality

**For most production systems: use hybrid retrieval**
- Combine BM25 (sparse) and dense retrieval, then fuse rankings with RRF (Reciprocal Rank Fusion)
- RRF formula: score = Σ 1/(k + rank_i) where k=60 is standard — no training required
- Hybrid almost always outperforms either alone across diverse query types
- This is the default recommendation unless you have strong evidence your queries are uniformly keyword or uniformly semantic

See [retrieval-architectures.md](references/retrieval-architectures.md) for detailed comparison of dense, sparse, hybrid, and reranking options.

---

## Step 4 — Fix Chunking and Indexing

Chunking strategy has an outsized impact on retrieval quality and is frequently underinvested.

**The key insight from Anthropic's Contextual Retrieval work:** Standard chunking loses context. A chunk that says "The treatment was effective in 73% of cases" is meaningless without knowing what treatment, what condition, what study. Before embedding, prepend a short LLM-generated context summary to each chunk describing what document it came from and where it sits in the document's structure. Anthropic reported a 49% reduction in retrieval failures with this approach.

**Chunking decision tree:**
- Prose documents (articles, reports, books) → semantic chunking or contextual chunking
- Code → chunk by function/class boundary, not token count
- Structured data (tables, JSON) → row-level or entity-level chunks with structured metadata
- Mixed formats → chunk by document section first, then by token size within sections

**Always add metadata to chunks:** document title, section heading, page number, date, author, document type. This enables filtered retrieval and dramatically improves context assembly.

See [chunking-and-indexing.md](references/chunking-and-indexing.md) for chunking strategy details and trade-offs.

---

## Step 5 — Assemble Context Intelligently

Retrieval returning the right chunks is necessary but not sufficient. How you assemble them into the generator's context matters enormously.

**The Lost in the Middle finding:** LLMs systematically underuse information placed in the middle of long contexts. Performance is highest when relevant information is at the beginning or end of the context window. If you're concatenating 10 retrieved chunks, don't put the most relevant one in position 5.

**Ordering strategy:**
- Put the most relevant chunk first
- If using reranking, order by reranker score descending
- For long contexts: most relevant at top, second-most-relevant at bottom, filler in the middle

**Check if retrieved context is actually sufficient before generating.** The Sufficient Context paper frames this as a detection problem: does the retrieved context actually contain an answer? If not, generating will hallucinate. Add a lightweight sufficiency check — either a dedicated classifier or an LLM call asking "does this context contain enough information to answer this question?" — and fall back to a "I don't have enough information" response rather than hallucinating.

**FiD (Fusion-in-Decoder) insight:** When using multiple retrieved passages, generating while attending to all of them simultaneously outperforms feeding them one at a time. Most modern LLMs do this implicitly when you concatenate chunks in the prompt, but the ordering still matters.

---

## Step 6 — Escalate to Advanced Patterns Only When Warranted

Advanced RAG patterns add significant complexity. Only use them when the baseline + tuned retrieval is still insufficient.

**Use Self-RAG when:** retrieval quality is inconsistent and you need the model to decide when retrieval helps. Self-RAG trains the model to emit special tokens — retrieve/no-retrieve, and critique tokens (supported/not supported/unsure) — to adaptively retrieve and self-verify. Best for diverse query sets where some queries need retrieval and others don't.

**Use CRAG (Corrective RAG) when:** retrieval confidence is low or the corpus is incomplete. CRAG adds a retrieval quality evaluator; if the score is below a threshold, it falls back to web search or broader retrieval before generating. Particularly useful when your document corpus doesn't cover the full question space.

**Use GraphRAG when:** queries require synthesizing across many documents or understanding relationships between entities. Standard RAG fails on global queries like "what are the main themes across all these reports?" because no single chunk contains the answer. GraphRAG builds an entity-relationship graph and community summaries, enabling queries that require structural understanding. Microsoft's GraphRAG paper demonstrated this on analytical tasks where naive RAG performed near zero. LightRAG is a lighter-weight alternative combining graph and vector retrieval.

**Don't use advanced patterns as a first resort.** Self-RAG requires fine-tuning or strong prompting. CRAG requires a reliable retrieval scorer. GraphRAG requires significant preprocessing cost. Earn complexity by exhausting simpler options first.

See [advanced-patterns.md](references/advanced-patterns.md) for implementation details on each pattern.

---

## Step 7 — Evaluate Systematically

You cannot improve what you do not measure. RAG evaluation has two layers: retrieval quality and generation quality.

**Retrieval metrics (measure these first):**
- Context Precision: of the chunks retrieved, what fraction were actually relevant?
- Context Recall: of all relevant chunks in the corpus, what fraction were retrieved?
- NDCG / MRR: rank-aware metrics; relevant chunks should appear early

**Generation metrics:**
- Faithfulness (RAGAS): does the generated answer contradict or fabricate facts not in the retrieved context? This is your primary hallucination metric.
- Answer Relevance (RAGAS): does the answer address what was actually asked?
- RAGTruth patterns: hallucinations in RAG outputs cluster into unsupported additions, contradictions with retrieved context, and numerical errors — instrument specifically for these

**LLM-as-judge caveats (G-Eval, MT-Bench findings):**
- LLM judges show position bias — they favor responses presented first
- LLM judges show verbosity bias — longer responses score higher independent of quality
- Always randomize option order when using LLM judges; use rubric-based scoring (G-Eval style) not pairwise preference
- For open-source evaluation without GPT-4 API dependency, consider Prometheus 2

**Use RAGAS for automated pipeline evaluation.** It provides reference-free metrics computed only from the question, retrieved context, and generated answer — no ground truth required. Use ARES when you have the capacity to generate synthetic labeled data for a more rigorous framework.

**Minimum eval setup before shipping:**
1. 50–100 representative questions from your actual user queries
2. Human-labeled relevance judgments for retrieval eval (or use RAGAS context metrics)
3. Faithfulness scoring on generated answers
4. A regression test that runs on every pipeline change

See [evaluation.md](references/evaluation.md) for detailed metric definitions, tooling, and eval dataset construction guidance.

---

## Common Failure Modes and Fixes

| Symptom | Likely Cause | Fix |
|---|---|---|
| Retrieval returns irrelevant chunks | Embedding model too generic | Switch to domain-specific or fine-tuned embeddings; add BM25 hybrid |
| Right answer exists but isn't retrieved | Chunk context lost during embedding | Add contextual retrieval (Anthropic approach) |
| Model ignores retrieved context | Relevant chunk buried in middle | Reorder — most relevant first or last |
| Model generates facts not in context | No sufficiency check; model fills gaps | Add Sufficient Context check before generating |
| Good retrieval but wrong final answer | Generator doesn't attend to all passages | Check context length; ensure all chunks are within effective attention range |
| Queries about relationships across documents fail | Single-passage RAG can't do multi-hop | Escalate to GraphRAG or CRAG with web fallback |
