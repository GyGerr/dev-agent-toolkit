---
name: feature-roadmap
description: Turn a feature goal into a small, testable delivery roadmap with acceptance criteria, dependencies, and trade-offs. Use for feature planning, scope decisions, and incremental rollout; not for automatically implementing a feature.
---

# Feature roadmap

1. Identify the user problem, desired outcome, constraints, and explicit non-goals.
   Distinguish a requested solution from the underlying need. Ask about gaps that
   change scope; record assumptions for less consequential unknowns.
2. Inspect relevant project boundaries and existing capabilities when a repository
   is available. Ground proposed touchpoints in actual files rather than inventing
   services, APIs, or abstractions.
3. Propose the smallest useful end-to-end slice. Break later work into independently
   verifiable increments with dependencies and reasons for ordering.
4. Give each increment acceptance criteria expressed as observable scenarios, likely
   touchpoints, verification ideas, and relevant migration or rollout considerations.
   Mark estimates as provisional; avoid unsupported calendar commitments.
5. Surface consequential product and technical trade-offs, unresolved decisions,
   and what can be deferred. End with the next decision or experiment.

Return the outcome and scope, ordered increments, acceptance criteria, risks, and
open questions. Keep the plan proportionate to the feature. Product strategy can be
handled in this workflow until a separate specialist has a demonstrated purpose.

Planning does not authorize implementation or file creation. Acceptance criteria are
not permission to write tests: the user must explicitly request test writing and
describe or explicitly adopt the scenarios to cover.
