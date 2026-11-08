---
type: llm
focus: last_message
weight: 3
---
PASS only if the response starts the developer decision interview instead of
inventing retry semantics or producing a final plan. It must distinguish facts
the agent should research from developer-owned decisions, ask a numbered
decision question with a recommendation and tradeoff, wait for the developer,
and state that implementation requires later approval of a reviewed revision.
FAIL if it claims approval, implements, presents a completed plan, asks the
developer to locate code facts, or answers the product decision itself.
