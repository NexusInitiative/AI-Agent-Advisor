# Recipes: Agents and Systems (A1–A8)

Same template as the other recipe files. Sources are in [source-map.md](source-map.md). Runtime design lives in `advise-harness`, orchestration in `advise-multi-agent`, caching in `advise-caching`, and memory in `advise-memory`. Items marked *(procedure)* are workflow steps rather than findings. Anthropic's guidance is to find the simplest solution and add complexity only when needed, since agentic systems trade latency and cost for task performance; keep that in mind before adding structure to fix a failure.

## A1. Wrong tool or bad arguments

**Test.** Replay the known-correct call in a safe fixture, then read the transcript to see what the model saw: the tool names, descriptions, schemas, and error messages.

**Causes and fixes.**

1. *Weak arguments and invented usage.* GPT-4 was limited by inaccurate input arguments and hallucinated API usage, and combining a model with a retriever over API documentation mitigated it (Gorilla).
2. *Interface design.* The agent-computer interface significantly affects agent performance (SWE-agent).
3. *Tool definitions.* Anthropic recommends a few thoughtful tools for high-impact workflows, shared name prefixes, descriptions written as for a new hire, strict data models for inputs and outputs, high-signal results instead of low-level identifiers, token-efficient responses, and error messages that suggest a fix. It also recommends evaluating tools with realistic multi-step tasks and reading transcripts.

**Verify.** Tool-call accuracy and argument validity on an evaluation set, and transcript review of residual errors.

## A2. Loops, stalls, or runaway cost

**Test.** Scan the trace for repeated steps, missing termination, and steps versus budget.

**Causes and fixes.** In the MAST analysis, step repetition (15.7%) and being unaware of termination conditions (12.4%) were among the most common failure modes, with premature termination at 6.2%; in AgentBench, exceeding the task limit was the predominant failure cause, revealing weak reasoning and decision-making. Define explicit termination criteria, set a step and token budget, add a verifier, and stop and escalate on no progress (AWS likewise advises limiting retries, for example with a token bucket). Where the task is well defined, a fixed workflow is more predictable than an open-ended agent (Anthropic).

**Do not** raise the step limit as the fix.

## A3. Loses track in long tasks or long conversations

**Test.** Run the same task fully specified in one turn and then spread over several turns; vary context length; inspect what is in context at the point of failure.

**Causes and fixes.**

1. *Multi-turn unreliability.* Tested LLMs performed 39% worse on average in multi-turn than single-turn settings across six tasks. The loss was mostly increased unreliability, not lost aptitude: models made assumptions early, tried to answer prematurely, and "when LLMs take a wrong turn in a conversation, they get lost and do not recover" (Laban et al.).
2. *Long inputs.* Reliability fell with input length even on simple tasks (Context Rot, an unreviewed technical report), and models claiming 32K tokens often could not sustain it on harder tasks (RULER).
3. *Position and history loss.* Middle-of-context information was used less (Lost in the Middle); loss of conversation history is a recorded multi-agent failure mode (MAST FM-1.4).

**Fix.** Since errors persisted once made, restart from a verified, consolidated state instead of continuing a bad branch, and test that approach on your task before relying on it *(procedure; the paper documents the problem, not this remedy)*. For context budgets and compaction see `advise-context`; for memory design see `advise-memory` (MemGPT is one published design; LoCoMo found long-term conversational memory still well behind human performance).

## A4. Multi-agent system fails, or is no better than one agent

**Test.** Label failed traces with MAST categories and compare with a single-agent baseline that has the same tools.

**Causes and fixes.** MAST identified 14 failure modes in three categories from 1,600+ traces across seven frameworks (inter-annotator kappa 0.88): system design issues (41.8% of failures), inter-agent misalignment (36.9%), and task verification (21.3%). The leading individual modes were step repetition, reasoning-action mismatch (13.2%), unawareness of termination, and disobeying the task specification. Tighten task and role specifications and termination rules (FC1), require clarification and explicit information sharing (FC2), and verify at several levels (FC3). A verifier alone was not a silver bullet and final-stage low-level checks were inadequate. Cost matters too: agents used about 4 times and multi-agent systems about 15 times the tokens of a chat in Anthropic's data, which pays off only for high-value tasks.

**Do not** assume a stronger model removes these failures; the authors found that a better-designed system improved results with the same model.

## A5. Duplicate emails, charges, or writes after a timeout

**Test.** Inspect system state after the timeout and look for retries in the logs.

**Causes and fixes.** Retries multiply load, and layered retries compound it. APIs with side effects are not safe to retry unless they provide idempotency, client errors should not be retried unchanged, and backoff needs jitter (Amazon Builders' Library). Use idempotency keys, check state before retrying an uncertain write, and apply bounded backoff with jitter to transient errors only. Provider SDKs already retry transient failures (the Claude SDK retries twice by default with exponential backoff), so avoid stacking another retry layer on top; a spend-cap 429 has no retry-after header and keeps failing until access resumes.

**Verify.** A fault-injection test that times out a write and confirms exactly one effect.

## A6. The cache returns an answer to a different question

**Test.** Log each semantic-cache hit with its similarity score, the new query, and the cached query, then judge a sample of hits.

**Causes and fixes.** Static similarity thresholds give no formal correctness guarantee and produce unexpected error rates; vCache learns a per-entry threshold from a user-defined error bound and reported up to 26 times lower error rates and up to 12.5 times higher hit rates than static thresholds. Include model, prompt, policy version, and tenant in the cache key and audit sampled hits (`advise-caching`). Provider prompt caching is different: it needs the entire rendered prefix to match, so its failure mode is a low hit rate, not a wrong answer (OpenAI documentation).

## A7. Memory is stale, wrong, or poisoned

**Test.** List the memory entries retrieved for the failing turn with their source and timestamp, then replay with memory disabled.

**Causes and fixes.** Poisoned long-term memory or knowledge bases reached over 80% average attack success at poison rates below 0.1% while leaving benign performance nearly unchanged (AgentPoison), so bad memory can be invisible in normal evaluation. Long-term conversational memory remains challenging even with long-context models and RAG (LoCoMo). Record provenance, validate before writes, and expire or supersede entries *(procedure)*; design detail is in `advise-memory`.

## A8. Retrieved or tool content caused an unauthorized action

**Test.** Replay the same content against the executor with the model removed, and check whether authorization is enforced outside the model.

**Causes and fixes.** Instructions injected into data the model retrieves can control how and whether other APIs are called (Greshake et al.). OpenAI notes that untrusted input in a developer message gives attackers the highest control. CaMeL separates control flow from untrusted data and enforces capability-based policies when tools are called, solving 77% of AgentDojo tasks with provable security versus 84% undefended, under its stated threat model. Enforce tenant, object, action, and destination checks in the executor, keep untrusted content out of privileged instructions, and require approval for consequential actions (`advise-harness`).

**Do not** rely on prompt wording or delimiters as the boundary.
