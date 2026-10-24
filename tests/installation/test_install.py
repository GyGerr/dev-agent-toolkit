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

    def test_fresh_install_idempotence_and_uninstall(self):
        self.install()
        self.assertTrue(installer.status(self.config_dir, "opencode"))
        self.assertEqual(self.config().data["default_agent"], "mentor")
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

    def test_jsonc_comments_strings_trailing_commas_and_default_restore(self):
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
        config = config.set("instructions", config.data["instructions"] + ["my-rules.md"])
        path.write_text(config.text)
        installer.uninstall(self.config_dir, False)
        self.assertEqual(self.config().data, {
            "model": "personal/model", "default_agent": "reviewer", "instructions": ["my-rules.md"],
        })

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
            binary.write_text("#!/bin/sh\nprintf '2.0.21\\n'\n")
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
