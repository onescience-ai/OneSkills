#!/usr/bin/env python3
"""Build a step-scoped handoff without copying the full task history.

Reads JSON or YAML; never opens referenced artifacts or resource assets.
This prepares model input, but does not edit a host's conversation history.
"""

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


HISTORY_FIELDS = {
    "messages", "conversation_history", "execution_transcript", "task_state",
    "global_plan", "events", "observations", "active_skill_context",
}
SNAPSHOT_FIELDS = (
    "metadata_source", "script_path", "skills_roots", "snapshot_path",
    "snapshot_sha256", "source_fingerprint", "inventory_complete", "exit_code",
)


def mapping(value, name):
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a mapping")
    return value


def sequence(value, name):
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    return value


def unique(values):
    result, seen = [], set()
    for value in values:
        key = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
        if key not in seen:
            seen.add(key)
            result.append(copy.deepcopy(value))
    return result


def select(items, requested, key, name, include_global=False):
    requested = sequence(requested, name + " selector")
    if any(not isinstance(item, str) or not item for item in requested):
        raise ValueError(f"{name} selectors must be nonempty strings")
    index = {}
    for item in sequence(items, name):
        mapping(item, name + " entry")
        identity = item.get(key)
        if not isinstance(identity, str) or not identity or identity in index:
            raise ValueError(f"{name} entries require unique {key}")
        index[identity] = item
    missing = set(requested) - index.keys()
    if missing:
        raise ValueError(f"Unknown {name}: {sorted(missing)}")
    selected = set(requested)
    return [copy.deepcopy(item) for identity, item in index.items()
            if identity in selected or (include_global and item.get("scope") == "global")]


def merge_requirements(inherited, local):
    merged = {}
    for item in inherited + sequence(local, "requirements"):
        mapping(item, "requirement")
        identity = item.get("id")
        if not isinstance(identity, str) or not identity:
            raise ValueError("Each requirement needs an id")
        if identity in merged and merged[identity] != item:
            raise ValueError(f"Conflicting requirement {identity}; update its source first")
        merged[identity] = copy.deepcopy(item)
    return list(merged.values())


