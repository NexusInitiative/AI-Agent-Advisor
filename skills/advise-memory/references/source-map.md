# Source Map

Use this reference when citing research or explaining why the skill recommends a pattern.

## Practical Engineering Sources

- LangGraph memory docs: separates short-term thread-scoped memory via checkpoints from long-term memory under custom namespaces. Also provides the semantic, episodic, and procedural split; profile vs collection trade-off; and hot-path vs background write distinction. https://docs.langchain.com/oss/python/concepts/memory
- Letta stateful-agent docs: frames agents as persisted state machines with messages, memory blocks, and tools. Useful for explaining in-context core memory, editable blocks, archival memory, and context hierarchy. https://docs.letta.com/guides/core-concepts/stateful-agents
- Letta memory blocks: supports the always-in-context pattern for small, important, editable or read-only memories. https://docs.letta.com/guides/core-concepts/memory/memory-blocks
- Letta archival memory and context hierarchy: supports the distinction between pinned memory, searchable archival memory, files, and external RAG. https://docs.letta.com/guides/core-concepts/memory/archival-memory and https://docs.letta.com/guides/core-concepts/memory/context-hierarchy
- OpenAI Memory FAQ: useful for product governance: saved memory, chat-history-derived personalization, temporary chat, deletion, and user controls. https://help.openai.com/en/articles/8590148-memory-faq

## Research Sources

- MemGPT: introduces OS-inspired virtual context management: small active context plus larger external tiers managed by the agent. Best citation for "context window as RAM, external memory as disk" and active paging. https://arxiv.org/abs/2310.08560
- Generative Agents: uses observation, retrieval, reflection, and planning. Best citation for recency, relevance, and importance signals, and for reflection as a higher-level synthesis mechanism. https://arxiv.org/abs/2304.03442
- CoALA: provides the clean cognitive architecture frame: modular memory, action space, and decision loop. Useful for taxonomy without tying the skill to one framework. https://arxiv.org/abs/2309.02427
- Reflexion: shows agents improving through verbal reinforcement stored in episodic memory rather than weight updates. Use it to justify outcome-linked reflection memory. https://arxiv.org/abs/2303.11366
- Voyager: demonstrates procedural memory as an executable skill library, especially relevant to coding and tool-using agents. https://arxiv.org/abs/2305.16291
- MemoryBank: demonstrates companion-style long-term memory with importance, reinforcement, and forgetting/decay inspired by the Ebbinghaus curve. Use carefully; decay is a ranking tool, not a substitute for user controls. https://arxiv.org/abs/2305.10250
- LongMemEval: benchmark for long-term chat memory covering information extraction, multi-session reasoning, temporal reasoning, knowledge updates, and abstention. https://arxiv.org/abs/2410.10813
- LoCoMo / Evaluating Very Long-Term Conversational Memory: benchmark for long-term conversations across many sessions, temporal/causal dynamics, summarization, and QA. https://arxiv.org/abs/2402.17753

## How To Cite In Answers

When answering practical architecture questions, cite at most two or three sources:

- For implementation defaults, cite LangGraph or Letta.
- For long-context tiered memory, cite MemGPT or Letta.
- For reflection/procedural memory, cite Reflexion or Voyager.
- For evals, cite LongMemEval and LoCoMo.
- For privacy controls, cite OpenAI Memory FAQ.
