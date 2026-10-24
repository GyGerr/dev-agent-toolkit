# Engineering advisory toolkit

A globally installed, **OpenCode v2** toolkit for engineering mentorship, architecture
consulting, code review, feature planning, and language understanding. Skills are
portable Markdown workflows; OpenCode-specific roles and permissions live separately.

## tl;dr setup and guide

### 1. Install once

Check that `opencode --version` reports **2.x** and Python **3.10+** is available.
From this toolkit's checkout, run:

```sh
sh install.sh install --dry-run
sh install.sh install
sh install.sh doctor
```

Quit and restart OpenCode after installation. Keep the toolkit checkout in a stable
location because the global installation uses symlinks.

### 2. Open your project

```sh
cd /path/to/your/project
opencode
```

**Mentor** is the default. Choose a specialist at startup when useful:

```sh
opencode --agent architect
opencode --agent reviewer
```

The agents and skills are global; onboarding inspects the repository where you launch
OpenCode. Each project's context and resume helper belong to that project.

### 3. Onboard the project

Send this in OpenCode:

> @project-onboarding Inspect this repository, explain its structure, and draft an
> accurate AGENTS.md. Also help me save opencode.sh to resume this session.

Review and apply the `AGENTS.md` draft yourself. For the helper, provide the current
session ID if asked, review the script, and confirm saving it in the project root.
You can find session IDs with `opencode session list`. Each helper stores one chosen
session ID; it does not automatically track your latest session.

### 4. Ask everyday engineering questions

- **Mentorship:** "Explain why this Rust borrowing error occurs."
- **Architecture:** "Review these module boundaries and suggest a simpler design."
- **Code review:** "Review this branch against main for bugs and regressions."
- **Planning:** "Break this feature into small delivery slices with acceptance criteria."

Skills can load automatically. Mention a skill such as `@code-review` when you want
to request its workflow explicitly.

English and Russian are both usable with a model that supports them. The toolkit
instructions are written in English, but there is no English-only restriction. For
predictable Russian responses, start with:

> Отвечай по-русски. Названия API, идентификаторы и команды оставляй в оригинале.

Agent and skill IDs remain English. For example:

> @project-onboarding Изучи этот репозиторий, объясни его устройство и подготовь
> черновик AGENTS.md. Также помоги сохранить opencode.sh для восстановления этой сессии.

Agents stay advisory. To authorize test writing, explicitly request tests and describe
the scenarios:

> Напиши тесты для следующих сценариев: пустой ввод возвращает 0; отрицательное
> значение вызывает ValueError; некорректная строка вызывает ValueError.

### 5. Resume later

From the project directory, run the saved helper:

```sh
sh ./opencode.sh
```

Alternatively, ask onboarding for `opencode.txt` containing
`opencode -s <sessionID>` and run that command from the project root.

## Working style

- Teach the mental model and trade-offs; help you form your own judgment.
- Prefer simple designs grounded in actual requirements and repository evidence.
- Use authoritative, version-aware sources for language semantics.
- Stay advisory, including when asked to implement or fix production code.
- Write tests **only when explicitly asked, with described test cases**.
- Draft project context in chat. Onboarding can separately save a confirmed local
  session-resume helper, as described below.

Test-writing example:

> Write tests for these scenarios: empty input returns zero; negative input raises
> ValueError; malformed input raises ValueError. Use the existing test framework.

"Write tests" needs clarification about cases. "Review and fix", "add coverage", and
tool permission approval do not authorize implementation. A failing regression test
stays a reported failure; agents do not change production code to make it pass.

## Install globally

Requirements: OpenCode **2.x**, Python **3.10+**, and a filesystem supporting symlinks.
Keep this checkout in a stable location. Installation does not require Python packages
outside the standard library.

```sh
sh install.sh install --dry-run
sh install.sh install
sh install.sh doctor
```

The installer:

1. Links all seven skills into `~/.config/opencode/skills/`.
2. Links Mentor, Architect, and Reviewer into `~/.config/opencode/agents/`.
3. Links the shared baseline at `~/.config/opencode/toolkit/engineering.md`.
4. Adds that path to global `instructions` and selects `mentor` as `default_agent`.

Existing JSON/JSONC settings and comments outside the changed values are preserved.
Existing instruction entries are retained. The installer refuses name collisions and
unowned links rather than replacing them. It records ownership and previous default
selection in a private `dev-agent-toolkit-state.json` alongside the global config.
It leaves global `AGENTS.md` files alone and adds the baseline through `instructions`.

`XDG_CONFIG_HOME` is respected. For an explicit global configuration directory:

```sh
sh install.sh install --config-dir "$HOME/my-opencode-config"
sh install.sh doctor --config-dir "$HOME/my-opencode-config"
```

OpenCode must also be configured to use that directory. The installer flag selects
its destination; it does not change OpenCode's environment. `--opencode-bin /path/to/opencode`
selects an executable for the version check. A dry run previews installation even
before v2 is available; actual installation rejects v1 and missing executables.

**Quit and restart OpenCode after installation or configuration changes**, and start
a fresh session to select the new default. V2 also provides `opencode reload` for its
background service; restarting provides a straightforward verification baseline.
Inspect `opencode debug agents` and `opencode debug config` to confirm discovery and
effective configuration. Doctor checks toolkit links and global activation, not every
project or managed override.

### Updates and uninstall

