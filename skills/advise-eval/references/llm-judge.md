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

## Judge Cost and Placement

Judges are the most expensive grader class, so place them last in the grading pipeline: deterministic checks reject invalid outputs first, reference checks decide clear-cut correctness, and only surviving cases reach the judge. This ordering typically cuts judge spend severalfold and — more importantly — keeps the judge answering only the question it was calibrated for. Cache judge verdicts keyed by (case ID, output hash, judge version) so re-runs of unchanged outputs are free and historical comparisons stay stable.

## When the Judge and Humans Disagree

Persistent judge-human disagreement on a category is signal, not noise: either the rubric is ambiguous (fix the rubric and recalibrate), the humans disagree with each other too (fix the labeling guide), or the property genuinely requires expertise the judge lacks (route that category to human review permanently). Record which of the three it was — the pattern across categories tells you how far the judge can be trusted to expand.
