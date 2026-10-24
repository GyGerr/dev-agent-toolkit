#!/usr/bin/env python3
"""Validate portable skills, advisory permission contracts, and optional live schema."""

import argparse
import fnmatch
import json
from pathlib import Path
import re
import sys
import urllib.request

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "architecture-review", "code-review", "feature-roadmap", "language-deep-dive",
    "design-challenge", "performance-investigation", "project-onboarding",
}


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"Missing frontmatter: {path}")
    head, body = text[4:].split("\n---\n", 1)
    return yaml.safe_load(head), body


def permission(rules, action, resource):
    result = "ask"
    for rule in rules:
        if fnmatch.fnmatchcase(action, rule["action"]) and fnmatch.fnmatchcase(resource, rule["resource"]):
            result = rule["effect"]
    return result


def check(live_schema=False):
    found = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    assert found == SKILLS, f"Unexpected skill inventory: {found}"
    for name in sorted(SKILLS):
        path = ROOT / "skills" / name / "SKILL.md"
        data, body = frontmatter(path)
        assert data["name"] == name and re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name)
        assert len(name) <= 64 and 1 <= len(data["description"]) <= 1024
        assert len(body.splitlines()) < 500 and body.strip()
        assert "Loading this skill" in " ".join(body.split()), f"Missing agent-scope guidance: {name}"
        for target in re.findall(r"\]\(([^)]+)\)", body):
            if "://" not in target and not target.startswith("#"):
                assert (path.parent / target.split("#")[0]).is_file(), f"Missing reference: {target}"
    agents = {}
    canonical_rules = None
    agreement = (ROOT / "instructions/engineering.md").read_text(encoding="utf-8").strip()
    for path in sorted((ROOT / "opencode/agents").glob("*.md")):
        data, body = frontmatter(path)
        assert data["mode"] == "primary" and body.strip()
        embedded = body.split("<!-- BEGIN ENGINEERING AGREEMENT: keep identical to instructions/engineering.md -->\n", 1)[1]
        embedded, remainder = embedded.split("\n<!-- END ENGINEERING AGREEMENT -->", 1)
        assert embedded.strip() == agreement and not remainder.strip(), f"Agreement drift: {path}"
        assert "permission" not in data and "tools" not in data
        rules = data["permissions"]
        assert all(set(rule) == {"action", "resource", "effect"} for rule in rules)
        if canonical_rules is None:
            canonical_rules = rules
        assert rules == canonical_rules, "Advisory permissions drifted between roles"
        for target in ("src/main.py", "package.json", ".gitignore", "src/feature.mdx",
                       ".opencode/agents/build.md", "pkg/.opencode/skills/test/SKILL.md",
                       ".git/config.md", "opencode/agents/mentor.md", "instructions/engineering.md",
                       "/custom/opencode/toolkit/engineering.md", "/custom/opencode/agents/mentor.md",
                       "/custom/opencode/skills/example/SKILL.md", "skills/code-review/SKILL.md",
                       "/custom/opencode/commands/implement.md", "/checkout/skills/example/SKILL.md"):
            assert permission(rules, "edit", target) == "deny", target
        for target in ("tests/test_parser.py", "pkg/tests/helper.py", "test/a.ts", "src/a.test.ts",
                       "src/a.spec.ts", "test_parser.py", "pkg/test_parser.py", "pkg/a_test.go",
                       "__tests__/a.js", "opencode.sh", "opencode.txt", "AGENTS.md",
                       "docs/architecture.md", "ROADMAP.md", "docs/notes.txt"):
            assert permission(rules, "edit", target) == "ask", target
        for action in ("subagent", "untrusted_write", "github_create_pull_request", "execute"):
            assert permission(rules, action, "*") == "deny"
        assert permission(rules, "shell", "python arbitrary.py") == "ask"
        assert permission(rules, "read", ".env") == "ask"
        agents[path.stem] = {**data, "system": body}
    assert set(agents) == {"mentor", "architect", "reviewer"}
    config = json.loads((ROOT / "opencode/config.example.json").read_text(encoding="utf-8"))
    assert config == {"$schema": "https://opencode.ai/config.json"}, "Example must not activate global restrictions"
    scenarios = json.loads((ROOT / "tests/scenarios/behavior.json").read_text(encoding="utf-8"))
    assert len({case["id"] for case in scenarios}) == len(scenarios)
    assert all(case["prompt"] and case["expected"] and case["agent"] in {*agents, "build"} for case in scenarios)
    if live_schema:
        import jsonschema
        request = urllib.request.Request("https://opencode.ai/config.json",
                                         headers={"User-Agent": "Mozilla/5.0 dev-agent-toolkit"})
        with urllib.request.urlopen(request, timeout=30) as response:
            schema = json.load(response)
        jsonschema.Draft202012Validator.check_schema(schema)
        validator = jsonschema.Draft202012Validator(schema)
        validator.validate({**config, "agents": agents})
        print("Published OpenCode schema: configuration and all three agents valid")
    print(f"Validated {len(SKILLS)} skills, {len(agents)} agents, and {len(scenarios)} behavioral scenarios")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-schema", action="store_true", help="Validate against the published schema (network)")
    args = parser.parse_args()
    try:
        check(args.live_schema)
    except (AssertionError, ValueError, KeyError, IndexError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        sys.exit(1)
