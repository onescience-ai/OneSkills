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

SSH_FIELD_SPECS: dict[str, dict[str, str]] = {
    "runtime.ssh.host": {"label": "host", "description": "SSH Host 别名；没有则可留空自动生成"},
    "runtime.ssh.hostname": {"label": "hostname", "description": "远程主机名或 IP"},
    "runtime.ssh.port": {"label": "port", "description": "SSH 端口；直接回车使用 22"},
    "runtime.ssh.user": {"label": "user", "description": "SSH 用户名"},
    "runtime.ssh.identity_file": {"label": "identity_file", "description": "SSH 私钥路径"},
    "runtime.ssh.remote_work_dir": {"label": "remote_work_dir", "description": "远程工作目录"},
}

SCNET_FIELD_SPECS: dict[str, dict[str, str]] = {
    "runtime.scnet.SCNET_ACCESS_KEY": {
        "label": "SCNET_ACCESS_KEY",
        "description": "SCnet access key；我不会在输出中回显明文",
    },
    "runtime.scnet.SCNET_SECRET_KEY": {
        "label": "SCNET_SECRET_KEY",
        "description": "SCnet secret key；我不会在输出中回显明文",
    },
    "runtime.scnet.SCNET_USER": {"label": "SCNET_USER", "description": "SCnet 用户名"},
    "runtime.scnet.region": {"label": "region", "description": "SCnet 区域，例如核心节点、华东一区【昆山】等"},
    "runtime.scnet.remote_work_dir": {"label": "remote_work_dir", "description": "远程工作目录"},
}

CLUSTER_FIELD_SPECS: dict[str, dict[str, str]] = {
    "runtime.cluster.partition": {"label": "partition", "description": "Slurm 分区名称，例如 gpu、compute、hpctest01；无默认值"},
    "runtime.cluster.nodes": {"label": "nodes", "description": "节点数量；直接回车使用 1"},
    "runtime.cluster.gpus_per_node": {"label": "gpus_per_node", "description": "每个节点需要的 GPU/DCU 数量；直接回车使用 1"},
    "runtime.cluster.cpus_per_task": {"label": "cpus_per_task", "description": "每个任务需要的 CPU 核心数；直接回车使用 8"},
    "runtime.cluster.memory": {"label": "memory", "description": "内存大小，例如 64GB；直接回车使用 64GB"},
    "runtime.cluster.time_limit": {"label": "time_limit", "description": "作业时间限制 HH:MM:SS；直接回车使用 02:00:00"},
    "runtime.cluster.gpu_type": {"label": "gpu_type", "description": "Slurm 加速器类型；直接回车使用刚刚检测或确认的 dcu/gpu"},
    "runtime.cluster.ntasks_per_node": {"label": "ntasks_per_node", "description": "每节点任务数；直接回车使用 1"},
}

EXECUTION_PROFILE_FIELD_SPECS: dict[str, dict[str, str]] = {
    "runtime.execution_profile.run_site": {"label": "run_site", "description": "运行站点；只能填写 local 或 remote"},
    "runtime.execution_profile.execution_mode": {"label": "execution_mode", "description": "调度方式；填写 slurm 或 null"},
    "runtime.execution_profile.access_mode": {
        "label": "access_mode",
        "description": "接入方式；run_site=local 时留空字符串，run_site=remote 时填写 ssh 或 scnet",
    },
}

TARGET_FIELD_SPECS: dict[str, dict[str, str]] = {
    "runtime.target.platform_type": {"label": "platform_type", "description": "运行平台类型；通常由脚本根据本地/远程与 Slurm 情况生成"},
    "runtime.target.accelerator_kind": {"label": "accelerator_kind", "description": "加速器类型；必须确认是 dcu 或 gpu"},
    "runtime.environment.cpu.arch": {"label": "cpu_arch", "description": "CPU 架构；通常由脚本检测或写入"},
    "runtime.modules": {"label": "modules", "description": "运行环境模块列表；应按检测出的硬件 profile 生成，不能自行猜测补全"},
}

