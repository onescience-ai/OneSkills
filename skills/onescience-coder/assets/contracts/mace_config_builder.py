"""Build minimal OneScience MACE YAML/CLI config from a probed task context."""

from __future__ import annotations

import argparse
import sys
from typing import Any

from material_config_common import (
    ConfigError,
    compact_dict,
    emit,
    first_value,
    load_json_arg,
    raise_if_errors,
    require_value,
    validate_mace,
)


TRAIN_KEYS = [
    "seed",
    "work_dir",
    "device",
    "default_dtype",
    "distributed",
    "valid_batch_size",
    "scaling",
    "ema",
    "ema_decay",
    "swa",
    "start_swa",
    "swa_lr",
    "scheduler_patience",
    "patience",
    "eval_interval",
    "error_table",
    "restart_latest",
    "save_cpu",
    "num_samples_pt",
]

SCRATCH_ARCH_KEYS = [
    "r_max",
    "num_interactions",
    "num_channels",
    "max_L",
    "correlation",
    "num_radial_basis",
    "num_cutoff_basis",
    "hidden_irreps",
    "max_ell",
]


def _add_optional(cfg: dict[str, Any], context: dict[str, Any], keys: list[str]) -> None:
    for key in keys:
        value = first_value(context, [f"training.{key}", f"run.{key}", key])
        if value not in (None, "", [], {}, False):
            cfg[key] = value


def _common_train(context: dict[str, Any], allow_todo: bool) -> dict[str, Any]:
    cfg: dict[str, Any] = {
        "name": require_value(context, ["run.name", "name"], "run.name", allow_todo=allow_todo),
        "model": first_value(context, ["training.model", "model"], "MACE"),
        "train_file": require_value(
            context,
            ["data_probe.train_file", "train_file"],
            "data_probe.train_file",
            allow_todo=allow_todo,
        ),
        "energy_key": require_value(
            context,
            ["data_probe.energy_key", "energy_key"],
            "data_probe.energy_key",
            allow_todo=allow_todo,
        ),
        "forces_key": require_value(
            context,
            ["data_probe.forces_key", "forces_key"],
            "data_probe.forces_key",
            allow_todo=allow_todo,
        ),
        "E0s": require_value(context, ["training.E0s", "E0s"], "E0s", allow_todo=allow_todo),
        "batch_size": require_value(
            context,
            ["training.batch_size", "run.batch_size", "batch_size"],
            "batch_size",
            allow_todo=allow_todo,
        ),
        "max_num_epochs": require_value(
            context,
            ["training.max_num_epochs", "max_num_epochs"],
            "max_num_epochs",
            allow_todo=allow_todo,
        ),
        "lr": require_value(context, ["training.lr", "lr"], "lr", allow_todo=allow_todo),
        "energy_weight": require_value(
            context,
            ["training.energy_weight", "energy_weight"],
            "energy_weight",
            allow_todo=allow_todo,
        ),
        "forces_weight": require_value(
            context,
            ["training.forces_weight", "forces_weight"],
            "forces_weight",
            allow_todo=allow_todo,
        ),
    }
    valid_file = first_value(context, ["data_probe.valid_file", "valid_file"])
    valid_fraction = first_value(context, ["data_probe.valid_fraction", "valid_fraction"])
    if valid_file:
        cfg["valid_file"] = valid_file
    elif valid_fraction:
        cfg["valid_fraction"] = valid_fraction
    else:
        require_value(context, ["data_probe.valid_file", "data_probe.valid_fraction"], "validation source", allow_todo=allow_todo)

    stress_key = first_value(context, ["data_probe.stress_key", "stress_key"])
    virials_key = first_value(context, ["data_probe.virials_key", "virials_key"])
    if stress_key:
        cfg["stress_key"] = stress_key
    if virials_key:
        cfg["virials_key"] = virials_key
    _add_optional(cfg, context, TRAIN_KEYS)
    return cfg


def _add_stress_or_virial(cfg: dict[str, Any], context: dict[str, Any]) -> None:
    stress_weight = first_value(context, ["training.stress_weight", "stress_weight"])
    virials_weight = first_value(context, ["training.virials_weight", "virials_weight"])
    if stress_weight not in (None, "", 0, 0.0):
        cfg["stress_weight"] = stress_weight
    if virials_weight not in (None, "", 0, 0.0):
        cfg["virials_weight"] = virials_weight


