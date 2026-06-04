"""Build minimal OneScience UMA Hydra overrides from a probed task context."""

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
    set_path,
    validate_uma,
)


def _head_config(task_type: str) -> dict[str, Any]:
    if task_type == "finetune_energy":
        return {"primary": {"class": "MLP_Energy_Head"}}
    if task_type in {"finetune_ef", "finetune_efs"}:
        return {"primary": {"class": "MLP_EFS_Head"}}
    return {"primary": {"class": "MLP_EFS_Head"}}


def _tasks_list(task_type: str, dataset_name: str) -> list[dict[str, Any]]:
    tasks = [
        {"name": f"{dataset_name}_energy", "property": "energy", "loss": "mae"}
    ]
    if task_type in {"finetune_ef", "finetune_efs"}:
        tasks.append({"name": f"{dataset_name}_forces", "property": "forces", "loss": "l2mae"})
    if task_type == "finetune_efs":
        tasks.append({"name": f"{dataset_name}_stress", "property": "stress", "loss": "mae"})
    return tasks


def _training_config(context: dict[str, Any], task_type: str, allow_todo: bool) -> dict[str, Any]:
    dataset_name = require_value(
        context,
        ["data_probe.dataset_name", "data.dataset_name", "dataset_name"],
        "dataset_name",
        allow_todo=allow_todo,
    )
    cfg: dict[str, Any] = {
        "data": {
            "dataset_name": dataset_name,
            "elem_refs": require_value(
                context,
                ["data_probe.elem_refs", "data.elem_refs", "elem_refs"],
                "elem_refs",
                allow_todo=allow_todo,
            ),
            "normalizer_rmsd": require_value(
                context,
                ["data_probe.normalizer_rmsd", "data.normalizer_rmsd", "normalizer_rmsd"],
                "normalizer_rmsd",
                allow_todo=allow_todo,
            ),
            "train_dataset": require_value(
                context,
                ["data_probe.train_dataset", "data.train_dataset"],
                "train_dataset",
                allow_todo=allow_todo,
            ),
            "val_dataset": require_value(
                context,
                ["data_probe.val_dataset", "data.val_dataset"],
                "val_dataset",
                allow_todo=allow_todo,
            ),
            "heads": first_value(context, ["data.heads"], _head_config(task_type)),
            "tasks_list": first_value(context, ["data.tasks_list"], _tasks_list(task_type, str(dataset_name))),
        },
        "runner": {
            "train_eval_unit": {
                "model": {
                    "checkpoint_location": require_value(
                        context,
                        ["checkpoint_probe.checkpoint_location", "checkpoint_location"],
                        "checkpoint_location",
                        allow_todo=allow_todo,
                    ),
                    "overrides": {"backbone": {"regress_stress": task_type == "finetune_efs"}},
                }
            }
        },
        "optim": {
            "lr": require_value(context, ["training.lr", "optim.lr", "lr"], "optim.lr", allow_todo=allow_todo)
        },
        "trainer": {},
    }

    optional_paths = {
        "optim.weight_decay": ["training.weight_decay", "optim.weight_decay"],
        "trainer.batch_size": ["training.batch_size", "trainer.batch_size", "batch_size"],
        "trainer.max_steps": ["training.max_steps", "trainer.max_steps", "max_steps"],
        "trainer.epochs": ["training.epochs", "trainer.epochs", "epochs"],
        "trainer.evaluate_every_n_steps": ["training.evaluate_every_n_steps", "trainer.evaluate_every_n_steps"],
        "trainer.checkpoint_every_n_steps": ["training.checkpoint_every_n_steps", "trainer.checkpoint_every_n_steps"],
        "runner.train_eval_unit.model.overrides.backbone.always_use_pbc": [
            "data_probe.always_use_pbc",
            "training.always_use_pbc",
        ],
        "runner.train_eval_unit.model.overrides.backbone.max_neighbors": [
            "training.max_neighbors",
            "data_probe.max_neighbors",
        ],
        "runner.train_eval_unit.model.overrides.backbone.jd_path": [
            "run.jd_path",
            "jd_path",
        ],
    }
    for target, sources in optional_paths.items():
        value = first_value(context, sources)
        if value not in (None, "", [], {}, False):
            set_path(cfg, target, value)
    return compact_dict(cfg)


def _inference_config(context: dict[str, Any], task_type: str, allow_todo: bool) -> dict[str, Any]:
    cfg: dict[str, Any] = {
        "checkpoint_location": require_value(
            context,
            ["checkpoint_probe.checkpoint_location", "checkpoint_location"],
            "checkpoint_location",
            allow_todo=allow_todo,
        ),
        "task_name": require_value(context, ["task_name", "data_probe.task_name"], "task_name", allow_todo=allow_todo),
        "device": first_value(context, ["run.device", "device"], "cuda"),
    }
    if task_type == "relax_or_md":
        cfg["structure_file"] = require_value(
            context,
            ["structure_file", "data_probe.structure_file"],
            "structure_file",
            allow_todo=allow_todo,
        )
    if task_type == "batch_inference":
        cfg["input_path"] = require_value(context, ["input_path", "data_probe.input_path"], "input_path", allow_todo=allow_todo)
    if task_type == "molecule_charge_spin" or cfg.get("task_name") == "omol":
        cfg["r_data_keys"] = first_value(context, ["r_data_keys", "data_probe.r_data_keys"], ["spin", "charge"])
        value = first_value(context, ["molecule_cell_size", "data_probe.molecule_cell_size"])
        if value not in (None, "", [], {}, False):
            cfg["molecule_cell_size"] = value
    if task_type == "crystal_or_adsorbate_pbc":
        cfg["pbc"] = require_value(context, ["pbc", "data_probe.pbc"], "pbc", allow_todo=allow_todo)
    for key in ["jd_path", "max_neighbors", "always_use_pbc"]:
        value = first_value(context, [f"run.{key}", f"data_probe.{key}", key])
        if value not in (None, "", [], {}, False):
            cfg[key] = value
    return compact_dict(cfg)


def build_config(context: dict[str, Any], allow_todo: bool = False) -> tuple[str, dict[str, Any]]:
    task_type = context.get("task_type")
    if not task_type:
        raise ConfigError("Missing task_type in context.")
    if task_type in {"finetune_energy", "finetune_ef", "finetune_efs", "moe_advanced"}:
        return task_type, _training_config(context, task_type, allow_todo)
    if task_type in {
        "checkpoint_inference",
        "relax_or_md",
        "batch_inference",
        "molecule_charge_spin",
        "crystal_or_adsorbate_pbc",
    }:
        return task_type, _inference_config(context, task_type, allow_todo)
    raise ConfigError(f"Unsupported UMA task_type: {task_type}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context-file")
    parser.add_argument("--context-json")
    parser.add_argument("--format", choices=["yaml", "json", "overrides"], default="overrides")
    parser.add_argument("--allow-todo", action="store_true")
    args = parser.parse_args()
    try:
        context = load_json_arg(args.context_file, args.context_json)
        task_type, config = build_config(context, allow_todo=args.allow_todo)
        errors = validate_uma(config, context, task_type)
        raise_if_errors(errors)
        sys.stdout.write(emit(config, args.format))
        return 0
    except (ConfigError, ValueError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
