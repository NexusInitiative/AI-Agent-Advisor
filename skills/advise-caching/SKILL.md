---
name: advise-caching
description: |
  This skill should be used when the user asks to "how should I implement caching",
  "advise on prompt caching", "help with LLM caching strategy", "reduce API costs with caching",
  "KV cache guidance", "should I use semantic cache", "why are cache hits low",
  or needs guidance on cache keys, invalidation, cost, latency, or response reuse for AI applications.
---

# Caching Advisor

Cache only when repeated work is measurable and a stale or incorrect reuse is acceptable. Start with provider prompt caching and ordinary exact caching; add semantic reuse only after evaluating false hits on production-like traffic.

## Classify the work

- Use **provider prompt caching** for large, stable prompt prefixes such as instructions, tools, and static reference content. Keep the reusable prefix byte-for-byte stable and place changing user data after it.
- Use **exact response caching** for deterministic or nearly deterministic requests with a complete cache key.
- Use **application data caching** for tool results that have a clear source, TTL, and invalidation event.
- Use **semantic caching** only for low-risk tasks where a meaningfully similar prior answer is valid. It is not safe for personalized, authorized, current, or high-stakes decisions by default.
- Treat model KV cache optimization as an inference-runtime concern; it does not replace application-level correctness policy.

## Design the key and lifecycle

Include every behavior-changing input: normalized request, prompt/template version, model/version, tool or retrieval state, user/tenant scope, locale, safety policy, and output format. Never share a cache across tenants merely because prompts look similar. Store provenance, created time, TTL, freshness state, and the invalidation reason.

Prefer event-driven invalidation for changing source data. Use a conservative TTL when events are unavailable. Add stale-while-revalidate only when an older answer is explicitly acceptable. Cache negative results carefully; an absence can become false quickly.

## Evaluate the trade-off

Measure hit rate, saved tokens/cost, p50/p95 latency, added lookup latency, stale-answer rate, semantic false-hit rate, and privacy incidents. A high hit rate is not success if it hides important changes. Use a similarity threshold plus eligibility rules, tenant filters, prompt/model matching, and a bypass path. Sample hits for human or reference-based audits.

## Common failures

| Symptom | Fix |
|---|---|
| Provider cache misses | Stabilize the prefix and check provider eligibility rules |
| Wrong answer reused | Expand the key; tighten scope or TTL |
| Semantic cache invents relevance | Raise threshold; require a low-risk task and validate answers |
| Cache leaks data | Include tenant/user namespace before lookup and storage |
| Cache costs more than it saves | Remove low-hit, low-latency layers |

For context layout, see `advise-context`; for safe measurement, see `advise-eval`.

## Sources

- [OpenAI prompt caching](https://platform.openai.com/docs/guides/prompt-caching)
- [GPTCache documentation](https://github.com/zilliztech/GPTCache)
- [Cache replacement survey](https://arxiv.org/abs/2303.12731)
