---
name: advise-models
description: |
  This skill should be used when the user asks to "which model should I use", "advise on models",
  "help me choose an LLM", "what model is best for my use case", "compare models",
  "should I use GPT or Claude", "how do I reduce model cost", "should I route requests",
  or needs guidance on model selection, routing, quality, latency, privacy, or deployment trade-offs.
---

# Model Advisor

Model selection is a measured product decision, not a leaderboard pick. Model names, prices, and capabilities change every few months — so this skill teaches a selection *process* that stays valid, and deliberately avoids asserting which specific model is best this quarter.

## Step 1 — Pin Down Requirements Before Naming Models

Ask or infer:

**Task shape:** What must the model actually do — classify, extract, converse, code, reason over long documents, call tools, process images? Which of these dominates the traffic?

**Failure tolerance:** Which failures are unacceptable (wrong tool call that moves money, fabricated citation, missed refusal)? Which are merely annoying? This split defines your gates later.

**Operational envelope:** p95 latency target, expected volume, budget per request, availability needs, and traffic spikes.

**Deployment constraints:** data residency, privacy review, offline requirements, existing cloud commitments. These can eliminate whole categories before quality enters the picture.

**Inputs:** context length actually needed (measured, not guessed), modalities, languages.

Name any assumption you fill in. A recommendation built on an unstated latency guess is a wrong recommendation delivered confidently.

---

## Step 2 — Build the Task Eval, Then Shortlist

Build a representative evaluation set *before* comparing providers: ordinary traffic, hard cases, long inputs, malformed inputs, safety cases, and real production failures (see `advise-eval` for construction). Without this, model choice is vibes.

Then shortlist 2–3 candidates that pass the hard constraints (modalities, context, tools, structured output, deployment). Use public benchmarks like [HELM](https://crfm.stanford.edu/helm/) and provider docs to *filter*, not to decide: aggregate benchmarks rank models on someone else's tasks, and provider documentation is authoritative for features and pricing but is not independent quality evidence.

**Default starting posture:** begin with one capable general model at the top of your affordable range, make it work, then optimize downward. Premature optimization to a small model costs more in engineering time than it saves in tokens; you can only safely downsize once the eval exists to prove the smaller model holds.

---

## Step 3 — Match Model Tier to the Work

- **Frontier-tier model** when incorrect reasoning is expensive: complex tool use, multi-step agents, code generation beyond boilerplate, high-value decisions, safety-sensitive conversations. Token cost is usually dwarfed by the cost of being wrong.
- **Small/fast model** when the task is narrow, well-specified, high-volume, and validated: classification, extraction, routing, summarization with fixed formats. Pair it with deterministic validation (schemas, checks) so its failures are caught cheaply.
- **Local/self-hosted open model** when data residency, offline operation, deep customization (see `advise-fine-tune`), or predictable marginal cost at very high volume outweigh managed-service convenience. Budget for real ops: serving infrastructure, upgrades, and evals are now your job.
- **Specialized model** (code-specific, embedding, vision) only when its advantage shows up on *your* eval, not its marketing page.

---

## Step 4 — Compare Fairly, Decide With Gates

Hold everything constant except the model: same prompts (lightly adapted per provider conventions where required — note the adaptations), same tools, retrieval, sampling, timeouts, and eval cases. Run nondeterministic tasks multiple times and compare distributions, not single runs.

Score against **separate gates**, never a single blended score:

| Gate | Evidence |
|---|---|
| Critical task success ≥ target | task eval, worst-case included |
| Critical failure rate ≤ budget | safety/failure cases |
| p95 latency ≤ target | load test at realistic concurrency |
| Cost per request ≤ budget | measured tokens × current pricing |
| Deployment/compliance pass | contract and configuration review |
| Fallback behavior acceptable | failure drill (provider outage, rate limits) |

A model that wins the average but breaches one gate loses. Document the runner-up — it's your fallback and your renegotiation leverage.

---

## Step 5 — Add Routing Only After the Baseline Proves Itself

Routing (cheap model first, escalate hard cases) is a real cost lever — FrugalGPT-style cascades showed large savings on some workloads — but it's an optimization with its own failure modes, not an architecture to start with.

Prerequisites before routing anything:
1. A measured single-model baseline with per-category results.
2. Evidence that an identifiable subset is handled safely by the cheaper path.
3. An escalation trigger you can trust: observable task features or calibrated confidence — not response length or the model's self-assessment.
4. Logging of every routing decision so misroutes are auditable.

Never route by risk downward: high-stakes actions go to the capable model even when the cheap one is "usually fine." Re-validate routes whenever a provider updates a model version.

---

## Step 6 — Treat Models as Versioned Dependencies

Pin model versions where the provider allows; never let an auto-updating alias drift under production silently. Re-run the eval on provider version bumps, price changes, or context-limit changes. Keep the runner-up integration warm (adapter layer, tested prompts) so provider incidents are a config change, not a rewrite. Monitor quality drift with sampled production evals, not just uptime.

---

## Common Failure Modes and Fixes

| Symptom | Likely Cause | Fix |
|---|---|---|
| Great demo, bad production quality | Chose from leaderboard, not task eval | Build the eval set; re-decide with gates |
| Costs blew up at scale | Frontier model on high-volume narrow tasks | Downsize the narrow slice behind validation; keep frontier for the hard core |
| Cheap model quietly degraded outcomes | Routing without per-category evidence | Add escalation triggers + route logging; re-validate routes |
| Quality dropped with no deploy | Provider alias auto-updated | Pin versions; eval on provider changelog events |
| Provider outage took the product down | No warm fallback | Maintain tested runner-up integration and failure drills |
| Model "fails" on grounding or permissions | Wrong layer — model score used as proxy | Fix retrieval (`advise-rag`) and authorization (`advise-harness`); models don't solve those |

For prompt adaptation per model, see `advise-prompting`; for the measurement machinery, see `advise-eval`.

---

## References

- **Requirements worksheet, comparison protocol, and routing readiness checklist:** read [model-selection.md](references/model-selection.md) when running a selection or adding routing.
- **Verified sources with claims and caveats:** read [source-map.md](references/source-map.md) when citing evidence; treat all model names, prices, and limits as version-sensitive.
