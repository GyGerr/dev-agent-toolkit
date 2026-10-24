#!/usr/bin/env python3
"""Install OpenCode-only symlinks and minimally edit JSON/JSONC configuration."""

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "https://opencode.ai/config.json"
STATE_NAME = "dev-agent-toolkit-state.json"


class InstallError(Exception):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InstallError(f"Duplicate configuration key: {key}")
        result[key] = value
    return result


def clean_jsonc(text):
    """Blank comments/trailing commas without changing offsets or string content."""
    chars = list(text)
    i = 0
    while i < len(chars):
        if chars[i] == '"':
            i += 1
            while i < len(chars):
                if chars[i] == "\\":
                    i += 2
                elif chars[i] == '"':
                    i += 1
                    break
                else:
                    i += 1
        elif text.startswith("//", i):
            end = text.find("\n", i)
            end = len(text) if end == -1 else end
            chars[i:end] = " " * (end - i)
            i = end
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end == -1:
                raise InstallError("Unterminated JSONC comment")
            end += 2
            chars[i:end] = ["\n" if c == "\n" else " " for c in text[i:end]]
            i = end
        else:
            i += 1
    i = 0
    while i < len(chars):
        if chars[i] == '"':
            i += 1
            while i < len(chars):
                if chars[i] == "\\":
                    i += 2
                elif chars[i] == '"':
                    i += 1
                    break
                else:
                    i += 1
        elif chars[i] == ",":
            end = i + 1
            while end < len(chars) and chars[end].isspace():
                end += 1
            if end < len(chars) and chars[end] in "}]":
                chars[i] = " "
            i += 1
        else:
            i += 1
    return "".join(chars)


