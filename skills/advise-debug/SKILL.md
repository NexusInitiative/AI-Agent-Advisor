---
name: advise-debug
description: |
  This skill should be used when the user asks "why are my AI's answers wrong", "my model is hallucinating",
  "my RAG answers aren't accurate", "my fine-tuned model got worse", "did I overfit my fine-tune",
  "it worked yesterday and broke today", "my agent keeps looping", "my agent forgets things mid-task",
  "same input, different answers", "my evals say it's fine but users complain", or has an LLM application
  producing bad output and does not know which component (prompt, retrieval, tuned weights, tools, cache,
  memory, or the grader itself) is responsible. It routes a symptom to a discriminating test and a sourced
  fix recipe. For designing one component from scratch, use the matching advise-* skill.
---

# Debug Advisor

**Symptom first, component second, fix third.** A wrong answer is an observation, not a diagnosis. Failures concentrate in identifiable stages (the RAG failure-point catalogue, the multi-agent MAST taxonomy), and an analysis of 1,600+ multi-agent traces concluded that failure is not merely a function of the underlying model: a well-designed system can do better with the same model. So localize the stage before changing the model, the prompt, or the data.

## Step 1 — Pin the failure

Ask or infer:

- What exact input produced what output, and what should have happened?
- How often: every time, intermittently, or only after a change? What changed and when (model version, prompt, index, adapter, data, traffic)?
- Which components sit in the path: prompt, retrieval and index, tuned weights, tools, cache, memory, grader?

Collect artifacts before theorizing: the raw request and response with its stop or finish reason, the prompt as actually rendered, retrieved candidates and the final context with IDs and versions, tool calls and results, and the model, adapter, index, and cache versions. Then repeat the failing case several times with identical inputs. Accuracy has been measured to vary by up to 15% across runs of settings expected to be deterministic, and agents succeed less consistently than single-run scores suggest, so a one-off failure and a repeatable one need different treatment.

## Step 2 — Rule out the measurement

Before blaming the system, check the yardstick. Anthropic reports that a 0% pass rate across many trials with frontier models is most often a broken task, that one model's CORE-Bench score rose from 42% to 95% once grading, specification, and reproducibility bugs were fixed, and that container resource limits alone moved an agentic benchmark by 6 percentage points. Read transcripts of failing and changed cases; check whether the expected answer is right, the task solvable, the grader fair, the set leaked into training, and the difference larger than noise. Recipes E1–E3 in [triage-and-localization.md](references/triage-and-localization.md).

## Step 3 — Localize with one controlled substitution

Change one thing at a time and see whether the failure moves:

| Substitution | If the failure disappears, suspect | If it persists, suspect |
|---|---|---|
| Put the gold evidence in the prompt | Retrieval, ranking, or context selection (R1) | Generation, prompt, or insufficient or conflicting evidence (R2, R3) |
| Remove the evidence (closed-book) | Misleading or wrong context (R3) | Evidence use, or the corpus cannot answer it (R2) |
| Run the base, untuned model with the same prompt | Tuning (T1–T5) | Prompt, data, or retrieval |
| Run the previous model, prompt, or index version | Your change (P3, R8) | A long-standing defect, data, or grader (E1) |
| Score training-like inputs versus fresh held-out inputs | A large gap signals overfitting or leakage (T1) | Distribution or capability |
| Bypass the cache | Cache (A6) | Upstream stages |
| Replay a known-good raw response through the parser | Adapter or parser (P2) | Model output |
| Execute the tool call directly | API, permission, or data state (A1) | The model's call |
| Re-grade a sample by hand | Grader (E1, E2) | System |

A substitution suggests a stage; it does not prove a single cause. Failures can have more than one.

## Step 4 — Open the matching recipe

Each recipe has the same shape: symptom, discriminating test, causes ranked with fixes, how to verify, and what not to do.

