import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import install_oneskills


class OneScienceSourceInstallTest(unittest.TestCase):
    def test_codex_install_entries_include_onescience_source_tree(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = install_oneskills.load_manifest("codex", None)

            entries = install_oneskills.build_entries(
                project_root,
                manifest,
                "basic",
                "codex",
                with_onescience_source=True,
            )

            targets = {entry.target.relative_to(project_root).as_posix() for entry in entries}
            self.assertIn(".codex/oneskills/onescience", targets)

    def test_codex_bridge_mentions_project_local_onescience_source_root(self):
        bridge = install_oneskills.build_bridge_content("onescience-coder", ".codex/oneskills/skills")
        self.assertIn(".codex/oneskills/onescience", bridge)
        self.assertIn("./onescience/...", bridge)

    def test_onescience_source_tree_can_be_skipped(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = install_oneskills.load_manifest("codex", None)

            entries = install_oneskills.build_entries(
                project_root,
                manifest,
                "basic",
                "codex",
                with_onescience_source=False,
            )

            targets = {entry.target.relative_to(project_root).as_posix() for entry in entries}
            self.assertNotIn(".codex/oneskills/onescience", targets)


class OpenCodeInstallTest(unittest.TestCase):
    def test_opencode_install_entries_include_onescience_source_tree(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = install_oneskills.load_manifest("opencode", None)

            entries = install_oneskills.build_entries(
                project_root,
                manifest,
                "basic",
                "opencode",
                with_onescience_source=True,
            )

            targets = {entry.target.relative_to(project_root).as_posix() for entry in entries}
            self.assertIn(".opencode/onescience", targets)

    def test_opencode_default_layout_matches_opencode_discovery(self):
        manifest = install_oneskills.load_manifest("opencode", None)
        self.assertEqual(manifest["namespace_root"], ".opencode")
        self.assertEqual(install_oneskills.manifest_skills_dir(manifest), ".opencode/skills")

    def test_namespace_root_override_changes_install_targets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            manifest = install_oneskills.load_manifest(
                "opencode",
                None,
                namespace_root_override="vendor/oneskills/2026.05.15",
            )

            entries = install_oneskills.build_entries(
                project_root,
                manifest,
                "basic",
                "opencode",
                with_onescience_source=False,
            )

            targets = {entry.target.relative_to(project_root).as_posix() for entry in entries}
            self.assertIn("vendor/oneskills/2026.05.15/skills/onescience-workflow", targets)

    def test_opencode_config_snippet_contains_skills_paths(self):
        snippet = install_oneskills.build_opencode_config_snippet(".opencode/skills")
        self.assertIn('"paths": [".opencode/skills"]', snippet)

    def test_opencode_config_snippet_path_follows_namespace_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            target = install_oneskills.write_opencode_config_snippet(
                project_root,
                ".opencode",
                ".opencode/skills",
                force=True,
                dry_run=False,
            )
            self.assertEqual(target, project_root / ".opencode" / "opencode.jsonc.snippet")
            self.assertTrue(target.exists())

    def test_opencode_skills_paths_merge_optional_for_default_layout(self):
        self.assertTrue(install_oneskills.opencode_skills_paths_merge_optional(".opencode/skills"))
        self.assertFalse(
            install_oneskills.opencode_skills_paths_merge_optional(".opencode/oneskills/skills")
        )


if __name__ == "__main__":
    unittest.main()
