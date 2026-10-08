# R1 topic 2: live runs (2026-10-05)

The first live end-to-end runs of `run_research`, in test mode (`LLM_TEST_MODE=true`: Gemini 3.5
Flash-Lite on Google, Tavily, Jev for the claim check), with every `web_search` approval granted
by a wrapper. Script: `mentor/sandbox/r1_topic2_live.py` (sandbox, not committed). One run
each, so the numbers show one sample, not a spread.

| Topic | Options | Seconds | Searches | Reads | Claims (after cap) | Supported | Contradicted | Unsupported | Confidence |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| What is LangGraph's checkpointer and what is it used for? | `quick` | 8.2 | 1 | 1 | 5 | 5 | 0 | 0 | 0.70 |
| How do production teams evaluate RAG systems? | none (one run, no plan) | 13.7 | 1 | 1 | 6 | 4 | 0 | 2 | 0.467 |
| How do production teams evaluate RAG systems? | `standard` (3 sub-questions) | 11.9 | 4 | 4 | 15 (17 drafted) | 10 | 1 | 4 | 0.467 |

What they show:
- Test mode could not build any agent before this session's fix (`make_model_fallback` raised for
  the single-provider `free` tier); these are the first live agent runs since test mode moved there.
- The budgets are far from binding: each run used 1-2 searches and reads of its 5 and 8. The claim
  cap did bind (17 drafted, 15 kept). Budget numbers stay provisional.
- The claim check caught a real model error: "RAGAS provides four core ground-truth-free metrics"
  came back `contradicted` (context recall needs a reference answer).
- Planning tripled the supported facts on the broad topic (4 to 10) in less wall time, because the
  sub-question runs are parallel.
