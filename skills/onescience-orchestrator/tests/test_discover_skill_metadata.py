"""Run with: python -m unittest discover -s <orchestrator_dir>/tests -v"""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/discover_skill_metadata.py"
SPEC = importlib.util.spec_from_file_location("discover_skill_metadata", SCRIPT)
discovery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(discovery)


class MetadataDiscoveryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write_skill(self, directory="onescience-example", kind="executor", name=None):
        path = self.root / directory / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "name": name or directory,
            "description": "科研任务: 测试 # metadata",
            "type": kind,
            "capabilities": {field: [] for field in discovery.CAPABILITY_FIELDS},
        }
        data["capabilities"]["owns"] = ["执行任务"]
        self.save(path, data)
        return path, data

    def save(self, path, data):
        path.write_text("---\n" + yaml.safe_dump(data, allow_unicode=True) + "---\nBODY_SECRET\n")

    def discover(self, roots=None, kind=None):
        return discovery.discover(roots or [self.root], SCRIPT, kind)

    def cli(self, script=SCRIPT, *args, no_site=False):
        command = [sys.executable] + (["-S"] if no_site else []) + [str(script)] + list(args)
        completed = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        return completed.returncode, json.loads(completed.stdout)

    def test_repository_inventory_and_exact_metadata(self):
        root = SCRIPT.parents[2]
        result = self.discover([root])
        self.assertTrue(result["inventory_complete"], result["errors"])
        self.assertEqual(result["metadata_source"], "skill_frontmatter_script")
        self.assertEqual({item["type"] for item in result["skills"]}, set(discovery.SKILL_TYPES))
        actual = {item["name"]: item for item in result["skills"]}
        yaml_module, loader = discovery.yaml_loader()
        for path in root.glob("*/SKILL.md"):
            data = discovery.read_frontmatter(path, yaml_module, loader)
            self.assertEqual(actual[data["name"]]["capabilities"], data["capabilities"])
        self.assertIn("onescience-coder", actual)
        self.assertIn("scnet-chat", actual)

    def test_multiline_yaml_and_no_body_or_asset_reads(self):
        path, data = self.write_skill()
        header = yaml.safe_dump(data, allow_unicode=True).replace(
            "description: '科研任务: 测试 # metadata'", "description: >-\n  第一行\n  第二行"
        )
        path.write_bytes(("---\n" + header + "---\n").encode() + b"\xffBODY_SECRET")
        assets = path.parent / "assets" / "fake"
        assets.mkdir(parents=True)
        (assets / "SKILL.md").write_text("INVALID_YAML: [")
        result = self.discover()
        self.assertTrue(result["inventory_complete"], result["errors"])
        self.assertEqual(result["skills"][0]["description"], "第一行 第二行")
        self.assertNotIn("BODY_SECRET", json.dumps(result))

    def test_missing_capability_is_visible_and_incomplete(self):
        path, data = self.write_skill()
        del data["capabilities"]["not_owns"]
        self.save(path, data)
        result = self.discover()
        inventory = result["inventories"]["executor"]
        self.assertFalse(result["inventory_complete"])
        self.assertEqual(inventory["missing_executor_skills"], ["onescience-example"])
        self.assertIn("capabilities.not_owns", result["errors"][0]["reason"])

    def test_invalid_headers_are_errors_not_empty_success(self):
        for header in ("no frontmatter", "---\nname: missing-end", "---\nname: [\n---\n",
                       "---\nname: a\nname: b\n---\n", "---\n!!python/object:os.system {}\n---\n"):
            with self.subTest(header=header):
                path = self.root / "onescience-broken" / "SKILL.md"
                path.parent.mkdir(exist_ok=True)
                path.write_text(header)
                result = self.discover()
                self.assertFalse(result["inventory_complete"])
                self.assertTrue(result["errors"])

    def test_empty_or_missing_roots_fail(self):
        self.assertFalse(self.discover()["inventory_complete"])
        self.assertFalse(self.discover([self.root / "missing"])["inventory_complete"])

    def test_ordinary_third_party_skill_is_ignored(self):
        self.write_skill()
        path = self.root / "ordinary" / "SKILL.md"
        path.parent.mkdir()
        self.save(path, {"name": "ordinary", "description": "ordinary skill"})
        result = self.discover()
        self.assertTrue(result["inventory_complete"])
        self.assertEqual(result["ignored_skills"], [str(path)])

    def test_onescience_missing_file_or_metadata_fails(self):
        directory = self.root / "onescience-incomplete"
        directory.mkdir()
        self.assertFalse(self.discover()["inventory_complete"])
        self.save(directory / "SKILL.md", {"name": directory.name, "description": "missing contract"})
        self.assertFalse(self.discover()["inventory_complete"])

    def test_duplicate_names_rejected_but_aliases_deduplicated(self):
        path, _ = self.write_skill()
        (self.root / "alias").symlink_to(path.parent, target_is_directory=True)
        result = self.discover([self.root, self.root])
        self.assertTrue(result["inventory_complete"])
        self.assertEqual(len(result["skills"]), 1)
        self.write_skill("other", name="onescience-example")
        result = self.discover()
        self.assertFalse(result["inventory_complete"])
        self.assertEqual(result["skills"], [])
        self.assertIn("duplicate skill name", result["errors"][0]["reason"])

    def test_type_filter_does_not_hide_other_errors(self):
        self.write_skill("onescience-resource", "resource")
        path, data = self.write_skill()
        del data["capabilities"]
        self.save(path, data)
        code, result = self.cli(SCRIPT, "--skills-root", str(self.root), "--type", "resource")
        self.assertEqual(code, 1)
        self.assertEqual([item["type"] for item in result["skills"]], ["resource"])
        self.assertFalse(result["inventories"]["resource"]["resource_inventory_complete"])

    def test_installed_copy_and_symlink_work_from_other_cwd(self):
        root = self.root / "installed"
        destination = root / "onescience-orchestrator" / "scripts" / SCRIPT.name
        destination.parent.mkdir(parents=True)
        shutil.copyfile(SCRIPT, destination)
        self.write_skill("installed/onescience-orchestrator", "orchestrator", "onescience-orchestrator")
        self.write_skill("installed/onescience-coder", name="onescience-coder")
        code, result = self.cli(destination)
        self.assertEqual(code, 0, result["errors"])
        self.assertEqual(result["skills_roots"], [str(root)])
        self.assertEqual(result["skills"][0]["name"], "onescience-coder")
        alias_root = self.root / "linked"
        alias_root.mkdir()
        (alias_root / "onescience-orchestrator").symlink_to(destination.parents[1], target_is_directory=True)
        self.write_skill("linked/onescience-trainer", name="onescience-trainer")
        code, result = self.cli(alias_root / "onescience-orchestrator/scripts" / SCRIPT.name)
        self.assertEqual(code, 0, result["errors"])
        self.assertEqual(result["skills_roots"], [str(alias_root)])
        self.assertEqual([item["name"] for item in result["skills"]],
                         ["onescience-orchestrator", "onescience-trainer"])

    def test_multiple_roots_and_dependency_error_are_json(self):
        self.write_skill("first/onescience-a", name="onescience-a")
        self.write_skill("second/onescience-b", name="onescience-b")
        code, result = self.cli(SCRIPT, "--skills-root", str(self.root / "first"),
                                "--skills-root", str(self.root / "second"))
        self.assertEqual(code, 0, result["errors"])
        self.assertEqual([item["name"] for item in result["skills"]], ["onescience-a", "onescience-b"])
        code, result = self.cli(no_site=True)
        self.assertEqual(code, 1)
        self.assertIn("PyYAML", result["errors"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
