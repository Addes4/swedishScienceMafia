# Plans

Design plans written on 3 October 2026, before the one-command loop existed. None was implemented as
written: the project shipped `python -m autoresearch.loop` instead (PR #4; design notes in
[autoresearch/LOOP.md](../../autoresearch/LOOP.md)). They are kept because they record which options
were weighed and why.

| Document | Written | What it proposed | Status | Source |
|---|---|---|---|---|
| [unified-autoresearch-plan.md](unified-autoresearch-plan.md) | 3 Oct, 19:19 | One loop that keeps the evidence for each decision: proposal, falsification, promotion, audit, explanation | Superseded by `autoresearch.loop` | Branch `plan/unified-autoresearch`, local tag `archive/plan-unified-autoresearch` |
| [combined-framework-plan.md](combined-framework-plan.md) | 3 Oct, about 19:30 | One framework built from Falsify, Strategist, Simplify and triage | Superseded by `autoresearch.loop` | Branch `plan-combined-framework`, local tag `archive/plan-combined-framework` |
| [llm-weibull-v1-protocol.md](llm-weibull-v1-protocol.md) | 3 Oct, 22:30 | Pre-registration for a Falsify loop with Claude Sonnet on Weibull bin packing | Never run; no paid call was made | Same branch, as `experiments/PROTOCOL-llm-v1.md` |

The local tags hold the full branches, including draft code; they exist only in the checkout where
the plans were written and were not pushed.