Update this checkout to a chosen release tag or fast-forward it, run checks, then
rerun `sh install.sh install`. Symlinked contents follow the checkout; reinstalling
reconciles the skill/agent inventory. Keep the path stable. To relocate it, uninstall
from the old checkout first and then install from the new location.

```sh
git pull --ff-only
python3 -m unittest discover -s tests/installation -v
sh install.sh install --dry-run
sh install.sh install

sh install.sh uninstall --dry-run
sh install.sh uninstall
```

Uninstall removes owned links and the added instruction entry. It restores the
previous default only if the current default is still `mentor`, preserving later
user choices and unrelated settings. It may leave empty directories and an empty
configuration object. A replaced owned link blocks uninstall for inspection rather
than deleting the replacement. Interrupted installs retain an ownership manifest for
recovery; rerun install or uninstall after resolving the reported problem.

## Everyday use

Select a primary role in OpenCode, or choose one at startup:

```sh
opencode --agent mentor
opencode --agent architect
opencode --agent reviewer
```

| Role | Focus |
| --- | --- |
| Engineering Mentor | Explanations, debugging guidance, learning, engineering judgment |
| Software Architect | System boundaries, dependencies, trade-offs, incremental evolution |
| Code Reviewer | Correctness, idiomatic usage, regressions, maintainability |

All three are primary conversational agents with the same advisory boundary. They do
not delegate. They inherit your selected model rather than pinning a provider/model.

Skills load on demand. In OpenCode v2, mention `@skill-id` to request one explicitly:

| Skill | Example request |
| --- | --- |
| `architecture-review` | "Review our module boundaries and data ownership." |
| `code-review` | "Review this branch against release for correctness." |
| `feature-roadmap` | "Plan password reset as small, testable delivery slices." |
| `language-deep-dive` | "Explain this Rust borrowing error using the language rules." |
| `design-challenge` | "Challenge the need for this generic plugin abstraction." |
| `performance-investigation` | "Help investigate p95 latency before we optimize." |
| `project-onboarding` | "Explain this repository and draft accurate project guidance." |

### Onboarding and session restoration

Onboarding inspects the repository and drafts project-specific `AGENTS.md` and optional
architecture documentation **in chat**, for you to review and apply. It distinguishes
discovered commands, successfully executed commands, and unverified commands.

For a local resume helper, ask:

> Prepare opencode.sh for session ses_abc123. Show me the content before saving it.

After confirming the current session ID, path, and content, onboarding can save:

```sh
#!/bin/sh
set -eu
cd -- "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec opencode -s 'ses_abc123'
```

Run it later with `sh ./opencode.sh`. A plain `opencode.txt` containing
`opencode -s ses_abc123` is also supported; run that command from the project root.
The saved helper is the specific non-test artifact exception. It is not executed
during onboarding. Existing helpers require replacement confirmation. If the current
ID is unavailable, the skill asks you for it; it does not guess the newest session.
Use `opencode session list` to locate the ID. A helper refers to a local session; it
does not back up the session or make it available on another machine.

## Permissions and project context

The shared policy is in [`instructions/engineering.md`](instructions/engineering.md).
Each agent denies tools by default, enables inspection/documentation tools, asks before
shell/external-directory access, and asks before edits to conventional test paths and
the root resume helper. Other edit paths and delegation are denied.

These path rules are an operational backstop, not a semantic test detector: a file in
`tests/` is not necessarily a genuine test, and some projects use other conventions.
The agent must check purpose and scenario-based authorization before proposing an
edit. For unrecognized test paths, it provides test content in chat rather than using
shell to bypass the restriction. Shell approval deserves the same scope review as an
edit, because commands can change files. Test runs may produce caches/reports; those
side effects are handled with a bounded approval.

Put local commands, conventions, and architecture constraints in project `AGENTS.md`.
Keep global teaching preferences in the baseline. Skills provide workflows, not
permission to expand writes. OpenCode combines instruction sources, and projects can
override configuration: use effective-config inspection when behavior differs.
See [design](docs/design.md) and [compatibility](docs/compatibility.md) for details.

## Checks and behavioral evaluation

```sh
python3 -m unittest discover -s tests/installation -v

# With uv (temporary dependency environment):
uv run --no-project --with PyYAML --with jsonschema python scripts/check.py
uv run --no-project --with PyYAML --with jsonschema python scripts/check.py --live-schema

# Or use a virtualenv and requirements-dev.txt:
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/check.py --live-schema
```

Installation tests use temporary directories. The check script validates skill metadata,
supporting references, permission contracts, and optionally the current published
OpenCode schema. These checks do not prove model behavior.

[`tests/scenarios/behavior.json`](tests/scenarios/behavior.json) defines manual behavioral
cases for all roles, including authorization and session-ID edge cases. Follow
[`docs/evaluation.md`](docs/evaluation.md) for native OpenCode runs and review criteria.

## Repository organization

```text
instructions/                 Shared advisory/teaching baseline
skills/<name>/SKILL.md         Tool-independent workflow library
skills/project-onboarding/
  assets/                     Context drafts and OpenCode resume template
opencode/agents/               Native v2 primary roles and permissions
opencode/config.example.json   Minimal activation example
scripts/                      Installer and validation
tests/                        Installation tests, fixtures, behavior scenarios
docs/                         Design, compatibility, evaluation
install.sh                    Python installer entry point
```

Language Specialist and Product Strategist remain future options. Their current
workflows are covered by `language-deep-dive` and `feature-roadmap`; add agents only
when a distinct conversational role is useful.
