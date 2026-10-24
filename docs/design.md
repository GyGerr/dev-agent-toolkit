# Design

## Layers

1. `instructions/engineering.md` defines teaching style, evidence standards, and the
   advisory boundary. Installation adds it through OpenCode's `instructions` array.
2. OpenCode Markdown agents define conversational focus and native permissions.
   All three are primary, use the user's model, and deny delegation. Identical
   permission frontmatter is intentionally explicit; the validator detects drift.
3. Portable skills define focused task workflows with standard Agent Skills metadata.
   They avoid host tool call syntax. The optional session-helper section in onboarding
   is explicitly OpenCode-specific and uses a colocated adapter template.
4. Project instructions define local facts and conventions. Project-specific context
   stays in the project, separate from globally symlinked toolkit files.

There is no prompt compiler, plugin, daemon, or automatic agent router. A future tool
adapter can consume the same skills with its own native permissions and role definitions.
Installation currently publishes skills only to OpenCode's global skill directory.

## Write authorization

The toolkit is advisory even when the user requests generic production implementation.
Small explanatory snippets are acceptable in chat. Editing project files is limited to:

- Genuine test files/test-local helpers for explicitly requested, described test cases.
- A previewed, confirmed project-root `opencode.sh` or `opencode.txt` session helper.

Onboarding context documents are chat drafts. The helper is a narrowly requested
artifact exception, separate from test writing. Neither exception authorizes source
fixes, dependency installation, lockfiles, snapshot updates, or configuration changes.
The toolkit's own installation writes global configuration under the user's installer
invocation; that is separate from advisory agents operating in a project.

Permissions cannot recognize the intent of arbitrary test code. Native rules deny
ordinary edits and prompt for conventional test paths. The shared policy requires
scenario authorization and genuine test purpose even where a path matches. Unknown
tools (including MCP writes and Code Mode execution) are denied. Shell requires
approval and must not be used to bypass the policy. Existing approval persistence,
project overrides, and managed configuration mean effective native behavior must be
tested; a Markdown policy alone is not a sandbox guarantee.

## Instruction interaction

Use global policy for behavior, project AGENTS.md for domain constraints and commands,
and skills for workflow steps. This is a responsibility model, not an invented common
instruction hierarchy. OpenCode combines sources; avoid conflicting instructions and
surface conflicts rather than interpreting local auto-fix rules as new authorization.
Review project agent overrides when a toolkit role behaves differently than expected.

## Installation ownership

Individual skill directories and agent files are symlinked so neighboring user assets
can coexist. The installer preflights collisions, validates JSONC before edits, and
checks v2 before mutation. It does not adopt unowned links, even identical ones.

JSONC edits target top-level values and preserve unrelated comments and settings.
Comments inside a replaced `instructions` array are replaced with that array value.
An atomic private manifest records owned destinations and prior default selection.
Atomic per-file replacements reduce partial-write risk; this is not a filesystem-wide
transaction. Ownership is recorded before link/config mutation for recovery.

Uninstall removes only matching owned links and its own instruction entry. A later
default-agent choice is preserved. Rerunning installation explicitly reactivates Mentor.
Uninstall leaves directories/config files in place rather than assuming they are unused.

## Evolution

Improve the existing workflows using real conversations and the behavior rubric before
adding roles. Add Language Specialist or Product Strategist only for a distinct focus
or tool policy. Keep measured bottlenecks and real requirements ahead of orchestration
or packaging abstractions.
