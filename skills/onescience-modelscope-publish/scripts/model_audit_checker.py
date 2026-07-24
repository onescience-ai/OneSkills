#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型文件审计/盘点工具 — Model File Audit Checker

功能：
  1. 检查 model/、weight/、scripts/、config/ 目录是否存在且非空
  2. 检查 weight/ 下大文件的 Git LFS 指针状态（是否被正确追踪）
  3. 输出审计报告（文件数量、大小汇总、缺失项列表、LFS 状态）

用法：
  python model_file_audit.py [--repo-path <PATH>] [--lfs-size-threshold <MB>]

依赖：仅使用 Python 标准库（os, sys, json, hashlib, argparse, pathlib），无第三方依赖。
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

# 核心需检查的目录
CORE_DIRECTORIES = ["model", "weight", "scripts", "conf"]

# 权重文件扩展名（应与 .gitattributes 中的 LFS 规则一致）
WEIGHT_EXTENSIONS = {
    ".pth", ".pt", ".ckpt", ".safetensors", ".bin",
    ".h5", ".keras", ".onnx", ".pb", ".pkl", ".joblib", ".weights",
}

# 默认 LFS 大小阈值（MB）：超过此阈值的权重文件应被 LFS 追踪
DEFAULT_LFS_THRESHOLD_MB = 1

# Git LFS 指针文件头部标识
LFS_POINTER_MAGIC = b"version https://git-lfs.github.com/spec/v1"


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def _format_size(size_bytes: int) -> str:
    """将字节数格式化为人类可读的大小字符串。"""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def _hash_file_sha256(filepath: str) -> str:
    """计算文件的 SHA256 哈希值。"""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (OSError, PermissionError) as e:
        return f"<无法读取: {e}>"


def _is_lfs_pointer(filepath: str) -> bool:
    """检查文件是否为 Git LFS 指针文件（而非实际内容）。"""
    try:
        with open(filepath, "rb") as f:
            header = f.read(len(LFS_POINTER_MAGIC))
        return header == LFS_POINTER_MAGIC
    except (OSError, PermissionError):
        return False


def _parse_lfs_pointer(filepath: str) -> dict:
    """解析 Git LFS 指针文件，提取 oid 和 size。"""
    info = {"oid": "unknown", "size_bytes": 0, "is_pointer": True}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("oid sha256:"):
                    info["oid"] = line.split(":", 1)[1].strip()
                elif line.startswith("size "):
                    info["size_bytes"] = int(line.split("size ")[1].strip())
    except (OSError, PermissionError):
        info["oid"] = "<无法读取>"
    return info


# ---------------------------------------------------------------------------
# 核心审计逻辑
# ---------------------------------------------------------------------------

def scan_directory(repo_path: Path, dir_name: str) -> list[dict]:
    """扫描指定子目录，返回文件信息列表。"""
    target_dir = repo_path / dir_name
    if not target_dir.is_dir():
        return []

    files = []
    for entry in sorted(target_dir.iterdir()):
        if entry.is_file() and not entry.name.startswith("."):
            try:
                stat = entry.stat()
                files.append({
                    "name": entry.name,
                    "relative_path": str(entry.relative_to(repo_path)),
                    "size_bytes": stat.st_size,
                    "size_human": _format_size(stat.st_size),
                })
            except OSError:
                files.append({
                    "name": entry.name,
                    "relative_path": str(entry.relative_to(repo_path)),
                    "size_bytes": 0,
                    "size_human": "<无法读取>",
                })
    return files


def check_lfs_status(repo_path: Path, lfs_threshold_bytes: int) -> dict:
    """检查 weight/ 目录下大文件的 LFS 状态。

    返回:
      {
        "total_files": int,
        "lfs_pointers": int,       # 已是 LFS 指针的文件数
        "large_files_missing_lfs": list[dict],  # 大文件但非 LFS 指针
        "small_files": int,        # 小文件（低于阈值）
      }
    """
    weight_dir = repo_path / "weight"
    result = {
        "total_files": 0,
        "lfs_pointers": 0,
        "large_files_missing_lfs": [],
        "small_files": 0,
    }

    if not weight_dir.is_dir():
        return result

    for entry in sorted(weight_dir.iterdir()):
        if not entry.is_file() or entry.name.startswith("."):
            continue
        ext = entry.suffix.lower()
        if ext not in WEIGHT_EXTENSIONS:
            continue

        try:
            size_bytes = entry.stat().st_size
        except OSError:
            continue

        result["total_files"] += 1

        if size_bytes >= lfs_threshold_bytes:
            is_pointer = _is_lfs_pointer(str(entry))
            if is_pointer:
                result["lfs_pointers"] += 1
            else:
                result["large_files_missing_lfs"].append({
                    "name": entry.name,
                    "size_bytes": size_bytes,
                    "size_human": _format_size(size_bytes),
                    "sha256": _hash_file_sha256(str(entry)),
                })
        else:
            result["small_files"] += 1

    return result


