# LLM judge reference

## Judge contract

```text
Evaluate only [criterion].
Use only [provided references/context].
Do not judge style, verbosity, or outside knowledge unless the criterion requires it.
Extract the material claims or decision requirements.
Match each to evidence, record unsupported or contradicted items, then score the rubric.
Return JSON only: {score, label, evidence, failures}.
```

Prefer binary or small ordinal scales with anchored examples. Split groundedness, completeness, relevance, and tone into separate graders when their evidence differs. Avoid a single “overall quality” judge.

## Calibration protocol

Sample clear passes, clear failures, borderline cases, different lengths/styles, and multiple model families. Have at least two humans label a subset when stakes justify it, adjudicate disagreements, and compare the judge to the consensus. Track false-pass and false-fail rates by risk category, not only overall agreement.

For pairwise judging, randomize answer order and run order-swapped checks. A judge that changes its preference when only the position changes is not ready to gate releases. Also probe concise correct answers, verbose wrong answers, persuasive unsupported answers, and answers from the judge’s own model family.

LLM judges are useful scalable graders, but human labels remain necessary for calibration and for discovering judge failure modes. Use execution checks and claim-level verification wherever a semantic judge can be replaced by an external verifier.
