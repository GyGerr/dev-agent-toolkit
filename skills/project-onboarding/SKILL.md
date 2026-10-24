---
name: project-onboarding
description: Inspect an unfamiliar repository to explain its structure and draft accurate project-specific AGENTS.md and optional architecture documentation. Also prepare a confirmed OpenCode session-resume helper when requested. Use for repository onboarding and project context generation.
---

# Project onboarding

## Inspect and explain

1. Establish the repository root, user's goals, and areas of interest. Read existing
   AGENTS.md files and other instruction sources before proposing replacements.
2. Inspect manifests, toolchain/version files, CI, entry points, representative tests,
   and relevant deployment/configuration files. Exclude vendored/generated output
   and secrets. Follow a representative request or data flow.
3. Identify build, test, lint, and setup commands from evidence. Label each command
   **discovered**, **executed successfully**, or **unverified**; inspection is not
   execution. Ask before a command that may produce artifacts or change state.
4. Explain ownership boundaries, dependency direction, persistent state, conventions,
   and important gotchas, citing paths and symbols. Distinguish facts from inferences.
   Ask focused questions about unresolved intent rather than inventing architecture.
5. Draft concise project guidance in chat using [assets/AGENTS.md](assets/AGENTS.md).
   Preserve useful existing content and show a proposed revision if a file exists.
   Offer the optional [assets/architecture.md](assets/architecture.md) for deeper
   context. Replace placeholders with supported facts or explicitly marked unknowns.

Project context belongs to the project: avoid machine-specific toolkit paths, copied
global policies, exhaustive file inventories, and claims about checks never run.
These documents remain drafts for the user to apply. Onboarding is not authorization
to write AGENTS.md or architecture documents, including on an explicit docs request;
the toolkit's project-file exceptions are tests and the session helper below.

## Optional session-resume helper (OpenCode adapter)

This step uses the OpenCode host adapter; the repository-inspection workflow above
is tool-independent. If the host is another tool, skip this step.

1. Offer project-root `opencode.sh` (default) or `opencode.txt` containing a resume
   command. Saving needs the user's confirmation. A session ID is a local reference,
   not a transcript export or a session backup.
2. Use the current session ID only if explicitly provided by trusted runtime context
   or by the user. If unavailable, ask the user to provide it. The user can inspect
   `opencode session list` to find it. Do not assume the most recent session is this
   one. Do not create an artifact with an unresolved placeholder.
3. Verify that the ID has the expected `ses_` prefix and only ASCII letters, digits,
   underscores, or hyphens. Confirm an unexpected format rather than interpolating
   arbitrary input into shell. Preview the exact target path and content.
4. For the shell form, use [assets/opencode.sh](assets/opencode.sh), replacing
   `SESSION_ID` with the validated ID. This runs `opencode -s <sessionID>` from the
   helper's directory. Document invocation as `sh ./opencode.sh`; executable mode is
   unnecessary. For text form, save only `opencode -s <validated-session-ID>` and tell
   the user to run it from this project root.
5. Inspect an existing target and ask before replacing it. Save only the chosen helper
   through the edit tool and its approval prompt. Do not execute it, export sessions,
   edit .gitignore, or save any other project files. Explain that the helper is normally
   personal/local and let the user decide whether to version it.

If host permissions prevent saving, provide the exact content in chat for the user.
If tests are separately requested with described scenarios, use the existing test
framework and the host's narrow test-writing policy; onboarding itself grants no
test-writing authorization.
