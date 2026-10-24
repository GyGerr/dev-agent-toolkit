---
name: architecture-review
description: Assess an existing or proposed software architecture against concrete requirements, system boundaries, data flow, and operational constraints. Use for architectural reviews and system design trade-offs, rather than line-level code review.
---

# Architecture review

1. Establish the decision, system scope, users, and constraints. Ask only questions
   that materially affect the recommendation; mark provisional assumptions.
2. Read applicable project instructions, entry points, dependency declarations, data
   models, and relevant deployment configuration. Trace one representative flow.
   Cite files and symbols; distinguish observed structure from inferred intent.
3. Identify ownership boundaries, dependency direction, state, failure modes, security
   boundaries, and operational costs relevant to the decision. Avoid exhaustive
   checklists for small systems.
4. Compare the current approach, the simplest viable improvement, and another option
   only if it is genuinely competitive. Evaluate complexity, migration cost,
   reversibility, observability, and the requirements each option actually serves.
5. Recommend a direction with reasons, limitations, and evidence that would change
   the decision. Prefer incremental changes over a speculative rewrite.

Return a concise system model, evidence-backed risks ordered by impact, a trade-off
comparison, and next validation steps. Include a diagram in chat only when it makes
relationships clearer. Treat unavailable performance or scale data as unknown.

A review alone does not authorize implementation. Save informational architecture
documentation when explicitly requested and permitted by the selected agent. Follow
that agent's authorization boundaries: toolkit advisory agents remain advisory, while
Build may implement separately requested changes under its normal permissions. Loading
this skill does not change the agent's role or impose toolkit-wide restrictions.
