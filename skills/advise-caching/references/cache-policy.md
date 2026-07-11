# Cache Policy Reference

Use this file when implementing an exact or semantic response cache. It covers eligibility, key design, invalidation, semantic-cache threshold tuning, and audits.

## Eligibility Checklist

A request class is cache-eligible only if every answer is **yes**:

1. Would two users (or the same user twice) legitimately receive the same answer for this request?
2. Is the answer stable for at least the intended TTL?
3. Is the answer free of per-user permissions, entitlements, or private data?
4. Is a wrong reuse recoverable (user can retry, no irreversible action follows)?
5. Can you attribute the answer to source versions so it can be invalidated?

Route everything else — personalized, permissioned, time-sensitive, or high-stakes traffic — around the cache unconditionally. Encode this as an explicit allowlist of intents or routes, not a blocklist; new request types should default to *not cached*.

## Cache Key Design

The key must capture every input that changes the answer:

| Dimension | Example value | Why it matters |
|---|---|---|
| Normalized request | lowercased, whitespace-trimmed text | Near-identical requests should collide only when meaning is identical |
| Prompt/template version | `support-v14` | A prompt edit changes answers; old entries become wrong silently |
| Model + version | `claude-sonnet-4-5` pinned ID | Different models produce different answers |
| Retrieval/tool state | index build ID, doc-set hash | Answer derived from data that can change |
| Tenant/user scope | `tenant:acme` | Prevents cross-tenant leakage by construction |
| Locale + output format | `en-US`, `json-v2` | Same question, different valid answers |
| Safety/policy version | `policy-2025-11` | Policy changes must not serve pre-policy answers |

Missing dimensions cause wrong-answer reuse; superfluous dimensions only cost hit rate. When in doubt, include it.

## Invalidation Decision Table

| Situation | Strategy |
|---|---|
| Source data emits change events (CMS publish, DB trigger, index rebuild) | Event-driven eviction keyed to the retrieval-state dimension |
| Data changes on a known cadence (nightly sync) | TTL aligned to the cadence, evict-on-sync as a backstop |
| No change signal at all | Conservative TTL derived from "how long until wrong answers embarrass us" |
| Answer may be served stale during recompute | Stale-while-revalidate, plus a visible "as of" timestamp when user-facing |
| Negative/empty results | Short TTL (minutes, not hours) — absences go stale fastest |

## Semantic Cache Threshold Tuning

Never pick a similarity threshold by feel. Protocol:

1. Collect 500–1,000 production query pairs: for each incoming query, the nearest cached query and its answer.
2. Have humans (or a strong reference model with human spot-checks) label each pair: *same answer valid* / *invalid*.
3. Sweep the threshold and plot hit rate vs. false-hit rate. Pick the threshold at your false-hit budget — for most products that budget is well under 1%, and for anything high-stakes it is zero (meaning: don't semantic-cache that traffic).
4. Re-run the sweep whenever the embedding model, prompt version, or traffic mix changes.

Threshold alone is insufficient — combine with the eligibility allowlist, namespace filters applied before similarity search, and exact matching on prompt/model versions.

## Ongoing Audit

- Sample 1–5% of semantic-cache hits into a review queue; label validity weekly.
- Alert on hit-rate cliffs (prefix broke) and hit-rate spikes (threshold or eligibility bug).
- Log the cache layer that served every response so incidents can be traced to a layer in one query.
- Re-verify provider prompt-cache behavior (minimum lengths, TTLs, pricing) after provider announcements; treat those parameters as version-sensitive, per the source map.
