---
name: code-review
description: Review a diff, pull request, or specified code for correctness, regressions, idiomatic usage, and maintainability. Use when the user asks for a code review or defect assessment; do not load merely because a conversation contains code.
---

# Code review

1. Establish the review scope and comparison base. Inspect existing uncommitted work
   without changing it. If the intended base is unclear, ask rather than assuming main.
2. Read project instructions, the diff or supplied code, surrounding callers, and
   relevant tests. Trace the behavior behind a suspected defect before reporting it.
3. Prioritize correctness, security boundaries, data loss, regressions, concurrency,
   and missing behavior coverage. Check idioms against the actual language/framework
   version using authoritative references where semantics matter.
4. Separate demonstrated defects, plausible risks needing evidence, and optional
   maintainability suggestions. Do not manufacture findings or elevate personal
   formatting preferences to bugs. Defer formatting enforcement to existing tooling.
5. For each finding, give severity, file and line or symbol, triggering conditions,
   observable impact, and a suggested verification. Explain why it matters. State
   limitations of the review and which checks were actually run.

Lead with findings ordered by impact. If there are none, say so and name meaningful
remaining uncertainties. Offer a small conceptual correction, not a replacement patch.

A review does not authorize edits. If the user explicitly asks to write tests AND
describes the scenarios, write only those tests using the existing framework. Keep
production defects intact and report failing regression tests honestly. "Add coverage"
or a suggested test list alone is insufficient authorization.
