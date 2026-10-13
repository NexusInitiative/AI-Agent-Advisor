# Advanced RAG Patterns

Reach for these only when the baseline (naive RAG, hybrid retrieval, contextual chunking, reranking) fails in a way you have measured. Each pattern adds indexing, inference, or training cost. Descriptions follow the papers; results are the authors' own unless stated otherwise. Sources are in [source-map.md](source-map.md).

## Adaptive retrieval: decide whether and when to retrieve

**Self-RAG** (Asai et al.) trains one language model to emit reflection tokens so it can retrieve on demand and critique its output. Per the paper the tokens are: *Retrieve* (yes, no, continue), *IsRel* (relevant or irrelevant), *IsSup* (fully supported, partially supported, no support), and *IsUse* (a 1 to 5 usefulness rating). Self-RAG at 7B and 13B outperformed ChatGPT and retrieval-augmented Llama2-chat on open-domain QA, reasoning, and fact-verification tasks, and improved factuality and citation accuracy on long-form generation. It requires training a model; prompting a general model to imitate it is a different, unvalidated method.

**Adaptive-RAG** (Jeong et al., NAACL 2024) trains a small classifier to predict query complexity and then chooses between no retrieval, single-step retrieval, and iterative retrieval, reporting better efficiency and accuracy than fixed strategies on open-domain QA.

**FLARE** (Jiang et al., EMNLP 2023) drafts the upcoming sentence and retrieves again when it contains low-confidence tokens; it targets long-form generation where one up-front retrieval is not enough.

**When to use:** queries differ widely in difficulty, or fixed top-k retrieval hurts easy queries. **Skip when:** nearly every query needs the same single retrieval, or you cannot train or host the extra components.

## Corrective retrieval: handle bad retrieval explicitly

**CRAG** (Yan et al.) adds a lightweight retrieval evaluator that scores retrieved documents and triggers one of three actions: *Correct* (documents are refined by decomposing them into knowledge strips, filtering, and recomposing), *Incorrect* (documents are discarded and web search supplies replacement knowledge), or *Ambiguous* (a soft combination of both). The paper reports gains when CRAG is plugged into several RAG approaches.

**When to use:** the corpus is incomplete or retrieval quality is unpredictable and you can use a search fallback. **Skip when:** you cannot call external search, or retrieval is already reliable on your measured set.

## Multi-hop questions: retrieval that follows the reasoning

Standard retrieve-then-read struggles when what to retrieve depends on what was already derived. MultiHop-RAG found existing RAG methods unsatisfactory at retrieving and answering multi-hop queries.

- **IRCoT** (Trivedi et al., ACL 2023) interleaves retrieval with chain-of-thought steps. With GPT-3 it improved retrieval by up to 21 points and downstream QA by up to 15 points across four datasets, and reduced hallucination in the reasoning.
- **HippoRAG** (Gutiérrez et al., NeurIPS 2024) indexes with a knowledge graph and Personalized PageRank. It outperformed state-of-the-art methods by up to 20% on multi-hop QA, and single-step HippoRAG matched or beat iterative IRCoT while being 10 to 30 times cheaper and 6 to 13 times faster, per the authors.

## Graph-based retrieval for global questions

**GraphRAG** (Edge et al.) extracts entities and relationships with an LLM, builds a graph, detects communities, summarizes each, and answers global questions from the community summaries. The authors targeted global sensemaking questions over corpora of roughly 1 million tokens. Against vector RAG, global approaches won 72% to 83% of LLM-judged head-to-head comparisons on comprehensiveness (podcast corpus; 72% to 80% on news) and 75% to 82% on diversity (podcast; 62% to 71% news). Empowerment was mixed, and vector RAG gave the most direct answers. The abstract states that conventional RAG fails on global questions; it does not report near-zero baseline scores.

**LightRAG** (Guo et al.) combines graph structures with vector retrieval and supports incremental updates. In the authors' comparison on a legal dataset, GraphRAG's retrieval consumed about 610,000 tokens (610 communities of about 1,000 tokens each), against under 100 tokens and one API call for LightRAG. Treat that as self-reported on one dataset.

**Independent evidence is more cautious.**

- Han et al. (a unified comparison of RAG and GraphRAG): there was no consistent winner. RAG did better on single-hop and detail-oriented factual queries; GraphRAG did better on multi-hop, reasoning-heavy questions; community-based global search could sacrifice query-specific details; and LLM-judged summarization comparisons showed strong position effects.
- GraphRAG-Bench (Xiang et al., ICLR 2026): RAG excelled at discrete facts for simple questions, GraphRAG's advantages emerged as questions grew more complex, and GraphRAG significantly increased prompt length.

**Use graph retrieval when** questions are global or multi-hop and your measured baseline fails on them. **Avoid it for** single-passage factual lookup, frequently changing corpora (graph maintenance), or small budgets.

## Agentic and trained multi-step search

- **Anthropic's multi-agent research system** replaces static retrieval with dynamic multi-step search. In Anthropic's analysis, token usage alone explained 80% of the variance in BrowseComp performance, agents used about 4 times the tokens of a chat, and multi-agent systems about 15 times. It is economical only for tasks valuable enough to pay for that.
- **Search-R1** (Jin et al.) trains a model with reinforcement learning to issue multiple searches during reasoning, improving results by 41% (Qwen2.5-7B) and 20% (Qwen2.5-3B) over RAG baselines under the same setting. It requires RL training infrastructure.
- A 2025 survey of agentic RAG offers a taxonomy and lists open challenges in evaluation, coordination, memory, efficiency, and governance.

Use these for open-ended research where fixed pipelines demonstrably fail, and budget for tokens, latency, and evaluation of multi-step behavior. See `advise-multi-agent` for orchestration.

## Fusion-in-Decoder (FiD)

Izacard and Grave's FiD encodes each retrieved passage separately with the question and lets the decoder attend over all of them. It obtained state-of-the-art results on Natural Questions and TriviaQA at the time, and its performance improved significantly as the number of retrieved passages increased, which the authors read as evidence that generative models can aggregate evidence across passages. Jin et al. later found that for long-context LLMs quality first rose and then fell as passages were added, so the response to passage count depends on the model and the retriever; measure it for yours (Step 5 of the main skill).

## Escalation path

Naive RAG, then hybrid and contextual chunking, then reranking, then the pattern that matches the measured failure (adaptive for variable need, corrective for unreliable retrieval, iterative or graph for multi-hop, graph for global, agentic for open-ended research). Justify each step with a failure in the previous one, and confirm the gain on held-out questions. A selection guide with costs is in [architecture-selection.md](architecture-selection.md).
