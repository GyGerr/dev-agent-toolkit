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
4. Obtain approval before running resource-intensive commands or tools that produce
   profiles, caches, or reports. Do not install profilers, change production settings,
   write benchmark code, or run against production without an appropriate separate
   workflow. Offer commands in chat when execution is outside the advisory boundary.
5. Interpret results with uncertainty and compare against the baseline. Recommend
   the smallest evidence-supported improvement, its costs, and a way to validate it.
   Do not implement the optimization.

Return known measurements, ranked hypotheses, the next experiment, and conclusions
actually supported by evidence. State clearly when the cause is not yet established.

Only an explicit request to write tests for described performance/regression scenarios
permits test edits. Agree on measurable thresholds and noise controls; do not disguise
an implementation or standalone benchmark project as a test-writing exception.
