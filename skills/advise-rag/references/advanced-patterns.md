# Advanced RAG Patterns

Only reach for these when the baseline (naive RAG + hybrid retrieval + contextual chunking) is still insufficient. Each pattern adds meaningful complexity — maintenance cost, inference cost, or preprocessing cost. Know why you're adding it before you do.

---

## Self-RAG — Adaptive Retrieval and Self-Critique

**Paper:** Asai et al., "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection" (2023) — https://arxiv.org/abs/2310.11511

### What It Does

Self-RAG trains (or prompts) the model to emit special reflection tokens during generation:

- `[Retrieve]` / `[No Retrieve]` — decides whether retrieval is needed for this query
- `[ISREL]` / `[ISIRREL]` — judges whether retrieved passages are relevant
- `[ISSUP]` / `[ISPARTIALLY SUP]` / `[ISNOSUP]` — judges whether the generated statement is supported by the retrieved context
- `[ISUSE]` / `[ISNOTUSE]` — judges whether the response is useful overall

The model can retrieve multiple times within a single generation, critiquing its own output and retrieving again if needed.

### When to Use

- Query set is highly diverse (some queries need retrieval, others don't)
- Hallucination rate is high and retrieval quality is inconsistent
- You need fine-grained per-sentence source attribution
- You have the compute budget for multiple retrieval calls per query

### When Not to Use

- Simple, uniform query sets where retrieval is always needed
- Latency-sensitive applications (multiple retrieval rounds add significant latency)
- You don't have the capacity to fine-tune (prompting-only Self-RAG is weaker)

### Implementation Path

1. Start with prompting: instruct the model to explicitly assess whether it needs to retrieve before answering, and to flag any statements it cannot support from the context
2. If prompting isn't sufficient, fine-tune on Self-RAG training data or generate synthetic training data using the reflection token format
3. Use a retrieval threshold: only retrieve if the model's self-assessment confidence is below a set value

---

## CRAG — Corrective Retrieval Augmented Generation

**Paper:** Yan et al., "Corrective Retrieval Augmented Generation" (2024) — https://arxiv.org/abs/2401.15884

### What It Does

CRAG adds a retrieval evaluator between retrieval and generation:

1. Retrieve candidates as normal
2. Score each retrieved document with a lightweight evaluator (fine-tuned classifier or LLM call)
3. If score is **high** → use retrieved documents
4. If score is **low** → discard retrieved documents, fall back to web search (or broader corpus search)
5. If score is **ambiguous** → decompose the query, search for sub-questions, combine results

The key insight: bad retrieval actively hurts generation. It's better to acknowledge uncertainty than to generate from irrelevant context. "Lost in the Middle" and Sufficient Context both validate this — irrelevant context degrades generation quality, it doesn't just add noise.

### When to Use

- Your document corpus is incomplete — some queries will find no good answer in it
- Retrieval quality is inconsistent and hard to predict at query time
- You have access to a web search API as a fallback (Bing, Google, Brave Search)
- Hallucination rate is high even with good-looking retrieved context

### When Not to Use

- You cannot use web search (data sovereignty, air-gapped environments)
- Your corpus is comprehensive and well-indexed — the evaluator overhead isn't worth it
- Latency constraints are tight (evaluator + conditional web search adds time)

### Implementation Notes

- The retrieval evaluator can be a fine-tuned classifier (cheap at inference), a cross-encoder relevance score, or an LLM call ("Does this passage contain enough information to answer: [query]?")
- Web search fallback: retrieve the top web result, extract relevant passages, combine with any usable corpus passages before generating
- Use CRAG's knowledge refinement step: strip irrelevant sentences from retrieved documents before passing to the generator (reduces noise)

---

## GraphRAG — Graph-Based Retrieval for Multi-Hop and Global Queries

**Papers:**
- Microsoft GraphRAG: Edge et al., "From Local to Global: A Graph RAG Approach to Query-Focused Summarization" (2024) — https://arxiv.org/abs/2404.16130
- LightRAG: He et al., "LightRAG: Simple and Fast Retrieval-Augmented Generation" (2024) — https://arxiv.org/abs/2410.05779

### The Problem Standard RAG Can't Solve

Standard RAG retrieves individual passages. It fails when:
- The answer requires synthesizing across dozens of documents ("What are the key themes in these 500 customer complaints?")
- The query requires multi-hop reasoning ("Who reported to the person who signed the Q3 financial report?")
- The relevant information is distributed across the corpus with no single authoritative passage

### What GraphRAG Does

1. **Entity and relationship extraction:** Use an LLM to extract entities (people, places, concepts, events) and their relationships from all documents
2. **Graph construction:** Build a knowledge graph where nodes are entities and edges are relationships
3. **Community detection:** Cluster the graph into communities (related groups of entities) using algorithms like Leiden
4. **Community summaries:** Generate a summary for each community using an LLM
5. **Query routing:** For global queries, retrieve and synthesize community summaries. For local queries, use graph-traversal to find relevant entity neighborhoods, then retrieve associated passages

Microsoft's paper showed near-zero performance for standard RAG on global sensemaking queries where GraphRAG performed well.

### LightRAG as a Lighter Alternative

LightRAG combines graph indexing with vector retrieval in a simpler architecture:
- Extracts entities and relationships during indexing
- Stores them in both a graph structure and a vector index
- At query time: dual retrieval from both the graph and vector store, combined before generation
- Significantly lower preprocessing and query cost than full Microsoft GraphRAG

**Use LightRAG when:** You need graph-aware retrieval but can't afford GraphRAG's preprocessing cost (LLM calls over all documents for entity extraction and community summarization are expensive).

### When to Use GraphRAG

- Analytical queries over a large corpus ("summarize the main arguments across these documents")
- Knowledge graph-style queries ("what is the relationship between X and Y?")
- Multi-hop reasoning chains required
- Your users need to understand how documents relate, not just retrieve facts from them

### When Not to Use GraphRAG

- Your queries are factual and local (single-passage answers)
- Your corpus changes frequently (graph must be rebuilt on updates)
- You have a small corpus (< a few hundred documents) — overhead not justified
- Budget is constrained (entity extraction + community summarization requires many LLM calls at indexing time)

---

## Fusion-in-Decoder (FiD)

**Paper:** Izacard & Grave, "Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering" (2020) — https://arxiv.org/abs/2007.01282

### What It Does

FiD modifies the generator to encode each retrieved passage independently with the query, then concatenates the encoder representations before decoding. The decoder attends to all passage encodings simultaneously.

This differs from standard RAG where all passages are concatenated into a single long input string. FiD outperformed concatenation approaches on Natural Questions and TriviaQA benchmarks.

### Relevance to Modern LLMs

FiD was designed for encoder-decoder architectures (T5-style). Modern decoder-only LLMs already attend to all tokens in the concatenated context. The practical lesson: concatenate retrieved chunks into the context rather than processing them sequentially, and order them with the most relevant first (per the "Lost in the Middle" finding).

---

## The Naive → Advanced Escalation Path

```
Naive RAG (baseline)
  ↓ if: retrieval quality is low for keyword queries
Hybrid retrieval + RRF
  ↓ if: chunks lack context
Contextual chunking (Anthropic approach)
  ↓ if: query needs synthesis across many docs
GraphRAG or LightRAG
  ↓ if: retrieval confidence is inconsistent or corpus is incomplete
CRAG with web fallback
  ↓ if: need per-statement attribution or selective retrieval
Self-RAG
```

Each step should be justified by a measured failure in the previous step.