class Config:
    def __init__(self, text):
        self.text = text
        self.clean = clean_jsonc(text)
        try:
            self.data = json.loads(self.clean, object_pairs_hook=unique_object)
        except ValueError as exc:
            raise InstallError(f"Invalid JSON/JSONC configuration: {exc}") from exc
        if not isinstance(self.data, dict):
            raise InstallError("Configuration must be an object")

    def members(self):
        """Return top-level key/value spans, including a possible trailing comma."""
        decoder = json.JSONDecoder()
        i = self.clean.index("{") + 1
        result = {}
        while True:
            while self.clean[i].isspace():
                i += 1
            if self.clean[i] == "}":
                return result, i
            start = i
            key, i = decoder.raw_decode(self.clean, i)
            while self.clean[i].isspace():
                i += 1
            i += 1  # colon (the entire document has already been validated)
            while self.clean[i].isspace():
                i += 1
            value_start = i
            _, end = decoder.raw_decode(self.clean, i)
            i = end
            while self.clean[i].isspace():
                i += 1
            # clean_jsonc blanks the final comma; locate it in comment-free whitespace.
            raw_gap = clean_jsonc("[0" + self.text[end:i] + "0]")[2:-2]
            comma = end + raw_gap.index(",") if "," in raw_gap else None
            if self.clean[i] == ",":
                comma = i
                i += 1
            result[key] = (start, value_start, end, comma)

    def set(self, key, value):
        spans, close = self.members()
        encoded = json.dumps(value, ensure_ascii=False, indent=2)
        if key in spans:
            _, start, end, _ = spans[key]
            text = self.text[:start] + encoded + self.text[end:]
        else:
            text = self.text
            if spans:
                last = list(spans.values())[-1]
                if last[3] is None:
                    text = text[:last[2]] + "," + text[last[2]:]
                    close += 1
            text = text[:close] + f"\n  {json.dumps(key)}: {encoded}\n" + text[close:]
        return Config(text)

    def remove(self, key):
        spans, _ = self.members()
        if key not in spans:
            return self
        start, _, end, comma = spans[key]
        text = self.text
        if comma is not None:
            text = text[:comma] + text[comma + 1:]
        else:
            keys = list(spans)
            index = keys.index(key)
            if index:
                previous_comma = spans[keys[index - 1]][3]
                text = text[:previous_comma] + " " + text[previous_comma + 1:]
        return Config(text[:start] + text[end:])


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
    fd, temporary = tempfile.mkstemp(prefix=".toolkit-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def version(binary):
    executable = shutil.which(binary)
    if executable is None:
        raise InstallError("OpenCode is missing. Install OpenCode v2 before activation.")
    try:
        result = subprocess.run([executable, "--version"], capture_output=True,
                                text=True, check=True, timeout=15)
    except (subprocess.SubprocessError, OSError) as exc:
        raise InstallError(f"Unable to check OpenCode version: {exc}") from exc
    match = re.search(r"\bv?(\d+)\.(\d+)\.(\d+)\b", result.stdout)
    if not match or int(match[1]) != 2:
        raise InstallError(f"OpenCode v2 is required; detected {result.stdout.strip()!r}.")
    return ".".join(match.groups())


def links_for(config_dir):
    links = {config_dir / "toolkit/engineering.md": ROOT / "instructions/engineering.md"}
    for source in sorted((ROOT / "opencode/agents").glob("*.md")):
        links[config_dir / "agents" / source.name] = source
    for source in sorted((ROOT / "skills").iterdir()):
        if (source / "SKILL.md").is_file():
            links[config_dir / "skills" / source.name] = source
    return links


def same_link(path, target):
    return path.is_symlink() and path.resolve() == target.resolve()


def read_state(path):
    if path.is_symlink():
        raise InstallError(f"Refusing a symlinked ownership manifest: {path}")
    if not path.exists():
        return None
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("format") != 1 or state.get("root") != str(ROOT):
        raise InstallError("Ownership manifest belongs to another checkout or format. "
                           "Uninstall using the original checkout first.")
    return state


def config_path(config_dir, state):
    if state:
        return Path(state["config_path"])
    candidates = [config_dir / "opencode.json", config_dir / "opencode.jsonc"]
    existing = [path for path in candidates if os.path.lexists(path)]
    if len(existing) > 1:
        raise InstallError("Both opencode.json and opencode.jsonc exist; consolidate "
                           "them before installation so activation is unambiguous.")
    return existing[0] if existing else candidates[0]


def load_config(path):
    if path.is_symlink():
        raise InstallError(f"Refusing to rewrite a symlinked config: {path}")
    return Config(path.read_text(encoding="utf-8") if path.exists() else "{}\n")


def validate_instructions(config):
    value = config.data.get("instructions", [])
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise InstallError("Existing instructions must be an array of strings")
    return value


def remove_legacy_activation(config, state):
    """Undo only recorded pre-agent-scoping activation, preserving later choices."""
    if not state or state.get("activation_scope") == "agents":
        return config
    instructions = validate_instructions(config)
    if state["instruction_added"] and state["instruction"] in instructions:
        remaining = [item for item in instructions if item != state["instruction"]]
        config = config.set("instructions", remaining) if (
            remaining or state["previous_instructions_present"]
        ) else config.remove("instructions")
    if config.data.get("default_agent") == "mentor":
        config = config.set("default_agent", state["previous_default"]) if (
            state["previous_default_present"]
        ) else config.remove("default_agent")
    return config


def has_global_agreement(config):
    """Recognize concrete global references, including symlink and home aliases."""
    agreement = (ROOT / "instructions/engineering.md").resolve()
    for entry in validate_instructions(config):
        if "://" in entry:
            continue
        path = Path(entry).expanduser()
        if path.is_absolute() and path.resolve() == agreement:
            return True
    return False


def install(config_dir, dry_run, binary):
    state_path = config_dir / STATE_NAME
    state = read_state(state_path)
    path = config_path(config_dir, state)
    config = load_config(path)
    validate_instructions(config)
    links = links_for(config_dir)
    owned = state["links"] if state else {}
    for destination, source in links.items():
        if os.path.lexists(destination) and not (
            str(destination) in owned and same_link(destination, source)
        ):
            raise InstallError(f"Existing destination is not an owned matching link: {destination}")
    for old, target in owned.items():
        if Path(old) not in links and os.path.lexists(old) and not same_link(Path(old), Path(target)):
            raise InstallError(f"Obsolete owned destination has been changed: {old}")

    instruction = str(config_dir / "toolkit/engineering.md")
    new_config = remove_legacy_activation(config, state)
    if "$schema" not in config.data:
        new_config = new_config.set("$schema", SCHEMA)
    print(f"{'Preview' if dry_run else 'Install'}: {config_dir}")
    for destination, source in links.items():
        print(f"  link {destination} -> {source}")
    print(f"  install optional advisory agents; preserve default and global rules in {path}")
    if state and state.get("activation_scope") != "agents":
        print("  migrate recorded global advisory activation to agent-local prompts")
    if dry_run:
        print("Dry run: no files changed. Activation requires OpenCode v2.")
        return
    detected = version(binary)
    if state is None:
        state = {
            "format": 1, "root": str(ROOT), "config_path": str(path),
            "activation_scope": "agents",
            "schema_added": "$schema" not in config.data,
        }
    # Write ownership before mutations so an interrupted install can be uninstalled.
    new_links = {str(dst): str(src) for dst, src in links.items()}
    state["links"] = {**owned, **new_links}
    state["instruction"] = instruction
    atomic_write(state_path, json.dumps(state, indent=2) + "\n")
    for old, target in owned.items():
        if Path(old) not in links and same_link(Path(old), Path(target)):
            Path(old).unlink()
    for destination, source in links.items():
        if not os.path.lexists(destination):
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.symlink_to(source, target_is_directory=source.is_dir())
    if new_config.text != config.text or not path.exists():
        atomic_write(path, new_config.text)
    state["links"] = new_links
    # Mark migration complete only after the configuration has been written, so
    # interrupted upgrades can safely retry the legacy cleanup.
    state["activation_scope"] = "agents"
    atomic_write(state_path, json.dumps(state, indent=2) + "\n")
    print(f"Installed for OpenCode {detected}. Quit and restart OpenCode to load the toolkit.")


def uninstall(config_dir, dry_run):
    state_path = config_dir / STATE_NAME
    state = read_state(state_path)
    if not state:
        print("No toolkit installation is recorded.")
        return
    path = Path(state["config_path"])
    config = load_config(path)
    validate_instructions(config)
    config = remove_legacy_activation(config, state)
    if state["schema_added"] and config.data.get("$schema") == SCHEMA:
        config = config.remove("$schema")
    for destination, source in state["links"].items():
        if same_link(Path(destination), Path(source)):
            print(f"  unlink {destination}")
        elif os.path.lexists(destination):
            raise InstallError(f"Owned link was replaced; preserve or relocate it first: {destination}")
    print(f"  remove toolkit activation from {path}, preserving other settings")
    if dry_run:
        print("Dry run: no files changed.")
        return
    if path.exists():
        atomic_write(path, config.text)
    for destination, source in state["links"].items():
        if same_link(Path(destination), Path(source)):
            Path(destination).unlink()
    state_path.unlink()
    print("Uninstalled. Quit and restart OpenCode to reload configuration.")


def status(config_dir, binary):
    try:
        print(f"OpenCode: {version(binary)}")
        healthy = True
    except InstallError as exc:
        print(str(exc))
        healthy = False
    state = read_state(config_dir / STATE_NAME)
    if not state:
        print("Not installed.")
        return False
    expected = {str(dst): str(src) for dst, src in links_for(config_dir).items()}
    if state["links"] != expected:
        print("Link inventory changed; rerun install after updating the checkout.")
        healthy = False
    for destination, source in state["links"].items():
        okay = same_link(Path(destination), Path(source)) and Path(source).exists()
        print(f"{'OK' if okay else 'BROKEN'} {destination}")
        healthy = healthy and okay
    config = load_config(Path(state["config_path"]))
    active = (state.get("activation_scope") == "agents"
              and not has_global_agreement(config))
    print("Agent-local advisory activation: " + ("OK" if active else "CHECK REQUIRED"))
    if not active:
        print("Rerun install to migrate owned global rules; inspect any user-managed instruction entry.")
    print("Project or managed settings may override globals; inspect OpenCode's resolved config.")
    return healthy and active


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", default="install",
                        choices=["install", "uninstall", "status", "doctor"])
    parser.add_argument("--dry-run", action="store_true")
    default = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "opencode"
    parser.add_argument("--config-dir", type=Path, default=default,
                        help="OpenCode global config directory (default: XDG config/opencode)")
    parser.add_argument("--opencode-bin", default="opencode", help="OpenCode v2 executable")
    args = parser.parse_args(argv)
    directory = args.config_dir.expanduser().resolve()
    try:
        if args.action == "install":
            install(directory, args.dry_run, args.opencode_bin)
        elif args.action == "uninstall":
            uninstall(directory, args.dry_run)
        else:
            return 0 if status(directory, args.opencode_bin) else 1
    except (InstallError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