def build_config(context: dict[str, Any], allow_todo: bool = False) -> tuple[str, dict[str, Any]]:
    task_type = context.get("task_type")
    if not task_type:
        raise ConfigError("Missing task_type in context.")

    if task_type == "scratch_train":
        cfg = _common_train(context, allow_todo)
        for key in SCRATCH_ARCH_KEYS:
            value = first_value(context, [f"training.{key}", f"architecture.{key}", key])
            if value not in (None, "", [], {}, False):
                cfg[key] = value
        for required in ["r_max", "num_interactions", "num_channels", "max_L", "correlation"]:
            if required not in cfg:
                cfg[required] = require_value(context, [f"training.{required}", required], required, allow_todo=allow_todo)
        return task_type, compact_dict(cfg)

    if task_type == "foundation_finetune":
        cfg = _common_train(context, allow_todo)
        cfg["foundation_model"] = require_value(
            context,
            ["checkpoint_probe.foundation_model", "foundation_model"],
            "checkpoint_probe.foundation_model",
            allow_todo=allow_todo,
        )
        for key in ["multiheads_finetuning", "pt_train_file", "foundation_model_elements", "foundation_model_readout"]:
            value = first_value(context, [f"training.{key}", key])
            if value not in (None, "", [], {}, False):
                cfg[key] = value
        return task_type, compact_dict(cfg)

    if task_type == "stress_or_virial_train":
        if first_value(context, ["checkpoint_probe.foundation_model", "foundation_model"]):
            cfg = _common_train(context, allow_todo)
            cfg["foundation_model"] = first_value(context, ["checkpoint_probe.foundation_model", "foundation_model"])
        else:
            _, cfg = build_config({**context, "task_type": "scratch_train"}, allow_todo)
        _add_stress_or_virial(cfg, context)
        return task_type, compact_dict(cfg)

    if task_type == "evaluate":
        cfg = {
            "model_path": require_value(context, ["model_path", "checkpoint_probe.model_path"], "model_path", allow_todo=allow_todo),
            "test_file": require_value(context, ["data_probe.test_file", "test_file"], "test_file", allow_todo=allow_todo),
            "energy_key": require_value(context, ["data_probe.energy_key", "energy_key"], "energy_key", allow_todo=allow_todo),
            "forces_key": require_value(context, ["data_probe.forces_key", "forces_key"], "forces_key", allow_todo=allow_todo),
        }
        _add_optional(cfg, context, ["device", "default_dtype", "valid_batch_size", "error_table"])
        return task_type, compact_dict(cfg)

    if task_type == "ase_inference":
        cfg = {
            "model_path": require_value(context, ["model_path", "checkpoint_probe.model_path"], "model_path", allow_todo=allow_todo),
            "device": first_value(context, ["run.device", "device"], "cuda"),
        }
        _add_optional(cfg, context, ["default_dtype"])
        return task_type, compact_dict(cfg)

    if task_type == "relax_or_md":
        cfg = {
            "model_path": require_value(context, ["model_path", "checkpoint_probe.model_path"], "model_path", allow_todo=allow_todo),
            "structure_file": require_value(context, ["structure_file", "data_probe.structure_file"], "structure_file", allow_todo=allow_todo),
            "device": first_value(context, ["run.device", "device"], "cuda"),
        }
        _add_optional(cfg, context, ["default_dtype"])
        for key in ["optimizer", "md_ensemble", "temperature", "timestep", "steps", "trajectory"]:
            value = first_value(context, [f"run.{key}", key])
            if value not in (None, "", [], {}, False):
                cfg[key] = value
        return task_type, compact_dict(cfg)

    if task_type == "lammps_export":
        cfg = {
            "model_path": require_value(context, ["model_path", "checkpoint_probe.model_path"], "model_path", allow_todo=allow_todo),
            "output_path": require_value(context, ["output_path", "run.output_path"], "output_path", allow_todo=allow_todo),
            "elements": require_value(context, ["elements", "data_probe.elements"], "elements", allow_todo=allow_todo),
        }
        _add_optional(cfg, context, ["default_dtype", "save_cpu"])
        return task_type, compact_dict(cfg)

    raise ConfigError(f"Unsupported MACE task_type: {task_type}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context-file")
    parser.add_argument("--context-json")
    parser.add_argument("--format", choices=["yaml", "json", "overrides"], default="yaml")
    parser.add_argument("--allow-todo", action="store_true")
    parser.add_argument("--allow-foundation-arch-override", action="store_true")
    args = parser.parse_args()
    try:
        context = load_json_arg(args.context_file, args.context_json)
        task_type, config = build_config(context, allow_todo=args.allow_todo)
        errors = validate_mace(
            config,
            context,
            task_type,
            allow_foundation_arch_override=args.allow_foundation_arch_override,
        )
        raise_if_errors(errors)
        sys.stdout.write(emit(config, args.format))
        return 0
    except (ConfigError, ValueError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
