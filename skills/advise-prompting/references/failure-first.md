# Failure First, Technique Second

Read this reference to select an intervention for an apparent prompting failure. Use the main skill for the advisory sequence; use the specialized advisors for implementation depth. Symptom-indexed recipes that span retrieval, training, tools, caches, and graders live in `advise-debug`; this file keeps the prompt-scoped probes.

## Diagnose with controlled substitutions

Write the failing requirement and preserve a sanitized input, evidence snapshot, provider response, application result, and relevant tool/state trace. Reproduce the baseline before changing it. Check labels, fixture state, and resource limits: a bad expected answer or infrastructure error can mimic a model defect. Anthropic reports that agentic coding scores moved by 6 percentage points with container resource limits alone, and that, with frontier models, a 0% pass rate across many trials is most often a signal of a broken task.

Replace one upstream component with a known-good input. If authoritative evidence supplied directly fixes a fabricated answer, investigate source coverage, freshness, ingestion, retrieval, and permissions. If human-selected chunks help but retrieved chunks do not, investigate candidate recall and selection. If both fail, check whether the evidence answers the question and whether the prompt preserves qualifiers or contradictory facts.

If necessary-only context helps, compare selection and placement rather than increasing the context window reflexively: in one study, output quality first rose and then fell as more passages were retrieved. Compare long-context and retrieval-assisted configurations on actual quality, freshness, permissions, latency, and total cost. Published comparisons concern specific models and retrieval setups; they do not support a universal token threshold for switching.

For exact-term misses, test a lexical baseline against dense retrieval and hybrid fusion. RRF combines ranks with `sum(1 / (c + rank))`; Elastic's default is `c=60` and its documentation says RRF requires no tuning, while an analysis by Bruch et al. found RRF sensitive to its parameters and a tuned convex combination of normalized scores outperforming it. Treat the fusion method and constants as hyperparameters to validate on your queries. BEIR found BM25 a robust baseline and re-ranking and late-interaction models best on average at high computational cost; rerank only if final-context evidence retention improves enough to justify the latency you measure.

For incorrect reasoning with sufficient inputs, compare a verified calculation, documented effort settings, stronger model, or checkable subtask. Offload arithmetic and exact rules to tools. Avoid decomposition whose intermediate steps simply add uncertain judgments. Diagnose repeat disagreement under identical evidence and environment before calling it sampling variance: accuracy has been measured to vary by up to 15% across runs of settings expected to be deterministic.

For correct raw responses that become wrong application results, replay a known-good response through streaming assembly, parsing, persistence, and rendering. Fix the adapter. For a correct tool call that fails, execute it directly in a safe fixture and inspect permissions, dependencies, timeouts, and data state.

## Separate shape, evidence, and authority

Use supported constrained generation for machine-consumed responses. Read the provider's current schema rules: OpenAI strict schemas require all fields to be required (optional values are emulated with a null union), while Anthropic's supported subset differs. Explicitly model absent evidence with nullable values or statuses instead of requiring invented values.

Check the completion envelope before parsing. Refusal and incomplete output require distinct paths: OpenAI exposes refusals and finish reasons, and Anthropic documents `stop_reason: "refusal"`. Then validate field associations, units, computed versus quoted values, and business constraints. A syntactically valid price is not a supported price, and a schema-valid tool call is not authorization to execute it.

Carry source/chunk IDs and document versions. Check citation membership and support for the associated claim; an existing citation may still support the wrong claim (an audit of generative search engines found 74.5% of citations supported their sentence and 51.5% of sentences were fully supported). Retain verbatim spans for critical extraction. A claim can require several sources, so do not enforce exactly one citation regardless of synthesis. Whether the retrieved context suffices is a separate property to measure: Sufficient Context (ICLR 2025) found strong models often answer rather than abstain when context is insufficient, so evaluate answerable, missing-evidence, and conflicting-evidence cases.

XML and JSON help organization, but injected directives can appear inside either. Separate model-readable external content from executor authority. Enforce tenant/object/action/destination permissions, scoped credentials, and relevant sandbox/egress restrictions outside the model. Preserve access control and provenance when oversized results become fetchable references. Use concrete approval or preauthorized bounded policies for consequential actions; avoid asking again for actions already authorized. Refer these controls to `advise-harness`.

## Choose recovery by cause

| Failure | Recovery | What to measure |
|---|---|---|
| Transient transport/service error | Bounded backoff with jitter | Exhaustion rate, tail latency, duplicate effects |
| Unsupported schema or parameter | Fix configuration | First-attempt validity on deployed configuration |
| Truncated output | Fix output/context budget | Completion rate and semantic completeness |
| Repairable semantic violation | Return specific validation feedback; bound repair attempts | First-attempt and repaired success separately |
| Missing or conflicting evidence | Clarify, retrieve, abstain, or expose conflict | Coverage, unsupported claims, appropriate abstention |
| Refusal | Use documented handling or an appropriate permitted fallback | Refusal cause and user outcome |
| Uncertain write result | Inspect state or use idempotency | Correct state and absence of duplicate effects |

## Escalate from trustworthy measurements

Sample multiple candidates when a verifier or selector can identify useful answers. Self-consistency has evidence on reasoning benchmarks; majority selection returns the most common answer, so it cannot repair an error shared across samples. Evaluate the selection procedure; any-success rates alone do not establish deployable quality.

GEPA is a supported optimization candidate, not a universal best method. Optimize development cases, select candidates separately, and confirm on held-out release cases. Compare routing and training only when cheaper interventions plateau. Fine-tuning can improve extraction, tool behavior, task skills, or reasoning as well as style; for injecting knowledge, the cited comparisons found retrieval outperforming unsupervised fine-tuning, especially for less popular facts. Use `advise-fine-tune` for the data and maintenance decision.

Estimate cost per successful task including inference, retrieval/tools, retries, human handling, operations, and amortized engineering/training. Compare coverage and failure severity alongside cost; an abstaining system must not look efficient merely because it declines harder requests. Remove components whose measured value does not justify complexity or risk. Agentic designs trade latency and cost for task performance, and Anthropic reports about 4× the tokens of a chat for an agent and about 15× for a multi-agent system, so cost belongs in the comparison.
