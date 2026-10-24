# Design

## Layers

1. `instructions/engineering.md` defines teaching style, evidence standards, and the
   advisory boundary for Mentor, Architect, and Reviewer only. Each agent embeds the
   agreement directly in its Markdown system prompt; validation detects copy drift.
   The reference symlink is not added to OpenCode's global `instructions` array.
2. OpenCode Markdown agents define conversational focus and native permissions.
   All three are primary, use the user's model, and deny delegation. Identical
   permission frontmatter is intentionally explicit; the validator detects drift.
3. Portable skills define focused task workflows with standard Agent Skills metadata.
   They respect the selected agent's role rather than making every agent advisory.
   They avoid host tool call syntax. The optional session-helper section in onboarding
   is explicitly OpenCode-specific and uses a colocated adapter template.
4. Project instructions define local facts and conventions. Project-specific context
   stays in the project, separate from globally symlinked toolkit files.

There is no prompt compiler, plugin, daemon, or automatic agent router. A future tool
adapter can consume the same skills with its own native permissions and role definitions.
Installation currently publishes skills only to OpenCode's global skill directory.

## Write authorization

The three toolkit agents are advisory even when the user requests production implementation.
Standard Build and other agents retain their normal permissions; users select Build
when they want AI implementation. The installer does not change the default agent or
add global permissions, policies, or advisory instructions.
Small explanatory snippets are acceptable in chat. Editing project files is limited to:

- Explicitly requested informational documentation, preserving unrelated content.
- Genuine test files/test-local helpers for explicitly requested, described test cases.
- A previewed, confirmed project-root `opencode.sh` or `opencode.txt` session helper.

Onboarding can draft in chat or save explicitly requested documentation. Documents
may include small examples, not disguised implementations, executable Markdown/MDX,
scripts, or application-consumed templates. Agent definitions and toolkit policies are
configuration, not documentation exceptions. Project AGENTS.md must not weaken the
selected advisory agent's boundaries or copy them to Build and other agents.
The helper is a narrowly requested artifact exception, separate from test writing
and documentation. None of these exceptions authorizes source
fixes, dependency installation, lockfiles, snapshot updates, or configuration changes.
The toolkit's own installation writes global configuration under the user's installer
invocation; that is separate from advisory agents operating in a project.

Permissions cannot recognize the intent of arbitrary test code. Native rules deny
ordinary edits and prompt for conventional test paths and `.md`/`.txt` documentation.
Protected configuration and toolkit paths have later deny rules. The shared policy
requires scenario authorization for tests and checks documentation's purpose and content,
even where a path matches. Paths cannot enforce either semantic distinction. Unknown
tools (including MCP writes and Code Mode execution) are denied. Shell requires
approval and must not be used to bypass the policy. Existing approval persistence,
project overrides, and managed configuration mean effective native behavior must be
tested; a Markdown policy alone is not a sandbox guarantee.

## Instruction interaction

Use agent-local policy for advisory behavior, project AGENTS.md for domain constraints and commands,
and skills for workflow steps. This is a responsibility model, not an invented common
instruction hierarchy. OpenCode combines sources; avoid conflicting instructions and
surface conflicts rather than interpreting local auto-fix rules as new authorization.
Review project agent overrides when a toolkit role behaves differently than expected.
Loading a skill does not change roles. A plan or review alone does not authorize edits,
but Build can carry out separately requested implementation without inheriting advisory
test-writing restrictions. Avoid copying agent policies into project-wide context.

## Installation ownership

Individual skill directories and agent files are symlinked so neighboring user assets
can coexist. The installer preflights collisions, validates JSONC before edits, and
checks v2 before mutation. It does not adopt unowned links, even identical ones.

JSONC edits target top-level values and preserve unrelated comments and settings.
Comments inside a replaced `instructions` array are replaced with that array value.
An atomic private manifest records owned destinations and agent-local activation.
Atomic per-file replacements reduce partial-write risk; this is not a filesystem-wide
transaction. Ownership is recorded before link/config mutation for recovery.

Uninstall removes only matching owned links and installer-added schema metadata.
Install, reinstall, and uninstall preserve the selected default and unrelated configuration.
For legacy manifests, install/uninstall removes only the recorded installer-added
global instruction and restores the recorded prior default if it is still `mentor`.
Choosing Mentor again after legacy installation is indistinguishable from leaving the
installer-selected value; migration restores the prior default in either case. Migration
completion is recorded after config writes so interrupted upgrades can retry cleanup.
User-managed instruction entries are left intact and flagged by doctor for inspection.
Uninstall leaves directories/config files in place rather than assuming they are unused.

## Evolution

Improve the existing workflows using real conversations and the behavior rubric before
adding roles. Add Language Specialist or Product Strategist only for a distinct focus
or tool policy. Keep measured bottlenecks and real requirements ahead of orchestration
or packaging abstractions.
