---
name: language-deep-dive
description: Explain programming-language semantics, type systems, ownership, concurrency, runtime behavior, or non-obvious idioms using version-appropriate authoritative sources. Use for deep language questions and surprising compiler behavior, rather than ordinary syntax lookups.
---

# Language deep dive

1. Establish the language, compiler/runtime version, relevant flags, and the user's
   question. Inspect the project's version declarations if available. If unknown,
   state the assumed version and qualify version-sensitive claims.
2. Give the central mental model in direct language. Trace the supplied example
   step by step and distinguish compile-time checks from runtime effects.
3. Consult the official language specification/reference, compiler/runtime docs,
   or official library documentation for important semantic claims. Cite a link and
   the relevant section/version. Use proposals only with their implementation status.
4. Distinguish language guarantees, implementation details, observed measurements,
   and common conventions. Explain undefined, unspecified, or implementation-defined
   behavior precisely when relevant. Do not turn one successful run into a guarantee.
5. Provide a small contrasting example or counterexample in chat. Explain trade-offs
   and limits of the model, then offer an optional prediction exercise or next reading.

If documentation cannot be accessed, identify what is known and what is unverified;
never fabricate quotations or citations. Experiments need approval if they create
files or other artifacts. Normally show reproducible commands in chat instead.

Remain advisory. Only an explicit test-writing request with described cases permits
test file changes under the host's working agreement. This does not authorize fixing
the original program. A language-specialist agent is not required to use this skill.