def generate_report(repo_path: Path, lfs_threshold_bytes: int) -> dict:
    """生成完整的审计报告。"""
    # ---- 1. 核心目录检查 ----
    dir_checks = {}
    empty_dirs = []
    all_files = {}

    for dir_name in CORE_DIRECTORIES:
        files = scan_directory(repo_path, dir_name)
        dir_checks[dir_name] = {
            "exists": (repo_path / dir_name).is_dir(),
            "files": files,
            "file_count": len(files),
            "is_empty": len(files) == 0,
            "total_size_bytes": sum(f["size_bytes"] for f in files),
        }
        all_files[dir_name] = files
        if len(files) == 0:
            empty_dirs.append(dir_name)

    # ---- 2. 根目录文件检查 ----
    root_files = scan_directory(repo_path, ".")
    # 排除子目录中的文件
    root_files = [f for f in root_files if "/" not in f["relative_path"] and "\\" not in f["relative_path"]]

    # ---- 3. LFS 状态检查 ----
    lfs_status = check_lfs_status(repo_path, lfs_threshold_bytes)

    # ---- 4. 汇总 ----
    total_files = sum(dc["file_count"] for dc in dir_checks.values())
    total_size = sum(dc["total_size_bytes"] for dc in dir_checks.values())

    # ---- 5. 关键文件检查 ----
    key_files = {
        "configurations.json": (repo_path / "configurations.json").is_file(),
        "README.md": (repo_path / "README.md").is_file(),
    }
    missing_key_files = [k for k, v in key_files.items() if not v]

    report = {
        "repo_path": str(repo_path.absolute()),
        "summary": {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_human": _format_size(total_size),
            "core_directories_checked": CORE_DIRECTORIES,
            "empty_directories": empty_dirs,
            "missing_key_files": missing_key_files,
        },
        "directory_details": dir_checks,
        "root_files": {
            "files": root_files,
            "file_count": len(root_files),
        },
        "lfs_check": lfs_status,
        "key_files_status": key_files,
        "issues": [],
        "warnings": [],
    }

    # ---- 6. 问题收集 ----
    if empty_dirs:
        report["issues"].append({
            "severity": "warning",
            "type": "empty_directories",
            "detail": f"以下核心目录为空: {', '.join(empty_dirs)}",
            "suggestion": "请确认是否需要补充对应的文件内容后再推送到 ModelScope。",
        })

    if missing_key_files:
        report["issues"].append({
            "severity": "warning",
            "type": "missing_key_files",
            "detail": f"缺少关键平台文件: {', '.join(missing_key_files)}",
            "suggestion": "请使用 onescience-modelscope-publish 技能生成模板文件，或手动创建。",
        })

    if lfs_status["large_files_missing_lfs"]:
        missing = lfs_status["large_files_missing_lfs"]
        report["issues"].append({
            "severity": "error",
            "type": "lfs_not_tracked",
            "detail": f"以下 {len(missing)} 个大文件未被 Git LFS 追踪（可能已直接提交到 Git 历史）",
            "files": [m["name"] for m in missing],
            "suggestion": "请确保 .gitattributes 中包含对应的 LFS 规则，并使用 git lfs track 追踪这些文件。",
        })

    if lfs_status["total_files"] == 0 and not empty_dirs:
        report["warnings"].append(
            "weight/ 目录未找到权重文件。请确认模型权重是否已放置到 weight/ 目录中。"
        )

    return report


