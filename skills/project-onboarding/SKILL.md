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
    execution. Follow the selected agent's approval rules for commands that may produce
    artifacts or change state.
4. Explain ownership boundaries, dependency direction, persistent state, conventions,
   and important gotchas, citing paths and symbols. Distinguish facts from inferences.
   Ask focused questions about unresolved intent rather than inventing architecture.
5. Prepare concise project guidance using [assets/AGENTS.md](assets/AGENTS.md).
   Preserve useful existing content and show a proposed revision if a file exists.
   Offer the optional [assets/architecture.md](assets/architecture.md) for deeper
   context. Replace placeholders with supported facts or explicitly marked unknowns.

Project context belongs to the project: avoid machine-specific toolkit paths, copied
global policies, exhaustive file inventories, and claims about checks never run.
Draft in chat unless the user explicitly requests saving or updating documentation.
For requested saves, inspect the existing file, preserve unrelated content, and use the
host's edit approval. Documentation is informational: small examples are fine, but do
not disguise an implementation or executable template as documentation. Do not weaken
the selected agent's boundaries or copy advisory restrictions into AGENTS.md, where
they would also affect Build and other agents.

Follow the selected agent's authorization boundaries. Toolkit advisory agents remain
advisory; Build may perform separately requested coding work under its normal permissions.
Loading this skill does not change the agent's role or impose toolkit-wide restrictions.

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
    edit .gitignore, or treat helper confirmation as authorization for other files.
    Explain that the helper is normally
   personal/local and let the user decide whether to version it.

If host permissions prevent saving, provide the exact content in chat for the user.
Onboarding itself grants no test-writing or implementation authorization. For separately
requested tests or implementation, follow the selected agent's permissions and policy.
