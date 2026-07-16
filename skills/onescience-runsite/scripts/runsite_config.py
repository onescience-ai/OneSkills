#!/usr/bin/env python3
"""管理 OneScience 运行站点配置 (根目录 onescience.json)。"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


VALID_RUN_SITES = {"local", "remote"}
VALID_ACCESS_MODES = {"ssh", "scnet"}
LEGACY_CHANNELS: dict[str, tuple[str, str | None, str]] = {
    "local_direct": ("local", None, ""),
    "local_slurm": ("local", "slurm", ""),
    "ssh_direct": ("remote", None, "ssh"),
    "ssh_slurm": ("remote", "slurm", "ssh"),
    "scnet_direct": ("remote", None, "scnet"),
    "scnet_slurm": ("remote", "slurm", "scnet"),
}


def default_config_path(config_path: str | None = None) -> Path:
    if config_path:
        return Path(config_path).expanduser()
    return Path(__file__).resolve().parents[3] / "onescience.json"


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_config(path: Path, config: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_asset_json(filename: str) -> dict[str, Any]:
    asset_path = Path(__file__).resolve().parents[1] / "assets" / filename
    if not asset_path.exists():
        return {}
    return json.loads(asset_path.read_text(encoding="utf-8"))


def parse_json_payload(
    *,
    value: str | None,
    env_var: str | None,
    label: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    option = f"--{label.replace('_', '-')}"
    env_option = f"{option}-env"

    if value and env_var:
        return None, {
            "error": f"Ambiguous {label} source",
            "message": f"Use either {option} or {env_option}, not both.",
        }

    source_value = value
    source_label = option
    if env_var:
        source_value = os.environ.get(env_var)
        source_label = f"environment variable {env_var}"
        if source_value in (None, ""):
            return None, {
                "error": f"Missing {label} environment variable",
                "message": f"{env_var} is empty or not set.",
            }

    if not source_value:
        return None, None

    stripped = source_value.strip()
    if stripped.startswith("@") or stripped.lower().endswith(".json"):
        return None, {
            "error": f"Invalid {label} JSON source",
            "message": (
                f"{source_label} must contain a JSON object directly. "
                "Do not create or pass temp_run_site_data.json, temp_cluster_data.json, "
                "run_site_data.json, cluster_data.json, or any intermediate JSON file."
            ),
        }

    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as e:
        return None, {
            "error": f"Invalid {label} JSON",
            "message": str(e),
        }

    if not isinstance(parsed, dict):
        return None, {
            "error": f"Invalid {label} JSON",
            "message": f"{label} must be a JSON object.",
        }

    return parsed, None


def normalize_execution_mode(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized in {"", "none", "null", "no", "false"}:
        return None
    if normalized in {"slurm", "slrum"}:
        return "slurm"
    raise ValueError("execution_mode must be slurm or none/null.")


def normalize_access_mode(run_site: str, value: str | None) -> str:
    normalized = "" if value is None else str(value).strip().lower()
    if run_site == "local":
        if normalized in {"", "none", "null", "local"}:
            return ""
        raise ValueError("access_mode must be empty when run_site=local.")
    if normalized in VALID_ACCESS_MODES:
        return normalized
    raise ValueError("access_mode must be ssh or scnet when run_site=remote.")


def normalize_profile(
    *,
    run_site: str | None,
    execution_mode: str | None,
    access_mode: str | None,
    execution_channel: str | None,
) -> tuple[str, str | None, str]:
    if execution_channel:
        if execution_channel not in LEGACY_CHANNELS:
            raise ValueError(f"Invalid legacy execution_channel: {execution_channel}")
        return LEGACY_CHANNELS[execution_channel]

    site = (run_site or "").strip().lower()
    if site not in VALID_RUN_SITES:
        raise ValueError("run_site must be local or remote.")

    mode = normalize_execution_mode(execution_mode)
    access = normalize_access_mode(site, access_mode)
    return site, mode, access


def detect_local_slurm() -> bool:
    return shutil.which("sbatch") is not None


def detect_hardware() -> dict[str, str]:
    if shutil.which("nvidia-smi"):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return {
                    "accelerator_kind": "gpu",
                    "accelerator_vendor": "nvidia",
                    "cpu_arch": "x86_64",
                }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    if shutil.which("rocm-smi"):
        try:
            result = subprocess.run(
                ["rocm-smi", "--showproductname"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return {
                    "accelerator_kind": "dcu",
                    "accelerator_vendor": "amd",
                    "cpu_arch": "x86_64",
                }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return {
        "accelerator_kind": "cpu",
        "accelerator_vendor": "intel",
        "cpu_arch": "x86_64",
    }


def match_hardware_profile(hardware_kind: str, use_slurm: bool, node_count: int = 1) -> dict[str, Any] | None:
    if hardware_kind not in {"dcu", "gpu"}:
        return None

    profiles_data = load_asset_json(f"hardware_profiles/{hardware_kind}_hardware_profiles.json")
    profiles = profiles_data.get("profiles", [])
    if not profiles:
        return None

    for profile in profiles:
        capabilities = profile.get("capabilities", {})
        if use_slurm and not capabilities.get("supports_sbatch"):
            continue
        default_scope = capabilities.get("default_node_scope", "single_node")
        if node_count > 1 and default_scope == "multi_node":
            return profile
        if node_count <= 1 and default_scope != "multi_node":
            return profile

    return profiles[0]


def get_nested(config: dict[str, Any], path: str) -> Any:
    current: Any = config
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def has_key(config: dict[str, Any], path: str) -> bool:
    current: Any = config
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True


def validate_runtime_config(config: dict[str, Any]) -> tuple[bool, list[str], bool]:
    runtime = config.get("runtime", {})
    exec_profile = runtime.get("execution_profile", {})
    conda = runtime.get("conda", {})

    legacy_values_detected = any(
        [
            "execution_channel" in exec_profile,
            exec_profile.get("execution_mode") in {"remote_slurm", "remote_direct", "local_slurm"},
            exec_profile.get("access_mode") in {"local", "cloud_api", "slurm"},
        ]
    )

    missing_fields: list[str] = []
    run_site = exec_profile.get("run_site")
    execution_mode = exec_profile.get("execution_mode")
    access_mode = exec_profile.get("access_mode")

    if run_site not in VALID_RUN_SITES:
        missing_fields.append("runtime.execution_profile.run_site")
    if not has_key(config, "runtime.execution_profile.execution_mode") or execution_mode not in (None, "slurm"):
        missing_fields.append("runtime.execution_profile.execution_mode")
    if not has_key(config, "runtime.execution_profile.access_mode"):
        missing_fields.append("runtime.execution_profile.access_mode")

    if run_site == "local" and access_mode != "":
        missing_fields.append("runtime.execution_profile.access_mode")
    if run_site == "remote" and access_mode not in VALID_ACCESS_MODES:
        missing_fields.append("runtime.execution_profile.access_mode")

    if run_site == "remote":
        for field in [
            "runtime.ssh.host",
            "runtime.ssh.hostname",
            "runtime.ssh.port",
            "runtime.ssh.user",
            "runtime.ssh.identity_file",
            "runtime.ssh.remote_work_dir",
        ]:
            if get_nested(config, field) in (None, "", []):
                missing_fields.append(field)

    if run_site == "remote" and access_mode == "scnet":
        for field in [
            "runtime.scnet.SCNET_ACCESS_KEY",
            "runtime.scnet.SCNET_SECRET_KEY",
            "runtime.scnet.SCNET_USER",
            "runtime.scnet.region",
            "runtime.scnet.remote_work_dir",
        ]:
            if get_nested(config, field) in (None, "", []):
                missing_fields.append(field)

    if execution_mode == "slurm":
        for field in [
            "runtime.cluster.partition",
            "runtime.cluster.nodes",
            "runtime.cluster.gpus_per_node",
            "runtime.cluster.cpus_per_task",
            "runtime.cluster.memory",
            "runtime.cluster.time_limit",
        ]:
            if get_nested(config, field) in (None, "", []):
                missing_fields.append(field)

    # runtime.conda is managed by onescience-installer, not validated here

    for field in [
        "runtime.target.platform_type",
        "runtime.target.accelerator_kind",
        "runtime.environment.cpu.arch",
    ]:
        if get_nested(config, field) in (None, "", []):
            missing_fields.append(field)

    return not missing_fields and not legacy_values_detected, sorted(set(missing_fields)), legacy_values_detected


def normalize_ssh_data(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if data is None:
        return None
    normalized = dict(data)
    if "work_dir" in normalized and "remote_work_dir" not in normalized:
        normalized["remote_work_dir"] = normalized.pop("work_dir")
    if not normalized.get("host") and normalized.get("hostname"):
        normalized["host"] = normalized["hostname"]
    normalized.setdefault("strict_host_key_checking", "no")
    normalized.setdefault("password_authentication", "no")
    normalized.setdefault("port", 22)
    return normalized


def normalize_scnet_data(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if data is None:
        return None
    normalized = dict(data)
    if "work_dir" in normalized and "remote_work_dir" not in normalized:
        normalized["remote_work_dir"] = normalized.pop("work_dir")
    if "SCNET_REGION" in normalized and "region" not in normalized:
        normalized["region"] = normalized.pop("SCNET_REGION")
    return normalized


def build_onescience_config(
    *,
    run_site: str,
    execution_mode: str | None,
    access_mode: str,
    hardware_type: dict[str, str],
    ssh_data: dict[str, Any] | None = None,
    scnet_data: dict[str, Any] | None = None,
    cluster_data: dict[str, Any] | None = None,
    modules: list[str] | None = None,
) -> dict[str, Any]:
    use_slurm = execution_mode == "slurm"
    node_count = cluster_data.get("nodes", 1) if cluster_data else 1

    hardware_kind = hardware_type["accelerator_kind"]
    hardware_vendor = hardware_type["accelerator_vendor"]
    cpu_arch = hardware_type["cpu_arch"]
    hw_profile = match_hardware_profile(hardware_kind, use_slurm, int(node_count or 1))

    target = {
        "scheduler_type": "slurm" if use_slurm else None,
        "platform_type": "cluster" if run_site == "remote" or use_slurm else "workstation",
        "cpu_arch": cpu_arch,
        "cpu_vendor": hw_profile["cpu"]["vendor"] if hw_profile and "cpu" in hw_profile else hardware_vendor,
        "accelerator_kind": hardware_kind,
        "accelerator_vendor": hardware_vendor,
        "node_scope": "multi_node" if int(node_count or 1) > 1 else "single_node",
    }

    environment = {
        "cpu": {
            "arch": cpu_arch,
            "vendor": target["cpu_vendor"],
        },
        "accelerator_defaults": {},
    }
    if hw_profile and hw_profile.get("accelerators"):
        acc = hw_profile["accelerators"][0]
        environment["accelerator_defaults"] = {
            "kind": hardware_kind,
            "vendor": hardware_vendor,
            "visibility_env": acc.get("visibility_env", "CUDA_VISIBLE_DEVICES"),
            "distributed_backend": acc.get("distributed_backend", "nccl"),
            "launch_mode": hw_profile.get("capabilities", {}).get("launch_mode", "python"),
            "distributed_mode": "multi" if int(node_count or 1) > 1 else "single",
        }

    config: dict[str, Any] = {
        "runtime": {
            "execution_profile": {
                "run_site": run_site,
                "execution_mode": execution_mode,
                "access_mode": access_mode,
            },
            "target": target,
            "environment": environment,
            "cluster": cluster_data if use_slurm else None,
            "modules": modules or (hw_profile.get("software", {}).get("modules", []) if hw_profile else []),
            "resources": {
                "gpu_type": hardware_kind,
                "cpu_memory_ratio": 8,
                "disk_space": "100GB",
            },
            "env_vars": load_asset_json("env_vars/config.json"),
        }
    }

    if run_site == "remote":
        config["runtime"]["ssh"] = normalize_ssh_data(ssh_data) or {}
    if run_site == "remote" and access_mode == "scnet":
        config["runtime"]["scnet"] = normalize_scnet_data(scnet_data) or {}

    return config


def masked_config_summary(config: dict[str, Any]) -> dict[str, Any]:
    runtime = config.get("runtime", {})
    exec_profile = runtime.get("execution_profile", {})
    target = runtime.get("target", {})
    ssh = runtime.get("ssh", {})
    scnet = runtime.get("scnet", {})
    cluster = runtime.get("cluster") or {}

    return {
        "execution_profile": {
            "run_site": exec_profile.get("run_site"),
            "execution_mode": exec_profile.get("execution_mode"),
            "access_mode": exec_profile.get("access_mode"),
        },
        "hardware": {
            "accelerator_kind": target.get("accelerator_kind"),
            "accelerator_vendor": target.get("accelerator_vendor"),
        },
        "ssh_host_alias": ssh.get("host"),
        "scnet_user": scnet.get("SCNET_USER"),
        "cluster": {
            "scheduler_type": target.get("scheduler_type"),
            "partition": cluster.get("partition"),
            "nodes": cluster.get("nodes"),
            "gpus_per_node": cluster.get("gpus_per_node"),
        },
    }


def cmd_check(args: argparse.Namespace) -> None:
    path = default_config_path(args.config_path)
    if not path.exists():
        print(json.dumps({"config_path": str(path), "config_exists": False}, ensure_ascii=False, indent=2))
        return

    config = load_config(path)
    config_complete, missing_fields, legacy_values_detected = validate_runtime_config(config)
    print(
        json.dumps(
            {
                "config_path": str(path),
                "config_exists": True,
                "config_complete": config_complete,
                "missing_fields": missing_fields,
                "legacy_values_detected": legacy_values_detected,
                "next_action": "onescience-runtime" if config_complete else "onescience-runsite",
                "config_summary": masked_config_summary(config),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_show(args: argparse.Namespace) -> None:
    path = default_config_path(args.config_path)
    config = load_config(path)
    if config.get("runtime", {}).get("scnet"):
        scnet = dict(config["runtime"]["scnet"])
        if scnet.get("SCNET_ACCESS_KEY"):
            scnet["SCNET_ACCESS_KEY"] = "***"
        if scnet.get("SCNET_SECRET_KEY"):
            scnet["SCNET_SECRET_KEY"] = "***"
        config["runtime"]["scnet"] = scnet

    print(
        json.dumps(
            {
                "config_path": str(path),
                "config_exists": path.exists(),
                "config": config if path.exists() else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_detect_hardware(args: argparse.Namespace) -> None:
    hardware = detect_hardware()
    print(
        json.dumps(
            {
                "hardware_detected": True,
                "accelerator_kind": hardware["accelerator_kind"],
                "accelerator_vendor": hardware["accelerator_vendor"],
                "cpu_arch": hardware["cpu_arch"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_detect_local_slurm(args: argparse.Namespace) -> None:
    has_slurm = detect_local_slurm()
    print(
        json.dumps(
            {
                "has_slurm": has_slurm,
                "detected_profile": {
                    "run_site": "local",
                    "execution_mode": "slurm" if has_slurm else None,
                    "access_mode": "",
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_generate(args: argparse.Namespace) -> None:
    path = default_config_path(args.config_path)
    if path.exists() and not args.force:
        print(
            json.dumps(
                {
                    "error": "Configuration file already exists",
                    "config_path": str(path),
                    "message": "Use --force only for tests or use 'modify' to update specific fields.",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    try:
        run_site, execution_mode, access_mode = normalize_profile(
            run_site=args.run_site,
            execution_mode=args.execution_mode,
            access_mode=args.access_mode,
            execution_channel=args.execution_channel,
        )
    except ValueError as e:
        print(json.dumps({"error": "Invalid execution profile", "message": str(e)}, ensure_ascii=False, indent=2))
        return

    ssh_data, payload_error = parse_json_payload(value=args.ssh_data, env_var=args.ssh_data_env, label="ssh_data")
    if payload_error:
        print(json.dumps(payload_error, ensure_ascii=False, indent=2))
        return

    scnet_data, payload_error = parse_json_payload(value=args.scnet_data, env_var=args.scnet_data_env, label="scnet_data")
    if payload_error:
        print(json.dumps(payload_error, ensure_ascii=False, indent=2))
        return

    cluster_data, payload_error = parse_json_payload(
        value=args.cluster_data,
        env_var=args.cluster_data_env,
        label="cluster_data",
    )
    if payload_error:
        print(json.dumps(payload_error, ensure_ascii=False, indent=2))
        return

    if run_site == "remote" and not ssh_data:
        print(
            json.dumps(
                {
                    "error": "Missing ssh data",
                    "message": "ssh_data is required when run_site=remote.",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if run_site == "remote" and access_mode == "scnet" and not scnet_data:
        print(
            json.dumps(
                {
                    "error": "Missing scnet data",
                    "message": "scnet_data is required when run_site=remote and access_mode=scnet.",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if run_site == "remote" and access_mode == "scnet":
        scnet_data = normalize_scnet_data(scnet_data) or {}
        missing_scnet_fields = [
            field
            for field in ["SCNET_ACCESS_KEY", "SCNET_SECRET_KEY", "SCNET_USER", "region", "remote_work_dir"]
            if scnet_data.get(field) in (None, "", [])
        ]
        if missing_scnet_fields:
            print(
                json.dumps(
                    {
                        "error": "Incomplete scnet data",
                        "missing_fields": [f"runtime.scnet.{field}" for field in missing_scnet_fields],
                        "message": "scnet_data must include SCNET_ACCESS_KEY, SCNET_SECRET_KEY, SCNET_USER, region, and remote_work_dir.",
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return

    if execution_mode == "slurm" and not cluster_data:
        print(
            json.dumps(
                {
                    "error": "Missing cluster data",
                    "message": "cluster_data is required when execution_mode=slurm.",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    modules = args.modules.split(",") if args.modules else None
    hardware_type = detect_hardware()
    config = build_onescience_config(
        run_site=run_site,
        execution_mode=execution_mode,
        access_mode=access_mode,
        hardware_type=hardware_type,
        ssh_data=ssh_data,
        scnet_data=scnet_data,
        cluster_data=cluster_data,
        modules=modules,
    )
    save_config(path, config)

    print(
        json.dumps(
            {
                "config_created": True,
                "config_path": str(path),
                "execution_profile": config["runtime"]["execution_profile"],
                "hardware_detected": hardware_type,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def cmd_modify(args: argparse.Namespace) -> None:
    path = default_config_path(args.config_path)
    if not path.exists():
        print(
            json.dumps(
                {
                    "error": "Configuration file does not exist",
                    "config_path": str(path),
                    "message": "Use 'generate' to create a new configuration file.",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    config = load_config(path)
    target: Any = config
    field_parts = args.field.split(".")
    for part in field_parts[:-1]:
        if not isinstance(target, dict):
            print(json.dumps({"error": "Invalid field path", "field": args.field}, ensure_ascii=False, indent=2))
            return
        target = target.setdefault(part, {})

    value: Any = args.value
    if args.value.lower() in {"none", "null"}:
        value = None
    elif args.value.lower() in {"true", "false"}:
        value = args.value.lower() == "true"
    else:
        try:
            value = json.loads(args.value)
        except json.JSONDecodeError:
            value = args.value

    target[field_parts[-1]] = value
    save_config(path, config)
    config_complete, missing_fields, legacy_values_detected = validate_runtime_config(config)

    print(
        json.dumps(
            {
                "modified": True,
                "field": args.field,
                "value": value,
                "config_path": str(path),
                "config_complete": config_complete,
                "missing_fields": missing_fields,
                "legacy_values_detected": legacy_values_detected,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="管理 OneScience 运行站点配置。")
    parser.add_argument("--config-path", help="配置文件路径(默认: 项目根目录 onescience.json)")

    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="检查配置文件是否存在且完整")
    p_check.set_defaults(func=cmd_check)

    p_show = sub.add_parser("show", help="显示当前配置(隐藏密钥)")
    p_show.set_defaults(func=cmd_show)

    p_detect_slurm = sub.add_parser("detect-local-slurm", help="检测本地 SLURM")
    p_detect_slurm.set_defaults(func=cmd_detect_local_slurm)

    p_detect_hw = sub.add_parser("detect-hardware", help="检测硬件类型")
    p_detect_hw.set_defaults(func=cmd_detect_hardware)

    p_generate = sub.add_parser("generate", help="根据新版 execution_profile 生成配置")
    p_generate.add_argument("--run-site", choices=sorted(VALID_RUN_SITES), help="运行站点: local 或 remote")
    p_generate.add_argument("--execution-mode", default="none", help="调度方式: slurm 或 none")
    p_generate.add_argument("--access-mode", default="", help="远程接入方式: ssh 或 scnet；本地留空")
    p_generate.add_argument("--execution-channel", choices=sorted(LEGACY_CHANNELS), help=argparse.SUPPRESS)
    p_generate.add_argument("--ssh-data", help="SSH 配置数据(JSON 字符串)")
    p_generate.add_argument("--ssh-data-env", help="包含 SSH JSON 字符串的环境变量名")
    p_generate.add_argument("--scnet-data", help="SCnet 配置数据(JSON 字符串)")
    p_generate.add_argument("--scnet-data-env", help="包含 SCnet JSON 字符串的环境变量名")
    p_generate.add_argument("--cluster-data", help="Slurm 配置数据(JSON 字符串)")
    p_generate.add_argument("--cluster-data-env", help="包含 Slurm JSON 字符串的环境变量名")
    p_generate.add_argument("--modules", help="环境模块列表,逗号分隔")
    p_generate.add_argument("--force", action="store_true", help="强制覆盖已存在配置；仅用于测试")
    p_generate.set_defaults(func=cmd_generate)

    p_modify = sub.add_parser("modify", help="修改配置文件的特定字段")
    p_modify.add_argument("--field", required=True, help="字段路径,例如 runtime.cluster.partition")
    p_modify.add_argument("--value", required=True, help="字段值；none/null 会写为 JSON null")
    p_modify.set_defaults(func=cmd_modify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