SECTION_REQUIRED_FIELDS: dict[str, list[str]] = {
    "runtime.ssh": list(SSH_FIELD_SPECS.keys()),
    "runtime.scnet": list(SCNET_FIELD_SPECS.keys()),
    "runtime.cluster": list(CLUSTER_FIELD_SPECS.keys()),
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


def _hardware_result(
    *,
    accelerator_kind: str,
    accelerator_vendor: str,
    cpu_arch: str = "x86_64",
    detected: bool = True,
    detection_target: str = "local",
) -> dict[str, Any]:
    return {
        "hardware_detected": detected,
        "accelerator_kind": accelerator_kind,
        "accelerator_vendor": accelerator_vendor,
        "cpu_arch": cpu_arch,
        "detection_target": detection_target,
    }


def infer_hardware_from_accelerator_kind(accelerator_kind: str, cpu_arch: str = "x86_64") -> dict[str, Any]:
    normalized = accelerator_kind.strip().lower()
    if normalized == "dcu":
        return _hardware_result(
            accelerator_kind="dcu",
            accelerator_vendor="amd",
            cpu_arch=cpu_arch,
            detected=True,
            detection_target="user",
        )
    if normalized == "gpu":
        return _hardware_result(
            accelerator_kind="gpu",
            accelerator_vendor="nvidia",
            cpu_arch=cpu_arch,
            detected=True,
            detection_target="user",
        )
    raise ValueError("accelerator_kind must be dcu or gpu.")


def detect_hardware() -> dict[str, Any]:
    if shutil.which("nvidia-smi"):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return _hardware_result(
                    accelerator_kind="gpu",
                    accelerator_vendor="nvidia",
                    detection_target="local",
                )
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
                return _hardware_result(
                    accelerator_kind="dcu",
                    accelerator_vendor="amd",
                    detection_target="local",
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    if shutil.which("hy-smi"):
        try:
            result = subprocess.run(
                ["hy-smi"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return _hardware_result(
                    accelerator_kind="dcu",
                    accelerator_vendor="amd",
                    detection_target="local",
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return _hardware_result(
        accelerator_kind="unknown",
        accelerator_vendor="unknown",
        detected=False,
        detection_target="local",
    )


def detect_remote_hardware(ssh_alias: str) -> dict[str, Any]:
    remote_script = (
        "if command -v nvidia-smi >/dev/null 2>&1 && "
        "nvidia-smi --query-gpu=name --format=csv,noheader >/dev/null 2>&1; then "
        "printf gpu; "
        "elif command -v rocm-smi >/dev/null 2>&1 && rocm-smi --showproductname >/dev/null 2>&1; then "
        "printf dcu; "
        "elif command -v hy-smi >/dev/null 2>&1 && hy-smi >/dev/null 2>&1; then "
        "printf dcu; "
        "else printf unknown; fi"
    )
    try:
        result = subprocess.run(
            ["ssh", ssh_alias, remote_script],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return {
            **_hardware_result(
                accelerator_kind="unknown",
                accelerator_vendor="unknown",
                detected=False,
                detection_target=f"ssh:{ssh_alias}",
            ),
            "error": str(e),
        }

    accelerator_kind = result.stdout.strip().splitlines()[-1].strip().lower() if result.stdout.strip() else "unknown"
    if result.returncode == 0 and accelerator_kind in {"dcu", "gpu"}:
        hardware = infer_hardware_from_accelerator_kind(accelerator_kind)
        hardware["detection_target"] = f"ssh:{ssh_alias}"
        return hardware

    return {
        **_hardware_result(
            accelerator_kind="unknown",
            accelerator_vendor="unknown",
            detected=False,
            detection_target=f"ssh:{ssh_alias}",
        ),
        "stderr": result.stderr.strip(),
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


def _missing_field_entry(field: str, spec: dict[str, str]) -> dict[str, str]:
    return {
        "field": field,
        "label": spec["label"],
        "description": spec["description"],
    }


def infer_required_sections(config: dict[str, Any]) -> dict[str, bool]:
    runtime = config.get("runtime", {})
    exec_profile = runtime.get("execution_profile", {})
    run_site = exec_profile.get("run_site")
    execution_mode = exec_profile.get("execution_mode")
    access_mode = exec_profile.get("access_mode")

    return {
        "runtime.ssh": run_site == "remote",
        "runtime.scnet": run_site == "remote" and access_mode == "scnet",
        "runtime.cluster": execution_mode == "slurm",
    }


def collect_missing_required_fields(config: dict[str, Any], required_sections: dict[str, bool]) -> list[str]:
    missing_fields: list[str] = []
    for section, required in required_sections.items():
        if not required:
            continue
        for field in SECTION_REQUIRED_FIELDS[section]:
            if get_nested(config, field) in (None, "", []):
                missing_fields.append(field)
    return missing_fields


def build_missing_field_guidance(config: dict[str, Any], missing_fields: list[str], legacy_values_detected: bool) -> dict[str, Any]:
    runtime = config.get("runtime", {})
    exec_profile = runtime.get("execution_profile", {})
    access_mode = exec_profile.get("access_mode")
    required_sections = infer_required_sections(config)

    guidance: dict[str, Any] = {
        "next_action": "ask_user",
        "do_not_autofill_missing_fields": True,
        "message": "检测到 onescience.json 配置不完整或有误，请根据 run_site / execution_mode / access_mode 对应要求，重新提供下面缺失的配置；不要自行补全缺失字段。",
        "required_sections": required_sections,
        "missing_field_groups": [],
        "legacy_fix_required": legacy_values_detected,
    }

    remaining = list(dict.fromkeys(missing_fields))

    execution_profile_fields = [field for field in remaining if field in EXECUTION_PROFILE_FIELD_SPECS]
    if execution_profile_fields:
        guidance["missing_field_groups"].append(
            {
                "group": "execution_profile",
                "stage": "profile",
                "message": "请先确认运行站点三元组配置。",
                "fields": [
                    _missing_field_entry(field, EXECUTION_PROFILE_FIELD_SPECS[field]) for field in execution_profile_fields
                ],
            }
        )
        remaining = [field for field in remaining if field not in execution_profile_fields]

    scnet_fields = [field for field in remaining if field in SCNET_FIELD_SPECS]
    ssh_fields = [field for field in remaining if field in SSH_FIELD_SPECS]
    cluster_fields = [field for field in remaining if field in CLUSTER_FIELD_SPECS]
    target_fields = [field for field in remaining if field in TARGET_FIELD_SPECS]

    if required_sections["runtime.scnet"] and scnet_fields:
        guidance["missing_field_groups"].append(
            {
                "group": "scnet",
                "stage": "remote_scnet_first",
                "message": "因为 run_site=remote 且 access_mode=scnet，所以必须先补齐并验证 SCnet 连接字段。",
                "fields": [_missing_field_entry(field, SCNET_FIELD_SPECS[field]) for field in scnet_fields],
            }
        )

    if required_sections["runtime.ssh"] and ssh_fields:
        stage = "remote_ssh_after_scnet" if access_mode == "scnet" else "remote_ssh_first"
        message = (
            "因为 run_site=remote，所以 SSH 字段仍然必填；请在 SCnet 补齐并验证后，再补齐 SSH 连接字段。"
            if access_mode == "scnet"
            else "因为 run_site=remote，所以必须先补齐并验证 SSH 连接字段。"
        )
        guidance["missing_field_groups"].append(
            {
                "group": "ssh",
                "stage": stage,
                "message": message,
                "fields": [_missing_field_entry(field, SSH_FIELD_SPECS[field]) for field in ssh_fields],
            }
        )

    if required_sections["runtime.cluster"] and cluster_fields:
        guidance["missing_field_groups"].append(
            {
                "group": "cluster",
                "stage": "slurm_after_connection",
                "message": "因为 execution_mode=slurm，所以必须补齐 Slurm 集群资源字段。",
                "fields": [_missing_field_entry(field, CLUSTER_FIELD_SPECS[field]) for field in cluster_fields],
            }
        )

    if target_fields:
        guidance["missing_field_groups"].append(
            {
                "group": "target",
                "stage": "hardware_or_generated_fields",
                "message": "下面这些字段应由硬件确认或脚本生成；如果当前值缺失或错误，需要先让用户确认对应配置，再重新生成/写回。",
                "fields": [_missing_field_entry(field, TARGET_FIELD_SPECS[field]) for field in target_fields],
            }
        )

    handled = set(execution_profile_fields + scnet_fields + ssh_fields + cluster_fields + target_fields)
    other_fields = [field for field in remaining if field not in handled]
    if other_fields:
        guidance["missing_field_groups"].append(
            {
                "group": "other",
                "stage": "ask_user",
                "message": "请根据字段名重新提供以下缺失配置。",
                "fields": [{"field": field, "label": field.split(".")[-1], "description": "请按字段语义重新提供"} for field in other_fields],
            }
        )

    if legacy_values_detected:
        guidance["legacy_message"] = "检测到旧版 execution_channel 或旧枚举值，需要让用户按新版 run_site / execution_mode / access_mode 重新确认配置。"

    return guidance


def validate_runtime_config(config: dict[str, Any]) -> tuple[bool, list[str], bool]:
    runtime = config.get("runtime", {})
    exec_profile = runtime.get("execution_profile", {})

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

    profile_valid = not any(
        field in missing_fields
        for field in [
            "runtime.execution_profile.run_site",
            "runtime.execution_profile.execution_mode",
            "runtime.execution_profile.access_mode",
        ]
    )

    if profile_valid:
        required_sections = infer_required_sections(config)
        missing_fields.extend(collect_missing_required_fields(config, required_sections))

    # runtime.conda is managed by onescience-installer, not validated here

    for field in [
        "runtime.target.platform_type",
        "runtime.environment.cpu.arch",
        "runtime.modules",
    ]:
        if get_nested(config, field) in (None, "", []):
            missing_fields.append(field)

    if get_nested(config, "runtime.target.accelerator_kind") not in {"dcu", "gpu"}:
        missing_fields.append("runtime.target.accelerator_kind")

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
    hardware_type: dict[str, Any],
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


def resolve_hardware_for_generate(
    *,
    run_site: str,
    ssh_data: dict[str, Any] | None,
    accelerator_kind: str,
    ssh_alias: str | None,
) -> dict[str, Any]:
    if accelerator_kind != "auto":
        return infer_hardware_from_accelerator_kind(accelerator_kind)

    if run_site == "remote":
        alias = ssh_alias or (ssh_data or {}).get("host")
        if not alias:
            return _hardware_result(
                accelerator_kind="unknown",
                accelerator_vendor="unknown",
                detected=False,
                detection_target="ssh",
            )
        return detect_remote_hardware(str(alias))

    return detect_hardware()


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
    response = {
        "config_path": str(path),
        "config_exists": True,
        "config_complete": config_complete,
        "missing_fields": missing_fields,
        "legacy_values_detected": legacy_values_detected,
        "next_action": "onescience-runtime" if config_complete else "ask_user",
        "config_summary": masked_config_summary(config),
    }
    if not config_complete:
        response["remediation"] = build_missing_field_guidance(config, missing_fields, legacy_values_detected)
    print(json.dumps(response, ensure_ascii=False, indent=2))


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
    hardware = detect_remote_hardware(args.ssh_alias) if args.ssh_alias else detect_hardware()
    print(
        json.dumps(
            {
                "hardware_detected": hardware["hardware_detected"],
                "accelerator_kind": hardware["accelerator_kind"],
                "accelerator_vendor": hardware["accelerator_vendor"],
                "cpu_arch": hardware["cpu_arch"],
                "detection_target": hardware["detection_target"],
                "next_action": "continue" if hardware["hardware_detected"] else "ask_user",
                "question": None
                if hardware["hardware_detected"]
                else "未能自动检测到运行平台加速器类型，请确认是 dcu 还是 gpu。",
                "choices": [] if hardware["hardware_detected"] else ["dcu", "gpu"],
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
                    "message": "run_site=remote 时必须由用户重新提供 SSH 字段，不能由系统自行补全。",
                    "next_action": "ask_user",
                    "do_not_autofill_missing_fields": True,
                    "missing_fields": list(SSH_FIELD_SPECS.keys()),
                    "remediation": {
                        "group": "ssh",
                        "stage": "remote_ssh_first",
                        "fields": [_missing_field_entry(field, SSH_FIELD_SPECS[field]) for field in SSH_FIELD_SPECS],
                    },
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
                    "message": "run_site=remote 且 access_mode=scnet 时，必须由用户重新提供 SCnet 字段，不能由系统自行补全。",
                    "next_action": "ask_user",
                    "do_not_autofill_missing_fields": True,
                    "missing_fields": list(SCNET_FIELD_SPECS.keys()),
                    "remediation": {
                        "group": "scnet",
                        "stage": "remote_scnet_first",
                        "fields": [_missing_field_entry(field, SCNET_FIELD_SPECS[field]) for field in SCNET_FIELD_SPECS],
                    },
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
            scnet_missing_paths = [f"runtime.scnet.{field}" for field in missing_scnet_fields]
            print(
                json.dumps(
                    {
                        "error": "Incomplete scnet data",
                        "missing_fields": scnet_missing_paths,
                        "message": "scnet_data 不完整，请让用户按字段清单重新提供缺失项，不要自行补全。",
                        "next_action": "ask_user",
                        "do_not_autofill_missing_fields": True,
                        "remediation": {
                            "group": "scnet",
                            "stage": "remote_scnet_first",
                            "fields": [_missing_field_entry(field, SCNET_FIELD_SPECS[field]) for field in scnet_missing_paths],
                        },
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
                    "message": "execution_mode=slurm 时，必须由用户重新提供 Slurm 集群资源字段，不能由系统自行补全。",
                    "next_action": "ask_user",
                    "do_not_autofill_missing_fields": True,
                    "missing_fields": list(CLUSTER_FIELD_SPECS.keys()),
                    "remediation": {
                        "group": "cluster",
                        "stage": "slurm_after_connection",
                        "fields": [_missing_field_entry(field, CLUSTER_FIELD_SPECS[field]) for field in CLUSTER_FIELD_SPECS],
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    modules = args.modules.split(",") if args.modules else None
    hardware_type = resolve_hardware_for_generate(
        run_site=run_site,
        ssh_data=ssh_data,
        accelerator_kind=args.accelerator_kind,
        ssh_alias=args.ssh_alias,
    )
    if not hardware_type.get("hardware_detected") or hardware_type.get("accelerator_kind") not in {"dcu", "gpu"}:
        print(
            json.dumps(
                {
                    "error": "Undetected accelerator type",
                    "message": "未能自动检测到运行平台加速器类型；请先确认是 dcu 还是 gpu，然后使用 --accelerator-kind 写入匹配硬件 profile 的 modules。",
                    "question": "该运行平台的加速器类型是 dcu 还是 gpu？",
                    "choices": ["dcu", "gpu"],
                    "detection_target": hardware_type.get("detection_target"),
                    "config_created": False,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

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
    p_detect_hw.add_argument("--ssh-alias", help="通过已验证 SSH Host 别名检测远程运行平台硬件")
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
    p_generate.add_argument(
        "--accelerator-kind",
        choices=["auto", "dcu", "gpu"],
        default="auto",
        help="运行平台加速器类型；auto 会先检测，检测失败时需由用户确认 dcu 或 gpu",
    )
    p_generate.add_argument("--ssh-alias", help="remote auto 检测时使用的已验证 SSH Host 别名")
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