| What you see | Recipe | File |
|---|---|---|
| Answer is in my docs but the AI is wrong or says it doesn't know | R1 | [recipes-retrieval-grounding.md](references/recipes-retrieval-grounding.md) |
| Confident answer when the docs don't say | R2 | same |
| Contradicts or adds to the source text | R3 | same |
| Multi-part or multi-document questions fail | R4 | same |
| Stale or conflicting answers | R5 | same |
| Citations are wrong | R6 | same |
| Another user's data appears, or injected text steers answers | R7 | same |
| Quality dropped after a re-index or embedding change | R8 | same |
| Great in training, worse in production | T1 | [recipes-training-adaptation.md](references/recipes-training-adaptation.md) |
| Tuned model got worse at other things | T2 | same |
| Tuned model invents facts | T3 | same |
| Safety behavior weakened after tuning | T4 | same |
| Repetitive, less diverse, or agrees with everything | T5 | same |
| Works in the notebook, fails when served | T6 | same |
| An instruction is ignored, sometimes | P1 | [recipes-prompt-output.md](references/recipes-prompt-output.md) |
| Invalid or truncated JSON | P2 | same |
| Worked on the old model or yesterday | P3 | same |
| Same input, different answers | P4 | same |
| Agrees with a wrong claim from the user | P5 | same |
| Wrong math or logic though the facts are present | P6 | same |
| Few-shot examples made it worse | P7 | same |
| Wrong tool or bad arguments | A1 | [recipes-agents-systems.md](references/recipes-agents-systems.md) |
| Loops, stalls, or runs up cost | A2 | same |
| Loses track in long tasks or chats | A3 | same |
| Multi-agent system fails or is no better than one agent | A4 | same |
| Duplicate emails, charges, or writes after a timeout | A5 | same |
| Cache returns the wrong answer | A6 | same |
| Memory is stale, wrong, or poisoned | A7 | same |
| Retrieved or tool text caused an unauthorized action | A8 | same |
| Evals say fine but users say bad; or score dropped but output looks fine | E1–E3 | [triage-and-localization.md](references/triage-and-localization.md) |

## Step 5 — Fix one component, then verify

1. Change one component. Rerun the failing cases and a regression slice on the same snapshot and compare them as pairs, with standard errors rather than bare rates.
2. Report first-attempt success separately from success after retries or repair, so a fix does not hide a defect.
3. Confirm on cases you did not tune on. Reusing one dataset for repeated selection breaks the assumption behind standard statistical inference.
4. Turn the failure into a versioned regression case, and record the model, prompt, index, adapter, and grader versions beside it.

Finish with: **observed failure → stage localized (and the test that showed it) → cause → smallest fix → verification → regression case.** If the evidence does not point to a cause, say what test would, rather than guessing.

## What not to do

- Do not ask the model to re-check its own answer without external feedback: intrinsic self-correction did not reliably improve reasoning and sometimes hurt.
- Do not read a model's explanation as the cause of its answer: chain-of-thought often omits the influences on the answer.
- Do not raise retrieval depth or agent step limits blindly: more retrieved passages eventually lowered quality, and exceeding the task limit was the dominant agent failure.
- Do not retry a write that may have succeeded; check state or use idempotency.
- Do not judge a prompt on one format or one run: format changes moved accuracy by up to 76 points on one model.
- Do not tune on the set you will report on.

## References

- [triage-and-localization.md](references/triage-and-localization.md): trace checklist, probe details, evaluation-system recipes E1–E3, statistics for comparisons.
- [recipes-retrieval-grounding.md](references/recipes-retrieval-grounding.md): R1–R8. Design details live in `advise-rag`.
- [recipes-training-adaptation.md](references/recipes-training-adaptation.md): T1–T6. Method and data choices live in `advise-fine-tune`.
- [recipes-prompt-output.md](references/recipes-prompt-output.md): P1–P7. Contract design lives in `advise-prompting`.
- [recipes-agents-systems.md](references/recipes-agents-systems.md): A1–A8. Runtime design lives in `advise-harness`, `advise-multi-agent`, `advise-caching`, and `advise-memory`.
- [source-map.md](references/source-map.md): every claim with source, venue, and scope.
