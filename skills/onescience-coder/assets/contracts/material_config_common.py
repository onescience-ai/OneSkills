"""Shared helpers for OneScience material config builders.

The contract helpers in this folder intentionally use only the Python standard
library so they can run inside a fresh Codex skill environment.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigError(Exception):
    """Raised when config generation or validation cannot continue safely."""


TODO_PREFIX = "<TODO:"


def script_root() -> Path:
    return Path(__file__).resolve().parent


def skill_root() -> Path:
    return script_root().parent.parent


def load_json_arg(path: str | None = None, inline: str | None = None) -> dict[str, Any]:
    if path and inline:
        raise ConfigError("Use either --context-file/--config-file or inline JSON, not both.")
    if inline:
        return json.loads(inline)
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    raise ConfigError("JSON input is required.")


def load_schema(model: str) -> dict[str, Any]:
    path = script_root() / f"{model}_parameter_schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def get_path(data: dict[str, Any], dotted: str, default: Any = None) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def set_path(data: dict[str, Any], dotted: str, value: Any) -> None:
    cur = data
    parts = dotted.split(".")
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value


def first_value(data: dict[str, Any], paths: list[str], default: Any = None) -> Any:
    for path in paths:
        value = get_path(data, path)
        if value not in (None, "", []):
            return value
    return default


def require_value(
    data: dict[str, Any],
    paths: list[str],
    label: str,
    *,
    allow_todo: bool = False,
) -> Any:
    value = first_value(data, paths)
    if value not in (None, "", []):
        return value
    if allow_todo:
        return f"{TODO_PREFIX} {label}>"
    raise ConfigError(f"Missing required value: {label}. Checked: {', '.join(paths)}")


def omit_empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def compact_dict(data: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            value = compact_dict(value)
        if omit_empty(value):
            continue
        out[key] = value
    return out


def flatten(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            out.update(flatten(value, path))
        else:
            out[path] = value
    return out


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    text = str(value)
    if text.startswith(TODO_PREFIX):
        return json.dumps(text, ensure_ascii=False)
    if any(ch in text for ch in [":", "#", "{", "}", "[", "]", ",", "&", "*", "!", "|", ">", "@"]):
        return json.dumps(text, ensure_ascii=False)
    if text.lower() in {"true", "false", "null", "none", "yes", "no"}:
        return json.dumps(text, ensure_ascii=False)
    return text


def dump_yaml(data: Any, indent: int = 0) -> str:
    lines: list[str] = []
    pad = " " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{pad}{key}:")
                lines.append(dump_yaml(value, indent + 2))
            elif isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
                lines.append(f"{pad}{key}:")
                for item in value:
                    lines.append(f"{pad}-")
                    lines.append(dump_yaml(item, indent + 2))
            else:
                lines.append(f"{pad}{key}: {yaml_scalar(value)}")
    else:
        lines.append(f"{pad}{yaml_scalar(data)}")
    return "\n".join(lines)


def emit(data: dict[str, Any], fmt: str) -> str:
    if fmt == "json":
        return json.dumps(data, ensure_ascii=False, indent=2)
    if fmt == "yaml":
        return dump_yaml(data) + "\n"
    if fmt == "overrides":
        pieces = []
        for key, value in flatten(data).items():
            pieces.append(f"{key}={json.dumps(value, ensure_ascii=False)}")
        return "\n".join(pieces) + "\n"
    raise ConfigError(f"Unsupported output format: {fmt}")


def validate_required(config: dict[str, Any], schema: dict[str, Any], task_type: str) -> list[str]:
    errors: list[str] = []
    required = schema.get("required_by_task", {}).get(task_type, [])
    for path in required:
        value = get_path(config, path)
        if omit_empty(value):
            errors.append(f"missing required parameter for {task_type}: {path}")
        elif isinstance(value, str) and value.startswith(TODO_PREFIX):
            errors.append(f"unresolved TODO parameter for {task_type}: {path}")
    return errors


def validate_mutual_exclusion(config: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for param in schema.get("parameters", []):
        name = param["name"]
        if omit_empty(get_path(config, name)):
            continue
        for other in param.get("mutually_exclusive_with", []):
            if not omit_empty(get_path(config, other)):
                errors.append(f"mutually exclusive parameters both set: {name}, {other}")
    return errors


def validate_mace(
    config: dict[str, Any],
    context: dict[str, Any],
    task_type: str,
    *,
    allow_foundation_arch_override: bool = False,
) -> list[str]:
    schema = load_schema("mace")
    errors = validate_required(config, schema, task_type)
    errors.extend(validate_mutual_exclusion(config, schema))

    has_foundation = not omit_empty(config.get("foundation_model"))
    if has_foundation and not allow_foundation_arch_override:
        for key in schema.get("architecture_keys", []):
            if key in config:
                errors.append(
                    f"foundation fine-tuning must not emit architecture key without explicit override: {key}"
                )

    stress_weight = config.get("stress_weight", 0) or 0
    if stress_weight and omit_empty(config.get("stress_key")):
        errors.append("stress_weight is set but stress_key is missing")
    virials_weight = config.get("virials_weight", 0) or 0
    if virials_weight and omit_empty(config.get("virials_key")):
        errors.append("virials_weight is set but virials_key is missing")

    cfg_foundation = config.get("foundation_model")
    ctx_foundation = first_value(context, ["checkpoint_probe.foundation_model", "foundation_model"])
    if cfg_foundation and ctx_foundation and cfg_foundation != ctx_foundation:
        errors.append("config foundation_model differs from checkpoint_probe.foundation_model")

    data_elements = set(first_value(context, ["data_probe.elements", "elements"], []) or [])
    ckpt_elements = set(first_value(context, ["checkpoint_probe.atomic_numbers", "checkpoint_probe.elements"], []) or [])
    if has_foundation and data_elements and ckpt_elements and not data_elements.issubset(ckpt_elements):
        missing = sorted(data_elements - ckpt_elements)
        errors.append(f"foundation checkpoint does not cover data elements: {missing}")

    return errors


def _task_names(tasks_list: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(tasks_list, list):
        for item in tasks_list:
            if isinstance(item, dict):
                name = item.get("name") or item.get("property")
                if name:
                    names.add(str(name))
            elif isinstance(item, str):
                names.add(item)
    return names


def validate_uma(config: dict[str, Any], context: dict[str, Any], task_type: str) -> list[str]:
    schema = load_schema("uma")
    errors = validate_required(config, schema, task_type)
    errors.extend(validate_mutual_exclusion(config, schema))

    dataset_cfg = get_path(config, "data.dataset_name")
    dataset_ctx = first_value(context, ["data_probe.dataset_name", "dataset_name"])
    if dataset_cfg and dataset_ctx and dataset_cfg != dataset_ctx:
        errors.append("config data.dataset_name differs from context data_probe.dataset_name")

    if task_type.startswith("finetune"):
        stats_source = first_value(context, ["data_probe.stats_source", "stats_source"])
        train_source = first_value(context, ["data_probe.train_dataset", "data.train_dataset"])
        if stats_source and train_source and str(stats_source) not in str(train_source):
            errors.append("stats_source does not appear to match train_dataset; verify elem_refs/normalizer_rmsd source")
        if omit_empty(get_path(config, "data.elem_refs")):
            errors.append("fine-tuning requires data.elem_refs from current dataset")
        if omit_empty(get_path(config, "data.normalizer_rmsd")):
            errors.append("fine-tuning requires data.normalizer_rmsd from current dataset")

    regress_stress = bool(get_path(config, "runner.train_eval_unit.model.overrides.backbone.regress_stress", False))
    tasks = _task_names(get_path(config, "data.tasks_list", []))
    has_stress_label = bool(first_value(context, ["data_probe.has_stress", "has_stress"], False))
    if task_type == "finetune_efs":
        if not regress_stress:
            errors.append("finetune_efs requires regress_stress=true")
        if not has_stress_label:
            errors.append("finetune_efs requires verified stress labels in data_probe.has_stress")
        if not any("stress" in name for name in tasks):
            errors.append("finetune_efs requires a stress task in data.tasks_list")
    if task_type == "finetune_ef" and regress_stress:
        errors.append("finetune_ef must keep regress_stress=false; use finetune_efs for stress")

    task_name = config.get("task_name")
    if task_type in {"molecule_charge_spin", "checkpoint_inference"} and task_name == "omol":
        keys = set(config.get("r_data_keys") or [])
        if not {"spin", "charge"}.issubset(keys):
            errors.append("OMOL inference requires r_data_keys to include spin and charge")

    return errors


def raise_if_errors(errors: list[str]) -> None:
    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ConfigError(f"Configuration validation failed:\n{joined}")
