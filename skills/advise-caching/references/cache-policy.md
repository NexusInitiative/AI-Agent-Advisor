# Cache Policy

Make cache eligibility explicit. Keys must include tenant scope, prompt/version, model, retrieval or tool state, and output format. Prefer event invalidation to a guessed TTL. Semantic cache hits require a low-risk task, a similarity threshold, and an audit path; bypass cache for personalized, current, authorized, or high-stakes requests.
