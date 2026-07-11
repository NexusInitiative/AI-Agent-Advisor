---
name: advise-context
description: |
  This skill should be used when the user asks to "how should I manage context", "advise on context windows",
  "help with context length strategy", "what to include in my context", "context window management",
  "my agent loses track", "should I summarize or use RAG", "how do I reduce token use",
  or needs guidance on context composition, compression, ordering, or token budgets.
---

# Context Advisor

## Step 1 — Diagnose the Actual Context Problem

"Context management" hides four distinct problems with different fixes. Ask or infer which one the user has:

- **Overflow:** conversations or documents exceed the window → compression or retrieval.
- **Distraction:** the model has the right information but ignores it → placement, structure, and pruning.
- **Cost/latency:** token bills or response times are too high → budgeting, caching, and pruning.
- **State loss:** a multi-step agent forgets decisions mid-task → structured state, not more transcript.

Also establish: typical and worst-case input sizes, how many turns a session runs, what other consumers share the window (tools, memory, retrieved docs), and whether outputs must quote or cite sources exactly.

Treat context as a limited working set, not a transcript bucket: every item must earn its tokens by changing the next decision. Anthropic's [context engineering guidance](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) frames this as finding the smallest set of high-signal tokens that maximizes the likelihood of the desired outcome — that framing is the right default.

---

## Step 2 — Set an Explicit Token Budget

Write down a budget before tuning anything. A workable starting allocation for an agent with a 200k window (scale proportionally):

| Slot | Share | Contents |
|---|---|---|
| Stable instructions + tools | 10–15% | System prompt, tool definitions, output contracts — keep byte-stable for prompt caching |
| Task + user input | 5–10% | Current request, user-provided facts |
| Evidence | 30–50% | Retrieved docs, tool results, files — the elastic slot |
| Working state | 5–10% | Decisions, constraints, open questions, artifact locations |
| Response headroom | 15–25% | Never let evidence squeeze the answer |

The budget makes trade-offs visible: when evidence wants more room, something must be evicted deliberately rather than by silent truncation. Log actual allocation per request so regressions show up as numbers. See [context-budgeting.md](references/context-budgeting.md) for a worked example and the state-checklist template.

---

## Step 3 — Put Information Where It Belongs

- **System/developer layer:** stable policy, permissions, output contracts, tool rules. Changing this per-request breaks prompt caching and instruction stability.
- **User turn:** the current request, user-provided facts, desired outcome.
- **Tool results:** structured, clearly delimited, machine-produced. Treat retrieved documents, web pages, and tool output as untrusted *data* — state explicitly that they must not override instructions (prompt-injection defense belongs here, not only in the harness).
- **Working state:** a compact, explicit checklist — goal, decisions made, completed actions, constraints, open questions, artifact paths. This is the single highest-leverage artifact for long-running agents: agents that carry state as prose transcripts lose it; agents that carry a structured checklist can resume after compaction.

Prefer source-of-truth references over copied prose: load exact files, rows, or passages on demand instead of pasting whole documents "just in case." Don't duplicate the same fact in multiple slots — duplication wastes budget and creates contradiction risk when one copy goes stale.

**Placement matters.** The Lost in the Middle result (Liu et al.) shows relevant content is used best at the beginning or end of long contexts and underused in the middle. Put critical instructions and the strongest evidence early; reserve the end for a concise task reminder or required output format. Effect size varies by model and length, so verify on your own long-context evals rather than assuming.

---

## Step 4 — Choose Compression vs. Retrieval vs. Long Context

Decision rule of thumb:

- **Rolling summary** when the *conversation itself* is the source of truth (support threads, pair-programming sessions). Preserve decisions, constraints, unresolved work, IDs, and links — not narrative. Summarize at explicit checkpoints (task completion, phase change), not every turn.
- **Retrieval (RAG)** when knowledge lives in a *large external corpus* and only a few passages are relevant per query. See `advise-rag` for pipeline design.
- **Long context** when relationships *across* a large source matter (whole-codebase reasoning, contract review) and you can afford the tokens and can evaluate the quality. Long context is not a substitute for selection — stuffing reduces signal-to-noise and costs linearly forever.
- **Deterministic code/tools** for exact state, counting, and search. Never spend context making the model simulate a database.
- **Persistent memory** only for information that must affect *future sessions* and has write/retrieval governance — see `advise-memory`.

These compose: a coding agent typically runs structured state + on-demand file loads + checkpoint summaries simultaneously.

---

## Step 5 — Compress Without Losing Control

Compaction is lossy; manage it like a risky operation:

1. Summarize at checkpoints into a structured schema (see the reference file), storing provenance and timestamps for each preserved fact.
2. Replace verbose history with the summary; keep original artifacts retrievable by path/ID so anything can be re-expanded.
3. **Test the summary** before trusting it: can the agent answer the next task's questions and restate the active constraints from the summary alone? If not, the schema is dropping load-bearing fields.
4. If the model must quote, cite, or interpret exact wording (legal text, code, policies), retain or re-retrieve the original — a summary is never a source of truth.
5. Refresh summaries after major decisions; a stale summary that contradicts recent turns is worse than no summary.

---

## Step 6 — Measure and Defend

Log per request: token allocation by slot, truncation events, retrieval counts, summary version, and failures. Build evals for: long-context retrieval quality, constraint retention across compaction, stale-summary detection, injection attempts via retrieved content, and token-cost regressions. A context change that improves quality but doubles cost should be a visible, deliberate trade.

---

## Common Failure Modes and Fixes

| Symptom | Likely Cause | Fix |
|---|---|---|
| Agent forgets decisions mid-task | State carried as prose transcript | Maintain a structured state checklist; rebuild it into every compaction |
| Right document in context, wrong answer | Relevant content buried mid-context | Reorder: strongest evidence first, task reminder last |
| Costs grow linearly with session length | No compaction checkpoints | Summarize at phase boundaries; evict superseded evidence |
| Constraint silently dropped after summarization | Unstructured narrative summary | Use a summary schema with a constraints field; test retention |
| Retrieved page changes agent behavior | Untrusted data treated as instructions | Delimit evidence as data; assert precedence in the system layer |
| Prompt cache misses after every deploy | Volatile content in the stable prefix | Move dynamic content after the cached prefix; see `advise-caching` |

---

## References

- **Budget worksheet, state-checklist template, and summary schema:** read [context-budgeting.md](references/context-budgeting.md) when implementing budgets or compaction.
- **Verified sources with claims and caveats:** read [source-map.md](references/source-map.md) when citing evidence behind these recommendations.
