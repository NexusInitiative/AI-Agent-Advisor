---
name: advise-fine-tune
description: |
  This skill should be used when the user asks to "should I fine-tune", "advise on fine-tuning",
  "when to fine-tune vs prompt engineer", "help with fine-tuning a model",
  "distillation vs fine-tuning", "should I use LoRA", "how much training data do I need",
  or needs guidance on model customization, training data, or adaptation trade-offs.
---

# Fine-Tuning Advisor

## Step 1 — Diagnose Whether Fine-Tuning Is Even the Right Tool

Most fine-tuning requests are actually prompting, retrieval, or tooling problems. Before anything else, ask or infer:

- What specific behavior is wrong today, with examples? ("Quality is bad" is not a trainable objective.)
- Is the gap about **knowledge** (facts the model doesn't have), **behavior** (format, style, policy, tool-use patterns), or **capability** (reasoning the model can't do)?
- Is there a strong baseline already: a well-engineered prompt, structured outputs, retrieval for facts, tools for calculation?
- Can you label a correct answer consistently? If two of your own reviewers would disagree on the right output, you are not ready to train.

**Route by gap type:**
- Changing or long-tail *facts* → retrieval (`advise-rag`), not fine-tuning. Fine-tuning does not reliably add current knowledge and cannot cite sources.
- A handful of *rules or formats* → prompting and structured outputs (`advise-prompting`). Cheaper, inspectable, instantly reversible.
- Missing *context* → context design (`advise-context`).
- *Calculation/lookup accuracy* → tools, not weights.
- Stable, repeated, narrow *behavior* that survives all of the above and still underperforms → fine-tuning is now on the table.

Fine-tuning earns its cost for: narrow classification/extraction at volume, rigid format consistency, domain tone/style, tool-call policy shaping, latency/cost reduction by moving work to a smaller model, and distillation of a defined task from a stronger teacher.

---

## Step 2 — Define the Target Before Collecting Data

Write down, in this order:

1. A held-out evaluation with a target metric (exact-match, F1, rubric score — see `advise-eval`) and the current baseline's score on it.
2. An error taxonomy of today's failures (which categories must the tuned model fix?).
3. The regression set: behaviors that must *not* get worse (safety refusals, adjacent tasks, general instruction following).

If the baseline eval doesn't exist, build it first — otherwise you cannot distinguish a successful fine-tune from a placebo.

---

## Step 3 — Build the Dataset (This Is Most of the Work)

Data quality dominates method choice. Requirements:

- **Match production.** Inputs drawn from real traffic distribution; outputs exactly as you want them produced, including formatting, refusals, and edge-case handling. Include deliberate hard cases and failures from your error taxonomy.
- **Clean ruthlessly.** Deduplicate; remove contradictory labels; fix systematic labeler disagreements before scale-up. A small clean set beats a large noisy one — hundreds to a few thousand strong examples is a realistic starting range for behavior-shaping tasks (provider guidance agrees; treat any fixed number as a starting point, not a law).
- **Split against leakage.** Separate train/validation/test by entity or time when the same customer, document, or template could appear on both sides. Keep a protected holdout that nobody tunes against.
- **Synthetic data with guardrails.** Teacher-generated examples are fine for coverage, but human-review a sample, filter aggressively, and never let synthetic data crowd out production-distribution coverage.
- **Governance.** Document provenance, licenses, and sensitive fields. Do not train on raw production conversations without privacy/legal review — training data is effectively permanent.

---

## Step 4 — Choose the Cheapest Adaptation That Can Hit the Target

In escalation order:

1. **Hosted supervised fine-tuning (SFT)** — when you're on a provider that offers it (e.g., [OpenAI's fine-tuning API](https://platform.openai.com/docs/guides/fine-tuning)) and the task is input→output behavior. Zero infrastructure; limited knobs.
2. **LoRA on an open model** — the default for self-hosted adaptation. Hu et al. showed low-rank adapters can match full fine-tuning quality on many tasks while training a fraction of parameters; adapters are cheap to store, swap, and roll back.
3. **QLoRA** — LoRA over a quantized base (Dettmers et al.) when GPU memory is the binding constraint. Adds quantization complexity; verify quality against plain LoRA when feasible.
4. **Distillation** — a stronger teacher generates/labels data for a smaller student; right when the goal is cost/latency at a defined task. The student must pass the same holdout as the teacher-based baseline.
5. **Full fine-tuning** — only when you control the model, have substantial data, and measured PEFT results cannot reach the target. Highest cost, highest regression risk, hardest rollback.

Preference-optimization methods (RLHF/DPO-family) are for shaping *preferences* at scale, not first-line task adaptation — exhaust SFT first.

Run small experiments first: base vs. prompt-only vs. retrieval/tool baseline vs. candidate adapter, all on the same holdout. Stop training when validation stops improving; investigate errors rather than adding epochs — more epochs on a small set is the fastest route to memorization.

---

## Step 5 — Evaluate Beyond the Target Metric, Then Ship Safely

Before deploying, measure: target-task quality, the regression set (adjacent tasks, refusal behavior, jailbreak susceptibility — tuning can erode safety behavior), output-format validity, latency, and serving cost.

Ship like any risky change: version the dataset + preprocessing + base model + hyperparameters + adapter + prompt + evaluator as one unit; canary against the incumbent; keep instant rollback (adapter swap makes this trivial with LoRA); monitor drift and re-run the holdout on a schedule. Re-train on demonstrated distribution shift, not on a calendar.

---

## Common Failure Modes and Fixes

| Symptom | Likely Cause | Fix |
|---|---|---|
| Great validation score, mediocre in prod | Leakage or unrepresentative data | Re-split by entity/time; sample training inputs from live traffic |
| Model learned format but invents facts | Fine-tuning used for knowledge | Add retrieval; keep tuning for behavior only |
| Quality regressed on everything else | Overfit narrow data; too many epochs | Fewer epochs, more diverse data, mix in general instruction data |
| Tuned model ignores new instructions | Behavior baked in too rigidly | Retune with instruction-varied examples; keep changing rules in the prompt |
| Wins in eval, loses money in serving | Ignored serving cost/latency | Include p95 latency and $/request as shipping gates |
| Can't reproduce last month's model | Untracked data/config versions | Version the full tuple; store eval snapshots with each run |

---

## References

- **Method-selection table, data checklists, and experiment protocol:** read [adaptation-playbook.md](references/adaptation-playbook.md) when the decision is made and implementation starts.
- **Verified sources with claims and caveats:** read [source-map.md](references/source-map.md) when citing evidence behind these recommendations.
