# Compatibility and sources

Research baseline: **2026-10-24**. Tool configuration evolves; the published schema
and installed version take precedence over copied examples.

## Supported target

- OpenCode **2.x**, native v2 Markdown agent frontmatter and JSON/JSONC config.
- Python **3.10+** for installation; no installer dependencies outside the standard library.
- POSIX shell for `install.sh` and the session helper; Linux/macOS are the initial targets.
- Symlink-capable filesystem and a stable checkout path.

The development machine reports OpenCode **2.1.4**. Activation rejects v1 and missing
executables. Installation behavior is tested in isolated directories with a mocked v2
version. Native v2 agent/skill discovery and real model/tool behavior require
the smoke tests in [evaluation.md](evaluation.md); schema validity does not establish
runtime compatibility. Version `2.0.21` in unit tests is a fixture, not a tested release.

## Conventions used

| Concern | Convention |
| --- | --- |
| Global config | `$XDG_CONFIG_HOME/opencode/opencode.json(c)`, ordinarily `~/.config/opencode/` |
| Agents | `agents/<name>.md`; body is system text, `mode: primary` |
| Permissions | Ordered `permissions` rules with `action`, `resource`, `effect` |
| Permission actions | `edit`, `shell`, `subagent`; last matching rule wins |
| Global skills | `skills/<id>/SKILL.md`; supporting paths are relative to the skill directory |
| Advisory agreement | Embedded only in the three toolkit agents; never appended to global `instructions` |
| Default role | Existing selection preserved; OpenCode falls back to Build if unset |
| Resume session | `opencode -s <sessionID>` (`--session` long form) |
| Discover session IDs | `opencode session list`; do not infer the current ID from ordering |

V2 accepts some v1 fields for compatibility, but this toolkit writes v2-native fields.
Do not activate its v2 configuration with a v1 binary. The installer does not upgrade
the user's executable. Check current OpenCode installation instructions when upgrading.

V2 instruction discovery differs from v1 and from other tools. It recognizes AGENTS.md,
combines global/project/configured instructions, and discovers nested guidance during
exploration. Avoid assuming that a filename alone implements an override policy.
In particular, putting advisory rules in global `instructions` or project AGENTS.md
would affect Build too. Installations made by the old installer are migrated using
their ownership manifest; manually added global rules require manual review.

## Authoritative sources

- [Agent Skills specification](https://agentskills.io/specification)
- [OpenCode v2 agents](https://opencode.ai/v2/docs/agents/)
- [OpenCode v2 skills](https://opencode.ai/v2/docs/skills/)
- [OpenCode v2 configuration](https://opencode.ai/v2/docs/config/)
- [OpenCode v2 permissions](https://opencode.ai/v2/docs/permissions/)
- [OpenCode v2 instructions](https://opencode.ai/v2/docs/instructions/)
- [OpenCode v2 CLI commands](https://opencode.ai/v2/docs/cli/commands/)
- [OpenCode v1 migration](https://opencode.ai/v2/docs/migrate-v1/)
- [Published JSON schema](https://opencode.ai/config.json)