def prepare(state, handoff):
    mapping(state, "task state")
    mapping(handoff, "handoff")
    step = copy.deepcopy(mapping(handoff.get("step_handoff", handoff), "step_handoff"))
    for field in ("step_id", "execution_skill", "step_goal"):
        if not isinstance(step.get(field), str) or not step[field].strip():
            raise ValueError(f"{field} must be a nonempty string")
    attempt = step.setdefault("attempt", 1)
    if type(attempt) is not int or attempt < 1:
        raise ValueError("attempt must be a positive integer")
    task_id = state.get("task_id") or step.get("task_id")
    if not isinstance(task_id, str) or not task_id:
        raise ValueError("task_id is required in task state or handoff")
    if step.get("task_id", task_id) != task_id:
        raise ValueError("handoff belongs to a different task")
    step["task_id"] = task_id
    context = mapping(step.setdefault("task_context", {}), "task_context")
    for value in (step, context):
        forbidden = HISTORY_FIELDS.intersection(value)
        if forbidden:
            raise ValueError(f"Move history out of handoff: {sorted(forbidden)}")
    # Unknown step-specific fields and all of inputs are preserved verbatim.
    goal = state.get("user_goal") or context.get("user_goal")
    if not isinstance(goal, str) or not goal.strip():
        raise ValueError("user_goal is required; a step title cannot replace it")
    context["user_goal"] = goal
    context["constraints"] = unique(
        sequence(state.get("constraints", []), "task constraints")
        + sequence(context.get("constraints", []), "step constraints")
    )
    inherited_flags = mapping(state.get("execution_flags", {}), "task execution_flags")
    local_flags = mapping(step.get("execution_flags", {}), "step execution_flags")
    for flags in (inherited_flags, local_flags):
        for name in ("training_allowed", "autonomous_mode"):
            if name in flags and type(flags[name]) is not bool:
                raise ValueError(f"{name} must be a boolean")
    flags = {**inherited_flags, **local_flags}
    if (inherited_flags.get("autonomous_mode") is False
            and local_flags.get("autonomous_mode") is True):
        raise ValueError("handoff cannot override the task's autonomous_mode restriction")
    if "training_allowed" in state and type(state["training_allowed"]) is not bool:
        raise ValueError("task training_allowed must be a boolean")
    if "training_allowed" in state and "training_allowed" not in inherited_flags:
        flags.setdefault("training_allowed", state["training_allowed"])
    training_values = [inherited_flags.get("training_allowed"), state.get("training_allowed")]
    if any(value is False for value in training_values):
        if local_flags.get("training_allowed") is True:
            raise ValueError("handoff cannot override the task's training prohibition")
        flags["training_allowed"] = False
    step["execution_flags"] = flags
    if "output_root" in state:
        for target in (step, context):
            if "output_root" in target and target["output_root"] != state["output_root"]:
                raise ValueError("Conflicting output_root; replan explicitly before dispatch")
        step["output_root"] = copy.deepcopy(state["output_root"])
    # A spec-delivery step can be part of a larger code-delivery task.
    if "completion_scope" in state:
        step.setdefault("completion_scope", state["completion_scope"])
        permitted = {"spec_delivery": {"spec_delivery"},
                     "code_delivery": {"spec_delivery", "code_delivery"}}
        if (state["completion_scope"] in permitted
                and step["completion_scope"] not in permitted[state["completion_scope"]]):
            raise ValueError("handoff cannot expand the task's completion_scope")

    selection = mapping(step.pop("context_selection", {}), "context_selection")
    unknown = set(selection) - {"requirement_ids", "artifact_ids", "resource_result_ids"}
    if unknown:
        raise ValueError(f"Unknown context selectors: {sorted(unknown)}")
    requirements = select(state.get("requirement_ledger", []),
                          selection.get("requirement_ids", []), "id", "requirements", True)
    ledger = state.get("requirement_ledger", [])
    if (any(item.get("scope") != "global" for item in ledger)
            and "requirement_ids" not in selection and not step.get("requirements")):
        raise ValueError("Select requirement_ids explicitly; do not drop the task ledger")
    step["requirements"] = merge_requirements(requirements, step.get("requirements", []))
    artifacts = select(state.get("artifacts", []), selection.get("artifact_ids", []),
                       "artifact_id", "artifacts")
    context["relevant_artifacts"] = unique(
        sequence(context.get("relevant_artifacts", []), "relevant_artifacts") + artifacts
    )
    if "resource_result_ids" in selection:
        results = select(state.get("resource_results", []), selection["resource_result_ids"],
                         "resource_result_id", "resource results")
        for result in results:
            if result.get("task_id", task_id) != task_id:
                raise ValueError("resource result belongs to a different task")
        step["resource_retrieval_results"] = unique(
            sequence(step.get("resource_retrieval_results", []), "resource_retrieval_results")
            + results
        )
    for result in sequence(step.get("resource_retrieval_results", []), "resource_retrieval_results"):
        mapping(result, "resource result")
        if result.get("task_id", task_id) != task_id:
            raise ValueError("resource result belongs to a different task")
    discovery = mapping(state.get("skill_metadata_discovery", {}), "skill_metadata_discovery")
    if discovery and "metadata_snapshot" not in context:
        context["metadata_snapshot"] = {
            key: copy.deepcopy(discovery[key]) for key in SNAPSHOT_FIELDS if key in discovery
        }
    step["context_policy"] = {
        "call_id": f"{task_id}/{step['step_id']}/{attempt}",
        "history_scope": "current_call_only",
        "release_after": "result_persisted_and_accepted",
        "host_release_verified": False,
    }
    return {"step_handoff": step}


def read_document(path):
    import yaml
    from discover_skill_metadata import yaml_loader

    _, loader = yaml_loader()
    try:
        return mapping(yaml.load(path.read_text(encoding="utf-8"), Loader=loader), str(path))
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid document {path}: {exc}") from exc


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-state", type=Path, required=True)
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.resolve() in {args.task_state.resolve(), args.handoff.resolve()}:
            raise ValueError("output must not overwrite the task state or original handoff")
        result = prepare(read_document(args.task_state), read_document(args.handoff))
        content = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        atomic_write(args.output, content)
    except (OSError, ValueError, TypeError, ImportError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"context_path": str(args.output),
                      "sha256": hashlib.sha256(content.encode()).hexdigest(),
                      "bytes": len(content.encode()), "host_release_verified": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