def print_report(report: dict):
    """以人类可读格式输出审计报告。"""
    summary = report["summary"]
    issues = report["issues"]
    warnings = report["warnings"]
    lfs = report["lfs_check"]

    print("=" * 60)
    print("  模型文件审计报告 — Model File Audit Report")
    print("=" * 60)
    print(f"  仓库路径: {report['repo_path']}")
    print(f"  文件总数: {summary['total_files']} 个核心文件")
    print(f"  总大小:   {summary['total_size_human']}")
    print()

    # ---- 目录详情 ----
    print("-" * 60)
    print("  核心目录状态")
    print("-" * 60)
    for dir_name in CORE_DIRECTORIES:
        detail = report["directory_details"][dir_name]
        status = "[OK] 非空" if not detail["is_empty"] else "[X] 为空  "
        if not detail["exists"]:
            status = "[X] 不存在"
        print(f"  {dir_name:12s} | {status:16s} | {detail['file_count']:3d} 个文件 | {_format_size(detail['total_size_bytes'])}")

    print()
    if report["root_files"]["file_count"] > 0:
        print(f"  根目录文件: {report['root_files']['file_count']} 个")
        for f in report["root_files"]["files"]:
            print(f"    - {f['name']} ({f['size_human']})")
        print()

    # ---- LFS 状态 ----
    print("-" * 60)
    print("  Git LFS 状态 (weight/ 目录)")
    print("-" * 60)
    print(f"  权重文件总数:       {lfs['total_files']}")
    print(f"  已转 LFS 指针:      {lfs['lfs_pointers']}")
    print(f"  小文件 (低于阈值):   {lfs['small_files']}")
    print(f"  大文件但非 LFS:     {len(lfs['large_files_missing_lfs'])}")

    if lfs["large_files_missing_lfs"]:
        print()
        print("  以下大文件未被 LFS 追踪:")
        for m in lfs["large_files_missing_lfs"]:
            print(f"    - {m['name']} ({m['size_human']}, SHA256: {m['sha256'][:16]}...)")

    print()

    # ---- 关键文件 ----
    kf = report["key_files_status"]
    kf_ok = all(kf.values())
    if kf_ok:
        print("  关键平台文件: [OK] 全部就绪 (configurations.json, README.md)")
    else:
        missing = [k for k, v in kf.items() if not v]
        print(f"  关键平台文件: [X] 缺失 {', '.join(missing)}")
    print()

    # ---- 问题与告警 ----
    if issues:
        print("-" * 60)
        print("  问题与告警")
        print("-" * 60)
        for issue in issues:
            tag = "[ERROR]" if issue["severity"] == "error" else "[WARN]"
            print(f"  {tag} {issue['detail']}")
            if "suggestion" in issue:
                print(f"        建议: {issue['suggestion']}")
        print()

    if warnings:
        for w in warnings:
            print(f"  [INFO] {w}")
        print()

    # ---- 总结 ----
    print("=" * 60)
    has_errors = any(i["severity"] == "error" for i in issues)
    has_warnings = bool(issues) or bool(warnings)

    if has_errors:
        print("  结论: 存在需修复的错误，推送前请先解决。")
    elif has_warnings:
        print("  结论: 存在告警，建议在推送前确认。")
    else:
        print("  结论: 通过 — 所有检查正常，可以推送。")
    print("=" * 60)

    return 0 if not has_errors else 1


def output_json_report(report: dict, filepath: str = None):
    """以 JSON 格式输出审计报告。"""
    json_str = json.dumps(report, ensure_ascii=False, indent=2)
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"  JSON 报告已写入: {filepath}")
    else:
        print(json_str)


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="模型文件审计/盘点工具 — 检查 ModelScope 模型仓库结构完整性",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python model_file_audit.py
  python model_file_audit.py --repo-path ./MARIO
  python model_file_audit.py --repo-path ./MARIO --lfs-size-threshold 5
  python model_file_audit.py --repo-path ./MARIO --json --output audit_result.json
        """,
    )
    parser.add_argument(
        "--repo-path",
        type=str,
        default=".",
        help="模型仓库根目录路径（默认: 当前目录）",
    )
    parser.add_argument(
        "--lfs-size-threshold",
        type=float,
        default=DEFAULT_LFS_THRESHOLD_MB,
        help=f"LFS 追踪的大小阈值（MB），超过此大小的权重文件应被 LFS 追踪（默认: {DEFAULT_LFS_THRESHOLD_MB}）",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出报告",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="将 JSON 报告写入指定文件（需与 --json 配合使用）",
    )

    args = parser.parse_args()
    repo_path = Path(args.repo_path).resolve()

    if not repo_path.is_dir():
        print(f"错误: 仓库路径不存在或不是目录: {repo_path}", file=sys.stderr)
        sys.exit(2)

    lfs_threshold_bytes = int(args.lfs_size_threshold * 1024 * 1024)

    report = generate_report(repo_path, lfs_threshold_bytes)

    if args.json:
        output_json_report(report, args.output)
    else:
        exit_code = print_report(report)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
