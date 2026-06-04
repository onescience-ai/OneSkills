import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
