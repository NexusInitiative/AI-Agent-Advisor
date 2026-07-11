# Context Budgeting Reference

Use this file when implementing a token budget, a working-state checklist, or checkpoint summarization.

## Worked Budget Example

A support agent on a 200k-token window, with tools and RAG:

| Slot | Budget | Notes |
|---|---|---|
| System prompt + tool definitions | 18k | Byte-stable; first in the prompt so provider caching applies |
| Retrieved policy passages | 60k max | Top-k with a hard cap; evict below-threshold passages instead of truncating blindly |
| Conversation (recent turns verbatim) | 30k | Last N turns raw; older turns live in the summary |
| Rolling summary + working state | 8k | Structured schema below |
| Response headroom | 40k | Protects long, cited answers |
| Slack | remainder | Absorbs spikes; alert when slack < 10% |

Enforce the caps in code. When the evidence slot wants more, the assembler must evict (lowest-relevance passage first) and log the eviction — silent tail truncation is how load-bearing constraints disappear.

## Working-State Checklist Template

Keep this as a single structured block, rebuilt at every checkpoint:

```markdown
## Task State
- Goal: <one sentence, user's words>
- Constraints: <hard requirements, budgets, deadlines, "never do X">
- Decisions: <decision — reason — turn/link>
- Done: <completed actions with artifact paths/IDs>
- Open: <unresolved questions, blocked items and what unblocks them>
- Artifacts: <file paths, ticket IDs, URLs — references, not contents>
```

Rules: facts get provenance (where they came from), superseded entries are removed rather than contradicted, and the block never contains document bodies — only references.

## Summary Schema for Checkpoint Compaction

When compacting conversation history, produce this — not a narrative:

```markdown
## Summary (v<N>, through turn <T>)
- Outcome so far: <what has been produced/decided>
- Active constraints: <verbatim-critical constraints, quoted exactly>
- Superseded: <what was tried and abandoned, one line each>
- Pending: <what remains, in priority order>
- Sources: <IDs/paths of artifacts the summary derived from>
```

Quote constraints and identifiers exactly; paraphrasing is where compaction loses correctness. Anything the model may later need verbatim (legal wording, code, config values) is referenced by path and re-retrieved, never trusted from the summary.

## Retention Test Before Trusting Compaction

After generating a summary, run these checks (automatable as an eval):

1. Ask the model, given only the summary, to restate every active constraint. Compare against the pre-compaction list — any miss fails the schema, not the model.
2. Ask it to answer the most likely next-task question. If it needs evicted material, the eviction policy is wrong.
3. Diff summary version N against N−1 for silently dropped decisions.

Run the same checks in CI on recorded sessions whenever the summary prompt or schema changes.

## Ordering Rules

- Strongest evidence and critical instructions early; a short task restatement and output-format reminder last.
- Group evidence by source with clear delimiters and stable labels (`[DOC-3]`) so citations survive reordering.
- Keep the stable instruction prefix untouched — reordering inside it breaks prompt caching (see `advise-caching`).
