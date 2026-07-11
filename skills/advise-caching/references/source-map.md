# Source Map

| Claim | Sources | Confidence | Scope and caveat |
|---|---|---|---|
| Stable prompt prefixes reduce provider-side cost and latency; breakpoints/eligibility are provider-specific. | [S-001](https://platform.openai.com/docs/guides/prompt-caching), [S-002](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | High | Minimum cacheable lengths, TTLs, and pricing are provider- and version-specific; re-check before relying on numbers. |
| Semantic caching can cut LLM cost/latency on repetitive chat traffic. | [S-003](https://arxiv.org/abs/2406.00025) (SCALM), [S-004](https://arxiv.org/abs/2411.05276) (GPT Semantic Cache) | Medium | Papers report workload-specific hit rates; do not generalize without measuring your own traffic. |
| Semantic caches need explicit thresholds and accuracy measurement to avoid false hits. | [S-003](https://arxiv.org/abs/2406.00025), [S-005](https://github.com/zilliztech/GPTCache) | Medium | GPTCache is a reference implementation, not evidence of safety; false-hit budgets are product decisions. |
