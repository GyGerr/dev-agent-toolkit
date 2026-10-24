---
name: performance-investigation
description: Investigate measured or suspected latency, throughput, memory, CPU, or allocation problems through baselines, profiling, and controlled experiments. Use for performance diagnosis and benchmark interpretation; not for speculative optimization during unrelated reviews.
---

# Performance investigation

1. Define the symptom and success metric: workload, environment, data size, percentiles,
   concurrency, version, and reproducibility. Ask for missing measurements before
   assuming the bottleneck.
2. Read the relevant execution path and available telemetry. Establish a baseline
   and separate CPU, I/O, contention, allocation, and external-service hypotheses.
   Rank hypotheses by evidence and cost to test.
3. Propose one discriminating measurement at a time using existing tooling. Explain
   expected signals and alternative explanations. Consider warm-up, caching, noise,
   sample sizes, and profiler overhead.
4. Follow the selected agent's approval rules for resource-intensive tools that produce
   profiles, caches, or reports. Do not install profilers, change production settings,
    write benchmark code, or run against production without appropriate separate
    authorization. Offer commands in chat when execution is outside the selected
    agent's permissions.
5. Interpret results with uncertainty and compare against the baseline. Recommend
   the smallest evidence-supported improvement, its costs, and a way to validate it.
    An investigation alone does not authorize implementing the optimization.

Return known measurements, ranked hypotheses, the next experiment, and conclusions
actually supported by evidence. State clearly when the cause is not yet established.

Follow the selected agent's authorization boundaries: toolkit advisory agents write
tests only when explicitly requested for described scenarios, with measurable thresholds
and noise controls; an implementation or standalone benchmark is not a test exception.
Build may implement separately requested optimizations under its normal permissions.
Loading this skill does not change the agent's role or impose toolkit-wide restrictions.
