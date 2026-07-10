# Evaluation

Use this reference when the user asks whether memory is helping or how to test it.

Memory evals need to test the whole loop: write, manage, read, and final behavior. Retrieval hit rate alone is not enough.

## Minimum Test Suite

Build 30-100 realistic multi-turn or multi-session scenarios. Include:

- Stable user preference that should be remembered.
- Preference update that should supersede the old value.
- Sensitive fact that should not be saved.
- Explicit "forget this" request.
- Similar users or projects to test isolation.
- Old irrelevant episode that should not be retrieved.
- Past failure that should improve a repeated task.
- Missing memory case where the agent should abstain.

## Metrics

Write policy:

- Save precision: saved memories that should have been saved.
- Save recall: required memories that were captured.
- Reject rate for unsafe, transient, or useless candidates.
- Correct update/noop/delete decisions.

Retrieval:

- Scoped hit rate: correct memory appears under the right namespace.
- Top-k relevance.
- Stale-memory suppression.
- Cross-user/project leakage rate.

Final answer:

- Task success with memory vs without memory.
- Personalization correctness.
- Temporal reasoning correctness.
- Abstention when memory is absent or ambiguous.
- Regression impact on non-memory tasks.

## Long-Term Memory Abilities

LongMemEval is useful as a checklist: information extraction, multi-session reasoning, temporal reasoning, knowledge updates, and abstention. It is a research benchmark for chat-assistant memory, not a substitute for domain-specific evaluation or a production safety case.

LoCoMo is useful for very long conversational memory: long-range consistency, event summarization, temporal and causal dynamics, and multi-session question answering. Treat benchmark scores cautiously: dataset coverage, answer quality, judge design, and retrieval setup can all affect results.

Convert those benchmark ideas into product-specific evals. Do not rely on generic benchmark scores alone.

## Test The Write Gate Directly

Create unit tests for memory candidates:

- "Remember I use pnpm in this repo" -> save as project procedural/semantic memory.
- "I feel annoyed right now" -> usually do not save.
- "My SSN is ..." -> reject.
- "Actually, I prefer TypeScript now" -> supersede old preference.
- "Forget my dietary preference" -> delete or deactivate matching memory.

These tests catch most dangerous failures earlier than end-to-end chat tests.

## Test Retrieval Assembly

Given a query and namespace, assert:

- Correct filters are applied before vector search or rank fusion.
- Invalid or deleted memories are excluded.
- Current facts outrank superseded facts.
- Episodes are retrieved only when the user needs history or examples.
- The final context contains compact memory snippets, not whole transcripts.

## A/B And Regression Testing

Run each scenario with memory disabled, with the baseline memory stack, and with proposed changes. Memory should improve the target cases without degrading unrelated tasks through irrelevant context.

Track latency and token cost. Hot-path memory extraction is often the first thing to move to background when quality is acceptable but latency is not.
