---
name: advise-caching
description: |
  This skill should be used when the user asks to "how should I implement caching",
  "advise on prompt caching", "help with LLM caching strategy", "reduce API costs with caching",
  "KV cache guidance", "should I use semantic cache", "why are cache hits low",
  or needs guidance on cache keys, invalidation, cost, latency, or response reuse for AI applications.
---

# Caching Advisor

## Step 1 — Diagnose Before Caching

Cache only when repeated work is measurable and a stale or incorrect reuse is acceptable. Before recommending any cache layer, ask or infer:

**About the traffic:**
- What fraction of requests share a large stable prompt prefix (system prompt, tools, reference docs)?
- What fraction of requests are exact or near-duplicates of earlier requests?
- Is the workload latency-sensitive, cost-sensitive, or both?

**About correctness:**
- What happens if a user receives an answer generated for a slightly different question? Annoyance, or a wrong medical/financial/policy answer?
- Is any response personalized, permissioned, or time-sensitive?
- Does the source data behind answers change? How often, and is there an event you can hook invalidation to?

**About the current baseline:**
- Do you have per-request token, cost, and latency numbers? Without them you cannot tell whether a cache is paying for itself.

The answers determine which of the four cache layers below applies. Teams that skip this step usually build a semantic cache first — the layer with the worst correctness risk — while leaving free provider-side prefix caching on the table.

---

## Step 2 — Take Provider Prompt Caching First (It's Nearly Free)

Provider prompt caching reuses server-side computation for a repeated prompt *prefix*. It changes cost and latency, never the response content, so it is the only cache layer with essentially no correctness risk. Do this before anything else:

1. **Order the prompt for stability.** Put tools, system instructions, and static reference content first; put per-request user data last. The cacheable prefix must be byte-for-byte identical between requests — a timestamp, request ID, or reordered tool list at the top silently kills every hit.
2. **Mark cache breakpoints where the provider requires them** (e.g., Anthropic's `cache_control` blocks) or rely on automatic prefix caching where offered (e.g., OpenAI). Minimum cacheable lengths, TTLs, and pricing differ by provider and change over time — check the current [Anthropic prompt caching docs](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) and [OpenAI prompt caching docs](https://platform.openai.com/docs/guides/prompt-caching) rather than hardcoding assumptions.
3. **Verify hits in the API response** (cache read/write token counts) instead of assuming. Low hit rates are almost always a prefix-instability bug, not a provider problem.

Note: model KV-cache tuning inside an inference runtime (vLLM, TGI) is an infrastructure concern for self-hosted serving. It follows the same prefix-stability logic but does not replace any application-level policy below.

---

## Step 3 — Add Exact Response Caching for Deterministic Repeats

If the same request arrives repeatedly (canned FAQ queries, classification of recurring inputs, tool results), cache whole responses keyed by a **complete** cache key. Incomplete keys are the number-one source of wrong-answer reuse. Include every behavior-changing input:

- Normalized request text (trim whitespace, casing where meaning allows)
- Prompt/template version and model + model version
- Tool or retrieval state that shaped the answer (index version, document set hash)
- User/tenant scope, locale, output format, safety policy version

Never share a cache across tenants merely because prompts look similar. Store provenance with each entry: created time, TTL, source versions, and the invalidation reason when evicted.

**Invalidation, in order of preference:**
1. **Event-driven** — when the source data changes, evict the affected keys. Requires knowing which sources feed which answers, which the key design above gives you.
2. **Conservative TTL** — when no change event exists. Choose the TTL from how fast the answer can become wrong, not from hit-rate ambition.
3. **Stale-while-revalidate** — serve the old answer while recomputing, only when an explicitly stale answer is acceptable.

Cache negative results ("no results found", refusals) with shorter TTLs — an absence becomes false quickly.

---

## Step 4 — Treat Semantic Caching as a Measured Risk, Not a Default

A semantic cache returns a stored answer when a *new* question is embedding-similar to an old one. It can cut cost dramatically on FAQ-like traffic (see SCALM and GPT Semantic Cache in the source map), but every hit is a bet that "similar question" implies "same correct answer." That bet fails for:

- Personalized or permissioned answers
- Time-sensitive facts
- Questions where one token changes the meaning ("can I…" vs "can't I…", different product versions, negations)
- High-stakes domains (medical, legal, financial)

**Adopt it only with all of these controls:**
- Eligibility rules: only low-risk intents may hit the semantic cache; everything else bypasses.
- Tenant/user namespace filters applied *before* similarity search.
- Prompt-version and model matching in the key, same as exact caching.
- A tuned similarity threshold validated on production-like traffic, measuring the **false-hit rate** (semantically close but wrong answer) — not just hit rate.
- Sampled audits of served hits (human or reference-based).
- A user-visible bypass path (retry/refresh that skips the cache).

If you cannot measure the false-hit rate, do not ship the semantic cache. See [cache-policy.md](references/cache-policy.md) for the eligibility checklist, threshold-tuning protocol, and audit design.

---

## Step 5 — Prove the Cache Pays for Itself

Instrument every layer separately:

- Hit rate and saved tokens/cost per layer
- p50/p95 end-to-end latency with and without the cache, including added lookup latency
- Stale-answer rate and semantic false-hit rate (sampled audits)
- Privacy incidents: any cross-tenant or cross-user serve is an incident to fix immediately, not a metric to trend

A high hit rate is not success if it hides important changes or serves wrong answers. Conversely, a cache layer whose lookup latency exceeds its saved latency, or whose hit rate stays in single digits, should be removed — cache layers are not free to operate or reason about.

---

## Common Failure Modes and Fixes

| Symptom | Likely Cause | Fix |
|---|---|---|
| Provider cache never hits | Unstable prefix (timestamps, IDs, reordered tools) | Move volatile content after the static prefix; verify with cache-read token counts |
| Provider cache hits then stops | Prefix edited by a deploy; TTL expiry between requests | Version prompts deliberately; batch traffic that shares a prefix |
| Wrong answer reused | Incomplete cache key | Add missing dimensions (model, prompt version, tenant, retrieval state) |
| Semantic cache "invents" relevance | Threshold too loose; no eligibility rules | Raise threshold, restrict to low-risk intents, audit hits |
| Cache leaks data across users | Namespace applied after lookup | Filter by tenant/user *before* similarity search or key lookup |
| Cache costs more than it saves | Low-hit layer on cheap/fast requests | Delete the layer; keep only measured winners |
| Answers stay stale after content updates | TTL-only invalidation on changing data | Add event-driven eviction keyed to source versions |

For deciding what belongs in the stable prefix, see `advise-context`. For measuring quality safely, see `advise-eval`.

---

## References

- **Cache eligibility, key design, invalidation, and the semantic-cache audit protocol:** read [cache-policy.md](references/cache-policy.md) when implementing any response-level cache.
- **Verified sources with claims and caveats:** read [source-map.md](references/source-map.md) when citing evidence or re-checking provider-specific details that change over time.
