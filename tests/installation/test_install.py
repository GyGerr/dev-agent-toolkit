"""Behavioral installation tests; all mutations stay inside temporary directories."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("toolkit_install", ROOT / "scripts/install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class VersionTests(unittest.TestCase):
    def detect(self, output):
        result = subprocess.CompletedProcess(["opencode", "--version"], 0, stdout=output)
        with patch.object(installer.shutil, "which", return_value="/usr/bin/opencode"), \
                patch.object(installer.subprocess, "run", return_value=result):
            return installer.version("opencode")

    def test_accepts_bare_and_prefixed_v2_versions(self):
        for output in ("2.1.4\n", "v2.1.4\n", "opencode v2.1.4\n", "opencode 2.1.4\n"):
            with self.subTest(output=output):
                self.assertEqual(self.detect(output), "2.1.4")

    def test_rejects_unsupported_or_unrecognized_versions(self):
        for output in ("1.18.31\n", "opencode v1.18.31\n", "opencode v3.0.0\n", "unknown\n"):
            with self.subTest(output=output):
                with self.assertRaises(installer.InstallError):
                    self.detect(output)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="toolkit test ")
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.config_dir = self.home / "custom config" / "opencode"
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)
        self.version = patch.object(installer, "version", return_value="2.0.21")
        self.version.start()
        self.addCleanup(self.version.stop)

    def install(self, dry_run=False):
        installer.install(self.config_dir, dry_run, "opencode")

    def config(self):
        path = installer.config_path(self.config_dir, None)
        return installer.load_config(path)

    def legacy_install(self, previous_default=None, previous_instructions=None,
                       instruction_added=True):
        """Seed the manifest/config produced by the original global installer."""
        self.install()
        state_path = self.config_dir / installer.STATE_NAME
        state = installer.read_state(state_path)
        state.pop("activation_scope")
        state.update({
            "previous_default_present": previous_default is not None,
            "previous_default": previous_default,
            "previous_instructions_present": previous_instructions is not None,
            "instruction_added": instruction_added,
        })
        instructions = list(previous_instructions or [])
        if state["instruction"] not in instructions:
            instructions.append(state["instruction"])
        config = self.config().set("default_agent", "mentor").set("instructions", instructions)
        Path(state["config_path"]).write_text(config.text)
        state_path.write_text(json.dumps(state))
        return state

    def test_fresh_install_idempotence_and_uninstall(self):
        self.install()
        self.assertTrue(installer.status(self.config_dir, "opencode"))
        self.assertEqual(self.config().data, {"$schema": installer.SCHEMA})
        self.assertEqual(len(list((self.config_dir / "skills").iterdir())), 7)
        self.assertFalse((self.home / ".agents").exists())
        self.assertFalse((self.home / ".codex").exists())
        before = (self.config_dir / "opencode.json").read_bytes()
        self.install()
        self.assertEqual(before, (self.config_dir / "opencode.json").read_bytes())
        installer.uninstall(self.config_dir, False)
        self.assertEqual(self.config().data, {})
        self.assertFalse(any((self.config_dir / "skills").iterdir()))
        self.assertFalse((self.config_dir / installer.STATE_NAME).exists())

    def test_jsonc_comments_strings_trailing_commas_and_default_preservation(self):
        self.config_dir.mkdir(parents=True)
        path = self.config_dir / "opencode.jsonc"
        path.write_text('''{
  // Keep this comment and URL.
  "model": "provider/model",
  "url": "https://example.test/a//b/*c*/,}",
  "default_agent": "plan", /* personal choice */
  "instructions": ["CONTRIBUTING.md",],
}''')
        self.install()
        self.assertEqual(self.config().data["default_agent"], "plan")
        self.assertEqual(self.config().data["instructions"], ["CONTRIBUTING.md"])
        self.assertIn("// Keep this comment", path.read_text())
        self.assertIn("/* personal choice */", path.read_text())
        installer.uninstall(self.config_dir, False)
        self.assertEqual(self.config().data, {
            "model": "provider/model", "url": "https://example.test/a//b/*c*/,}",
            "default_agent": "plan", "instructions": ["CONTRIBUTING.md"],
        })
        self.assertIn("// Keep this comment", path.read_text())

    def test_existing_config_without_final_comma(self):
        self.config_dir.mkdir(parents=True)
        (self.config_dir / "opencode.json").write_text('{"model":"provider/model"}')
        self.install()
        installer.uninstall(self.config_dir, False)
        self.assertEqual(self.config().data, {"model": "provider/model"})

    def test_dry_run_creates_nothing(self):
        self.install(dry_run=True)
        self.assertFalse(self.config_dir.exists())

    def test_uninstall_dry_run_preserves_installation(self):
        self.install()
        before = (self.config_dir / "opencode.json").read_bytes()
        installer.uninstall(self.config_dir, True)
        self.assertEqual(before, (self.config_dir / "opencode.json").read_bytes())
        self.assertTrue(installer.status(self.config_dir, "opencode"))

    def test_conflict_preflight_preserves_existing_work(self):
        destination = self.config_dir / "agents/reviewer.md"
        destination.parent.mkdir(parents=True)
        destination.write_text("my personal reviewer")
        with self.assertRaises(installer.InstallError):
            self.install()
        self.assertEqual(destination.read_text(), "my personal reviewer")
        self.assertFalse((self.config_dir / installer.STATE_NAME).exists())
        self.assertFalse((self.config_dir / "opencode.json").exists())

    def test_unowned_matching_symlink_is_not_adopted(self):
        destination = self.config_dir / "agents/mentor.md"
        destination.parent.mkdir(parents=True)
        destination.symlink_to(ROOT / "opencode/agents/mentor.md")
        with self.assertRaises(installer.InstallError):
            self.install()
        self.assertTrue(destination.is_symlink())

    def test_uninstall_preserves_new_user_settings(self):
        self.install()
        path = self.config_dir / "opencode.json"
        config = self.config().set("model", "personal/model").set("default_agent", "reviewer")
        config = config.set("instructions", ["my-rules.md"])
        path.write_text(config.text)
        installer.uninstall(self.config_dir, False)
        self.assertEqual(self.config().data, {
            "model": "personal/model", "default_agent": "reviewer", "instructions": ["my-rules.md"],
        })

    def test_build_and_custom_agents_permissions_and_instructions_are_untouched(self):
        self.config_dir.mkdir(parents=True)
        path = self.config_dir / "opencode.jsonc"
        original = '''{
  "$schema": "https://opencode.ai/config.json",
  // Build is an implementation agent, not an advisory role.
  "default_agent": "build",
  "agents": {"build": {"system": "Implement requested changes."},
             "custom": {"mode": "primary", "system": "Custom role."}},
  "permissions": [{"action": "shell", "resource": "git push *", "effect": "ask"}],
  "instructions": ["personal.md"],
}'''
        path.write_text(original)
        for _ in range(2):
            self.install()
            self.assertEqual(path.read_text(), original)
            self.assertTrue(installer.status(self.config_dir, "opencode"))
        installer.uninstall(self.config_dir, False)
        self.assertEqual(path.read_text(), original)

    def test_reinstall_and_uninstall_preserve_later_mentor_selection(self):
        self.install()
        path = self.config_dir / "opencode.json"
        path.write_text(self.config().set("default_agent", "mentor").text)
        self.install()
        self.assertTrue(installer.status(self.config_dir, "opencode"))
        installer.uninstall(self.config_dir, False)
        self.assertEqual(self.config().data, {"default_agent": "mentor"})

    def test_upgrade_removes_owned_global_rule_and_restores_previous_default(self):
        self.legacy_install(previous_default="build", previous_instructions=["personal.md"])
        self.assertFalse(installer.status(self.config_dir, "opencode"))
        self.install()
        self.assertEqual(self.config().data, {
            "$schema": installer.SCHEMA, "default_agent": "build", "instructions": ["personal.md"],
        })
        self.assertTrue(installer.status(self.config_dir, "opencode"))
        before = self.config().text
        self.install()
        self.assertEqual(self.config().text, before)
        installer.uninstall(self.config_dir, False)
        self.assertEqual(self.config().data, {"default_agent": "build", "instructions": ["personal.md"]})

    def test_upgrade_restores_absent_default_and_instructions(self):
        self.legacy_install()
        self.install()
        self.assertEqual(self.config().data, {"$schema": installer.SCHEMA})

    def test_upgrade_preserves_existing_empty_instructions_and_mentor_preference(self):
        self.legacy_install(previous_default="mentor", previous_instructions=[])
        self.install()
        self.assertEqual(self.config().data, {
            "$schema": installer.SCHEMA, "default_agent": "mentor", "instructions": [],
        })

    def test_upgrade_preserves_later_default_and_unrelated_instructions(self):
        self.legacy_install(previous_default="build")
        path = self.config_dir / "opencode.json"
        config = self.config().set("default_agent", "custom")
        config = config.set("instructions", ["new.md", *config.data["instructions"]])
        path.write_text(config.text)
        self.install()
        self.assertEqual(self.config().data, {
            "$schema": installer.SCHEMA, "default_agent": "custom", "instructions": ["new.md"],
        })

    def test_upgrade_does_not_remove_user_managed_global_rule(self):
        instruction = str(self.config_dir / "toolkit/engineering.md")
        self.legacy_install(previous_instructions=[instruction], instruction_added=False)
        self.install()
        self.assertEqual(self.config().data["instructions"], [instruction])
        self.assertFalse(installer.status(self.config_dir, "opencode"))

    def test_legacy_uninstall_still_removes_owned_activation(self):
        self.legacy_install(previous_default="plan", previous_instructions=["personal.md"])
        installer.uninstall(self.config_dir, False)
        self.assertEqual(self.config().data, {"default_agent": "plan", "instructions": ["personal.md"]})

    def test_doctor_flags_user_managed_global_agreement_aliases_without_removing_them(self):
        self.install()
        path = self.config_dir / "opencode.json"
        installed = self.config_dir / "toolkit/engineering.md"
        for entry in (str(installed), str(ROOT / "instructions/engineering.md"),
                      "~/" + str(installed.relative_to(self.home))):
            with self.subTest(entry=entry), patch.dict(installer.os.environ, {"HOME": str(self.home)}):
                path.write_text(self.config().set("instructions", [entry]).text)
                self.install()
                self.assertEqual(self.config().data["instructions"], [entry])
                self.assertFalse(installer.status(self.config_dir, "opencode"))

    def test_upgrade_dry_run_preserves_legacy_state_and_config(self):
        self.legacy_install()
        state_path = self.config_dir / installer.STATE_NAME
        before = (self.config().text, state_path.read_bytes())
        self.install(dry_run=True)
        self.assertEqual((self.config().text, state_path.read_bytes()), before)

    def test_interrupted_upgrade_can_retry_legacy_cleanup(self):
        self.legacy_install(previous_default="build")
        write = installer.atomic_write

        def fail_config_write(path, text):
            if path.name == "opencode.json":
                raise OSError("interrupted config write")
            write(path, text)

        with patch.object(installer, "atomic_write", side_effect=fail_config_write):
            with self.assertRaises(OSError):
                self.install()
        self.install()
        self.assertEqual(self.config().data, {"$schema": installer.SCHEMA, "default_agent": "build"})
        self.assertTrue(installer.status(self.config_dir, "opencode"))

    def test_replaced_owned_link_blocks_uninstall_without_mutation(self):
        self.install()
        path = self.config_dir / "agents/mentor.md"
        path.unlink()
        path.write_text("replacement")
        before = (self.config_dir / "opencode.json").read_bytes()
        with self.assertRaises(installer.InstallError):
            installer.uninstall(self.config_dir, False)
        self.assertEqual(path.read_text(), "replacement")
        self.assertEqual(before, (self.config_dir / "opencode.json").read_bytes())

    def test_missing_link_is_reported_and_can_be_repaired(self):
        self.install()
        (self.config_dir / "skills/code-review").unlink()
        self.assertFalse(installer.status(self.config_dir, "opencode"))
        self.install()
        self.assertTrue(installer.status(self.config_dir, "opencode"))

    def test_invalid_version_does_not_activate(self):
        with patch.object(installer, "version", side_effect=installer.InstallError("v1")):
            with self.assertRaises(installer.InstallError):
                self.install()
        self.assertFalse(self.config_dir.exists())

    def test_ambiguous_configs_and_duplicate_keys_are_rejected(self):
        self.config_dir.mkdir(parents=True)
        first = self.config_dir / "opencode.json"
        second = self.config_dir / "opencode.jsonc"
        first.write_text("{}")
        second.write_text("{}")
        with self.assertRaises(installer.InstallError):
            self.install()
        second.unlink()
        first.write_text('{"model":"a/b", "model":"c/d"}')
        with self.assertRaises(installer.InstallError):
            self.install()
        self.assertFalse((self.config_dir / installer.STATE_NAME).exists())

    def test_invalid_instruction_shape_is_rejected(self):
        self.config_dir.mkdir(parents=True)
        (self.config_dir / "opencode.json").write_text('{"instructions": "not-an-array"}')
        with self.assertRaises(installer.InstallError):
            self.install()
        self.assertFalse((self.config_dir / installer.STATE_NAME).exists())

    def test_reconcile_removed_skill_links_on_update(self):
        self.install()
        expected = installer.links_for(self.config_dir)
        reduced = {dst: src for dst, src in expected.items() if dst.name != "design-challenge"}
        with patch.object(installer, "links_for", return_value=reduced):
            self.install()
        self.assertFalse((self.config_dir / "skills/design-challenge").is_symlink())
        installer.uninstall(self.config_dir, False)


class ResumeHelperTests(unittest.TestCase):
    def test_helper_passes_session_id_and_uses_its_project_directory(self):
        with tempfile.TemporaryDirectory(prefix="resume test ") as temporary:
            root = Path(temporary)
            project = root / "project with spaces"
            project.mkdir()
            helper = project / "opencode.sh"
            template = (ROOT / "skills/project-onboarding/assets/opencode.sh").read_text()
            helper.write_text(template.replace("SESSION_ID", "ses_example123"))
            binary = root / "opencode"
            binary.write_text('#!/usr/bin/env python3\nimport json, os, sys\n'
                              'print(json.dumps({"args": sys.argv[1:], "cwd": os.getcwd()}))\n')
            binary.chmod(0o700)
            import os
            result = subprocess.run(["sh", str(helper)], cwd=root, check=True,
                                    capture_output=True, text=True,
                                    env={**os.environ, "PATH": str(root) + os.pathsep + os.environ["PATH"]})
            self.assertEqual(json.loads(result.stdout), {"args": ["-s", "ses_example123"], "cwd": str(project)})

    def test_launcher_installs_and_uninstalls_with_explicit_v2_binary(self):
        with tempfile.TemporaryDirectory(prefix="cli test ") as temporary:
            root = Path(temporary)
            binary = root / "fake opencode"
            binary.write_text("#!/bin/sh\nprintf 'opencode v2.1.4\\n'\n")
            binary.chmod(0o700)
            directory = root / "global config"
            options = ["--config-dir", str(directory), "--opencode-bin", str(binary)]
            for action in ("install", "doctor", "uninstall"):
                result = subprocess.run(["sh", str(ROOT / "install.sh"), action, *options],
                                        check=True, text=True, capture_output=True, cwd=root)
                self.assertNotIn("Error:", result.stderr)
            self.assertEqual(installer.load_config(directory / "opencode.json").data, {})


if __name__ == "__main__":
    unittest.main()
