---
name: design-challenge
description: Constructively challenge a proposed design or engineering decision by examining assumptions, failure modes, and simpler alternatives. Use when asked to critique an idea, stress-test a decision, or act as a devil's advocate; not for a full repository architecture inventory.
---

# Design challenge

1. Restate the proposal and intended outcome charitably. Identify constraints and
   what the user wants challenged. Do not turn an exploratory idea into a commitment.
2. Separate facts, assumptions, and preferences. Find the few assumptions whose
   failure would materially change the design.
3. Test those assumptions against concrete workloads, failure cases, maintenance
   costs, and repository evidence. Include a simpler baseline and explain where it
   succeeds or falls short.
4. Present the strongest case for the proposal as well as its strongest objections.
   Avoid contrarianism, imagined scale requirements, and complexity for its own sake.
5. Recommend retaining, simplifying, or revisiting the design. Give a small experiment
   or decision criterion that would resolve the most important uncertainty.

Return the proposal's strengths, ranked challenges, alternatives, and a decision
test. Adapt the depth to the stakes and reversibility of the decision.

Described experiments are proposals, not authorization to execute them or change files.
Follow the selected agent's authorization boundaries: toolkit advisory agents require
explicit test-writing requests with described cases; Build may carry out separately
requested coding work under its normal permissions. Loading this skill does not change
the agent's role or impose toolkit-wide restrictions.
