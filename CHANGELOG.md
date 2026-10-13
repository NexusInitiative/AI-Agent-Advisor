# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- `advise-debug` skill: symptom-first diagnosis of wrong AI answers when the failing component is unknown. A five-step workflow (pin the failure, rule out the measurement, localize with one controlled substitution, open the matching recipe, fix one component and verify) and 32 recipes across retrieval and grounding (R1–R8), training and adaptation (T1–T6), prompt and output (P1–P7), agents and systems (A1–A8), and evaluation-system defects (E1–E3). Every recipe lists a discriminating test, ranked causes with fixes, verification, and what not to do, with sources in its own `source-map.md`.
- `advise-prompting`: failure-first diagnostics (controlled substitutions, explicit missing-evidence behavior, shape-versus-semantic validation, failure-specific recovery) with two new references, `failure-first.md` and `failure-first-measurement.md`, and an expanded source map.
- `advise-rag`: `references/architecture-selection.md` (long context versus RAG and an escalation ladder keyed to measured failures) and the previously missing `references/source-map.md`.
- `scripts/validate_skills.py` now fails when a skill lacks `references/source-map.md`.
- `CONTRIBUTING.md` sourcing rules: no numeric threshold without a source, derived and procedural statements labeled, venues named only when the paper states one, quoted figures checked against full text.

### Changed

- `advise-rag`: corrected claims that the cited sources do not support: the Contextual Retrieval figures (35% for contextual embeddings alone, 49% with contextual BM25, 67% with reranking), the RAGTruth taxonomy (four types in two families, not three), the GraphRAG evaluation (LLM-judged win rates, not "near-zero" baseline scores), Self-RAG reflection tokens, CRAG's Correct/Incorrect/Ambiguous actions, the Fusion-in-Decoder claim, and the "RRF is robust and needs no tuning" claim (a tuned convex combination beat RRF in one analysis). Removed unsourced thresholds (fixed precision, recall, and faithfulness cutoffs, evaluation-set sizes, reranker latency figures, ANN recall figures). Added stage-wise diagnosis, evidence on semantic versus fixed-size chunking, late chunking, proposition and hierarchical retrieval, visual-document retrieval, adaptive and agentic retrieval, retrieval security, and stage-wise evaluation.
- `advise-fine-tune`: LoRA claim reconciled with evidence that it underperforms full fine-tuning on code and math while forgetting less; added evidence on forgetting, safety erosion, new-knowledge hallucination, memorization, and checkpoint selection; hosted fine-tuning availability corrected (OpenAI is winding down its platform).
- `advise-eval`, `advise-multi-agent`, `advise-context`, `advise-caching`, `advise-models`, `advise-memory`, `advise-vector-db`, `advise-harness`, `advise-embedding`: unsourced numeric heuristics replaced with sourced figures or with instructions to measure; new evidence and source-map entries added; cross-links to `advise-debug` added.
- `README.md`, `AGENTS.md`, and the plugin manifests now describe thirteen skills.
