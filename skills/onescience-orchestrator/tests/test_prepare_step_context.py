"""Verify lossless step projection and task boundary enforcement."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_step_context.py"
SPEC = importlib.util.spec_from_file_location("prepare_step_context", SCRIPT)
context = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(context)


class StepContextTest(unittest.TestCase):
    def setUp(self):
        self.state = {
            "task_id": "case1", "user_goal": "实现精确接口", "output_root": "/tmp/task",
            "constraints": ["只改 model.py", "不得训练"],
            "execution_flags": {"training_allowed": False, "autonomous_mode": True},
            "completion_scope": "code_delivery",
            "requirement_ledger": [
                {"id": "no_train", "scope": "global", "requirement": "禁止 optimizer update"},
                {"id": "api", "requirement": "forward(self, x, mask=None)",
                 "implementation_target": "Model.forward", "verification": "keyword call", "status": "pending"},
                {"id": "other", "requirement": "后续绘图"}],
            "artifacts": [{"artifact_id": "spec", "path": "/unread/spec.md", "sha256": "abc"},
                          {"artifact_id": "old_log", "path": "/unread/old.log"}],
            "resource_results": [{"resource_result_id": "usage", "task_id": "case1",
                                  "matched_resources": [{"path": "/unread/assets/spec.md",
                                                         "content": "exact shape (B,N,C); strict=True"}]}],
            "events": ["irrelevant history " * 1000],
            "active_skill_context": "previous skill " * 1000,
        }
        self.handoff = {"step_id": "s2", "execution_skill": "onescience-coder", "step_goal": "实现模型",
                        "inputs": {"kwargs": {"x": [1, 2], "mask": None}, "dtype": "float32"},
                        "context_selection": {"requirement_ids": ["api"], "artifact_ids": ["spec"],
                                              "resource_result_ids": ["usage"]}}

    def test_projection_preserves_exact_contract_and_excludes_history(self):
        original = copy.deepcopy(self.state)
        result = context.prepare(self.state, {"step_handoff": self.handoff})["step_handoff"]
        self.assertEqual(result["inputs"], self.handoff["inputs"])
        self.assertEqual(result["requirements"], self.state["requirement_ledger"][:2])
        self.assertEqual(result["resource_retrieval_results"], self.state["resource_results"])
        self.assertEqual(result["task_context"]["relevant_artifacts"], self.state["artifacts"][:1])
        self.assertEqual(result["task_context"]["constraints"], self.state["constraints"])
        self.assertEqual(result["execution_flags"], self.state["execution_flags"])
        self.assertFalse(result["context_policy"]["host_release_verified"])
        self.assertNotIn("irrelevant history", json.dumps(result))
        self.assertNotIn("previous skill", json.dumps(result))
        self.assertEqual(original, self.state)

    def test_missing_and_conflicting_requirements_rejected(self):
        self.handoff["context_selection"]["requirement_ids"] = ["unknown"]
        with self.assertRaisesRegex(ValueError, "Unknown requirements"):
            context.prepare(self.state, self.handoff)
        self.handoff["context_selection"]["requirement_ids"] = ["api"]
        self.handoff["requirements"] = [{"id": "api", "requirement": "different API"}]
        with self.assertRaisesRegex(ValueError, "Conflicting requirement"):
            context.prepare(self.state, self.handoff)

    def test_scoped_ledger_cannot_disappear_without_explicit_selection(self):
        del self.handoff["context_selection"]
        with self.assertRaisesRegex(ValueError, "Select requirement_ids"):
            context.prepare(self.state, self.handoff)

    def test_global_restrictions_and_task_identity(self):
        for field, value, message in [("task_id", "other", "different task"),
                                      ("output_root", "/other", "Conflicting output_root"),
                                      ("execution_flags", {"training_allowed": True}, "prohibition")]:
            with self.subTest(field=field):
                handoff = {**self.handoff, field: value}
                with self.assertRaisesRegex(ValueError, message):
                    context.prepare(self.state, handoff)
        self.state["resource_results"][0]["task_id"] = "other"
        with self.assertRaisesRegex(ValueError, "different task"):
            context.prepare(self.state, self.handoff)

    def test_delivery_scope_does_not_expand(self):
        self.handoff["completion_scope"] = "spec_delivery"
        self.assertEqual(context.prepare(self.state, self.handoff)["step_handoff"]["completion_scope"], "spec_delivery")
        self.state["completion_scope"] = "spec_delivery"
        for scope in ("code_delivery", "scientific_result"):
            self.handoff["completion_scope"] = scope
            with self.assertRaisesRegex(ValueError, "cannot expand"):
                context.prepare(self.state, self.handoff)

    def test_autonomy_and_selector_typo_cannot_change_task_scope(self):
        self.state["execution_flags"]["autonomous_mode"] = False
        self.handoff["execution_flags"] = {"autonomous_mode": True}
        with self.assertRaisesRegex(ValueError, "autonomous_mode restriction"):
            context.prepare(self.state, self.handoff)
        self.handoff.pop("execution_flags")
        self.handoff["context_selection"]["artifacts_ids"] = ["spec"]
        with self.assertRaisesRegex(ValueError, "Unknown context selectors"):
            context.prepare(self.state, self.handoff)

    def test_history_and_invalid_flags_rejected(self):
        for extra in ({"task_state": self.state}, {"execution_flags": {"training_allowed": "false"}}):
            with self.assertRaises(ValueError):
                context.prepare(self.state, {**self.handoff, **extra})

    def test_cli_writes_full_context_but_returns_only_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state, handoff, output = [root / name for name in ("state.json", "step.yaml", "context.json")]
            state.write_text(json.dumps(self.state))
            handoff.write_text(json.dumps(self.handoff))
            command = [sys.executable, str(SCRIPT), "--task-state", str(state), "--handoff", str(handoff)]
            completed = subprocess.run(command + ["--output", str(output)], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            ref = json.loads(completed.stdout)
            self.assertEqual(ref["sha256"], hashlib.sha256(output.read_bytes()).hexdigest())
            self.assertEqual(ref["bytes"], output.stat().st_size)
            self.assertNotIn("step_handoff", ref)
            self.assertEqual(json.loads(output.read_text()), context.prepare(self.state, self.handoff))
            completed = subprocess.run(command + ["--output", str(state)], capture_output=True, text=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(json.loads(state.read_text()), self.state)


if __name__ == "__main__":
    unittest.main()
