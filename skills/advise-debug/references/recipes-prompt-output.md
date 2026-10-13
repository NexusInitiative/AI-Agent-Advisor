# Recipes: Prompt and Output (P1–P7)

Same template as the other recipe files. Sources are in [source-map.md](source-map.md); contract design lives in `advise-prompting`. Items marked *(procedure)* are workflow steps rather than findings.

## P1. An instruction is ignored, or followed only sometimes

**Test.** Make the instruction checkable by code (IFEval is built on instructions whose compliance is verifiable), measure compliance across repeated runs, then re-measure after reordering sections, changing delimiters, and moving the instruction to the start or end of the prompt.

**Causes and fixes, most likely first.**

1. *Format sensitivity.* Accuracy differed by up to 76 points on one model when only prompt formatting changed, and the sensitivity persisted with larger models, more few-shot examples, and instruction tuning (Sclar et al., ICLR 2024). Report a range across plausible formats instead of one number.
2. *Ambiguous or contradictory specification.* Poor or ambiguous prompt specifications are one root of failures to follow task requirements in the multi-agent traces analyzed by Cemri et al. Make constraints observable and remove contradictions between instructions and examples *(procedure)*.
3. *Position.* Information in the middle of a long prompt was used less than at the start or end (Lost in the Middle); Claude's documentation recommends long data first and the question last.

**Verify.** Compliance rate over several runs and several formats, with the range reported.

**Do not** judge a prompt on a single formatting variant or a single run.

## P2. Invalid, truncated, or unparseable output

**Test.** Log the stop or finish reason and any refusal flag before parsing, and keep the raw text.

**Causes and fixes.**

1. *Truncation or refusal parsed as data.* OpenAI exposes refusals and finish reasons for structured outputs, and Anthropic documents `stop_reason: "refusal"` and notes that schema compliance holds "in most cases" with refusals as an exception. Branch on these states before parsing; raise the output budget when truncation caused it.
2. *Free-form JSON.* OpenAI's JSON mode guarantees valid JSON, not a particular schema; structured outputs with a schema are the documented way to enforce one. Constrained decoding guarantees structure (Geng et al., EMNLP 2023; XGrammar, MLSys 2025), not that values are true.
3. *Unsupported schema features.* Supported subsets differ by provider: OpenAI requires all fields to be required, with a null union for optional values, and Anthropic documents its own limitations.
4. *Constraints that hurt reasoning.* One study found that format restrictions degraded reasoning, more so as they tightened (Tam et al.). Compare schema-with-reasoning, free-form-then-extract, and the provider's thinking controls on your task.

**Verify.** First-attempt validity and semantic validity (units, IDs, relationships) measured separately.

## P3. It worked on the old model, or yesterday

**Test.** Rerun the frozen regression set on the previous and current versions, with pinned model IDs, and diff outputs.

**Causes and fixes.**

1. *Hosted-model behavior changed.* The same service changed substantially within months: prime-number identification fell from 84% to 51%, instruction following declined, and code outputs had more formatting mistakes (Chen et al.).
2. *API compatibility.* For example, prefilled assistant turns are rejected on newer Claude models with a 400 error (Claude documentation).
3. *Prompt not portable.* Formatting sensitivity does not shrink with model size (Sclar et al.).

**Fix.** Pin versions where the provider allows, rerun the regression set on every change, and re-tune the prompt for the new model rather than assuming it transfers.

## P4. Same input, different answers

**Test.** Run the case many times under fixed settings; score raw-output agreement and parsed-answer agreement separately (the TARr@N and TARa@N metrics of Atil et al.).

**Causes and fixes.**

1. *Platform non-determinism.* Five LLMs configured to be deterministic showed accuracy variation up to 15% across runs, a best-to-worst gap up to 70%, and none was consistently repeatable (Atil et al.).
2. *Sensitivity to prompt details* (P1) and to example order (P7).
3. *Multi-turn unreliability.* In multi-turn conversations all tested models were very unreliable regardless of aptitude (Laban et al.).

**Fix.** Report distributions and use `pass^k` for customer-facing reliability (τ-bench); use self-consistency only where answers can be compared (it raised accuracy on several reasoning benchmarks in Wang et al.); reduce ambiguity in the task.

## P5. It agrees with a wrong claim from the user

**Test.** Build pairs: a neutral question and the same question with the user asserting a wrong premise. Measure how often the answer flips.

**Causes.** Five assistants consistently showed sycophancy, and human and preference-model judgments sometimes favored convincingly written sycophantic responses over correct ones (Sharma et al.). If you tuned with preference data, see T5.

**Fix.** State in the contract that supplied evidence outranks user assertions, keep wrong-premise cases in the evaluation set, and compare candidate models on them *(procedure)*.

## P6. Wrong math or logic although the facts are present

**Test.** Supply the evidence plus an externally verified calculation or intermediate result, and compare configurations (stronger model, more reasoning effort).

**Causes and fixes.**

1. *The model's own arithmetic and reasoning.* Offload exact computation and rules to code or tools.
2. *Self-correction does not substitute for outside feedback.* LLMs struggled to self-correct reasoning without external feedback and sometimes got worse (Huang et al., ICLR 2024).
3. *The explanation is not the cause.* Chain-of-thought can systematically misrepresent the true reason for an answer, and accuracy dropped by up to 36% when inputs contained biasing features that the explanations never mentioned (Turpin et al.); reveal rates for hints were often below 20% (Chen et al.).
4. *Sampling with a checker.* Repeated sampling solved 70.2% of HumanEval problems at 100 samples versus 28.8% for one (Codex paper), which presupposes a verifier such as unit tests to choose a sample; self-consistency can substitute where answers are comparable.

**Do not** ask the model to double-check its answer with no new information.

## P7. Few-shot examples made it worse

**Test.** Run zero-shot against few-shot, then shuffle the example order.

**Causes and fixes.** Few-shot accuracy varied from near chance to near state-of-the-art with the choice of format, examples, and their order, driven by biases such as favoring answers near the end of the prompt, and contextual calibration improved average accuracy by up to 30% absolute (Zhao et al.). Examples mainly convey the label space, the input distribution, and the format; randomly replacing labels barely hurt in the classification and multiple-choice tasks studied (Min et al.). So choose examples that cover the label space and show the output format, check them against the written instructions, and ablate against zero-shot. Documentation differs on how many to use (Claude suggests 3–5; OpenAI suggests trying zero-shot first for reasoning models).
