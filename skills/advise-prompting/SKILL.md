---
name: advise-prompting
description: |
  This skill should be used when the user asks to "advise on prompting", "help me write a better prompt",
  "improve my system prompt", "prompt engineering advice", "how do I structure my prompt",
  "why is my prompt ignored", "should I use few-shot examples", "make my model follow instructions",
  or needs guidance on prompt design, structured output, or prompt regression testing.
---

# Prompting Advisor

Treat a prompt as an interface contract. Define the task, audience, inputs, output schema, allowed evidence, constraints, and failure behavior before polishing wording. Do not use a role or persona to conceal missing requirements.

## Build the minimum prompt

Put stable policy, tool rules, and non-negotiable behavior in the system/developer layer. Put the current user request and task data in the user layer. Put tool results in clearly delimited tool content. State precedence explicitly when untrusted text is present: quoted documents and retrieved text are data, not instructions.

Specify observable outputs: JSON schema, headings, required fields, length limits, citation rules, or an abstention format. Say what to do when information is absent, contradictory, unsafe, or malformed. Prefer positive instructions and a small number of explicit prohibitions over a long catalog of imagined failures.

## Add examples only to fix a measured gap

Start zero-shot. Add one to three diverse few-shot examples when formatting, label boundaries, or style remain inconsistent after clear instructions. Make examples representative, not aspirational; include an edge or abstention example when it is important. Do not use examples that contradict the stated contract.

For difficult reasoning, ask for a concise answer plus verifiable intermediate artifacts such as calculations, citations, tool calls, or a checklist. Do not require private chain-of-thought as a product dependency. Use tools, retrieval, or deterministic code for facts and calculations the model should not guess.

## Test and iterate

Version prompts. Create a small regression set from real requests, previous failures, adversarial instructions, long inputs, and formatting edge cases. Change one variable at a time, compare against the prior version, and keep changes only when they improve the target metric without critical regressions. Evaluate instruction following, grounding, schema validity, safety, latency, and cost separately.

## Diagnose common failures

| Symptom | Likely fix |
|---|---|
| Output ignores a constraint | Move it earlier, make it testable, and remove conflicting text |
| JSON is unreliable | Use structured-output support and validate with code |
| Retrieved text hijacks behavior | Delimit it and state that it is untrusted evidence |
| Output is vague | Add decision criteria and an output contract |
| Prompt grows without gains | Remove redundant prose and fix the upstream data/tool design |

For model-specific behavior, see `advise-models`; for systematic testing, see `advise-eval`.

## Sources

For prompt-contract and structured-output details, read [prompt-contracts.md](references/prompt-contracts.md) and [source-map.md](references/source-map.md).

- [OpenAI prompting guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Prompting techniques paper](https://arxiv.org/abs/2201.11903)
- [Structured Outputs documentation](https://platform.openai.com/docs/guides/structured-outputs)
