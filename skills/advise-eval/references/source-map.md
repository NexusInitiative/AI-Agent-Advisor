# Verified source map

The recommendations in `SKILL.md` were checked against the following primary documentation and original research. URLs are kept here so an agent can re-check time-sensitive details.

- [OpenAI Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices): task-specific evals, production-shaped data, logging, human calibration, continuous evaluation, and comparison/classification/scoring tasks.
- [Anthropic: Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests): measurable multidimensional criteria and choosing code, human, or LLM grading by reliability and nuance.
- [LangSmith evaluation concepts](https://docs.langchain.com/langsmith/evaluation-concepts): component-level evaluation, offline datasets, online traces, experiments, and reference-based versus reference-free evaluation.
- [Ragas available metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/): RAG and agent metric names including context precision/recall, faithfulness, tool-call accuracy, and goal accuracy. Treat metric definitions as library-specific implementations, not universal ground truth.
- [Judging LLM-as-a-Judge](https://arxiv.org/abs/2306.05685): evidence that capable judges can correlate with human preferences while exhibiting biases including position, verbosity, and self-enhancement effects.
- [A Survey on LLM-as-a-Judge](https://arxiv.org/abs/2411.15594): taxonomy and reliability/bias research. Use it as a survey, not as a guarantee that any judge is valid for a specific domain.
- [JudgeBench](https://arxiv.org/abs/2410.12784): evaluates judges on difficult knowledge, reasoning, math, and coding comparisons; supports testing the judge itself rather than assuming it is reliable.
- [Systematic study of position bias](https://arxiv.org/abs/2406.07791): motivation for order randomization and order-swapped checks in pairwise evaluation.

The sample sizes suggested in `SKILL.md` (for example, 20–30 common cases or 50–100 calibration cases) are practical starting points, not statistically universal requirements. Set sample sizes from risk, variance, domain coverage, and the decision’s acceptable error rate.
