#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import shutil
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "install" / "manifests"
STATE_DIR = ".oneskills/install-state"
DEFAULT_RUNTIME_ASSETS = [
    ("onescience.json", "onescience.json"),
    ("skills/onescience-runtime/assets/tpl.slurm", "tpl.slurm"),
]


@dataclass
class InstallEntry:
    source: Path
    target: Path


def current_platform_name() -> str:
    return platform.system() or "Unknown"


def resolve_install_mode(requested_mode: str) -> tuple[str, str | None]:
    system_name = current_platform_name().lower()
    if requested_mode == "symlink" and system_name == "windows":
        return "copy", "Windows 下 symlink 常依赖开发者模式或管理员权限，已自动降级为 copy 模式。"
    return requested_mode, None


def load_manifest(agent: str, skills_dir_override: str | None) -> dict:
    if agent == "generic":
        if not skills_dir_override:
            raise SystemExit("--agent generic 时必须提供 --skills-dir")
        return {
            "agent": "generic",
            "skills_dir": skills_dir_override,
            "integration_targets": [],
        }
    manifest_path = MANIFEST_DIR / f"{agent}.json"
    if not manifest_path.exists():
        raise SystemExit(f"不支持的 agent: {agent}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if skills_dir_override:
        manifest["skills_dir"] = skills_dir_override
    return manifest


def list_agents() -> list[str]:
    agents = sorted(p.stem for p in MANIFEST_DIR.glob("*.json"))
    agents.append("generic")
    return agents


def build_entries(project_root: Path, manifest: dict, with_runtime_assets: bool) -> list[InstallEntry]:
    entries: list[InstallEntry] = []
    skills_dir = project_root / manifest["skills_dir"]
    for item in sorted((ROOT / "skills").iterdir()):
        if item.name.startswith(".") or item.name == "__pycache__":
            continue
        entries.append(InstallEntry(source=item, target=skills_dir / item.name))

    for mapping in manifest.get("integration_targets", []):
        entries.append(
            InstallEntry(
                source=ROOT / mapping["source"],
                target=project_root / mapping["target"],
            )
        )

    if with_runtime_assets:
        for source, target in DEFAULT_RUNTIME_ASSETS:
            entries.append(InstallEntry(source=ROOT / source, target=project_root / target))

    return entries


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def remove_path(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)


def install_copy(source: Path, target: Path) -> None:
    ensure_parent(target)
    if source.is_dir():
        shutil.copytree(source, target, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc"))
    else:
        shutil.copy2(source, target)


def install_symlink(source: Path, target: Path) -> None:
    ensure_parent(target)
    target.symlink_to(source, target_is_directory=source.is_dir())


def write_state(project_root: Path, agent: str, mode: str, with_runtime_assets: bool, entries: list[InstallEntry]) -> Path:
    state_path = project_root / STATE_DIR / f"{agent}.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "agent": agent,
        "mode": mode,
        "with_runtime_assets": with_runtime_assets,
        "items": [
            {
                "source": str(entry.source.relative_to(ROOT)),
                "target": str(entry.target.relative_to(project_root)),
            }
            for entry in entries
        ],
    }
    state_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return state_path


def read_state(project_root: Path, agent: str) -> tuple[Path, dict]:
    state_path = project_root / STATE_DIR / f"{agent}.json"
    if not state_path.exists():
        raise SystemExit(f"未找到 {agent} 的安装记录：{state_path}")
    return state_path, json.loads(state_path.read_text(encoding="utf-8"))


def install(project_root: Path, agent: str, mode: str, with_runtime_assets: bool, force: bool, skills_dir_override: str | None, dry_run: bool) -> None:
    manifest = load_manifest(agent, skills_dir_override)
    entries = build_entries(project_root, manifest, with_runtime_assets)
    effective_mode, mode_warning = resolve_install_mode(mode)
    conflicts = [entry.target for entry in entries if entry.target.exists() or entry.target.is_symlink()]
    if conflicts and not force:
        conflict_text = "\n".join(f"- {path}" for path in conflicts)
        raise SystemExit(f"发现已存在的目标路径，请使用 --force 覆盖：\n{conflict_text}")

    if dry_run:
        print(f"[dry-run] platform: {current_platform_name()}")
        if mode_warning:
            print(f"[dry-run] note: {mode_warning}")
        for entry in entries:
            print(f"[dry-run] {effective_mode}: {entry.source.relative_to(ROOT)} -> {entry.target}")
        return

    if mode_warning:
        print(f"Note: {mode_warning}")

    for entry in entries:
        if entry.target.exists() or entry.target.is_symlink():
            remove_path(entry.target)
        if effective_mode == "copy":
            install_copy(entry.source, entry.target)
        else:
            install_symlink(entry.source, entry.target)

    state_path = write_state(project_root, agent, effective_mode, with_runtime_assets, entries)
    print(f"Installed OneSkills for {agent} into: {project_root}")
    print(f"Platform: {current_platform_name()}")
    print(f"Mode: {effective_mode}")
    print(f"State: {state_path}")
    if with_runtime_assets:
        print("Runtime assets: enabled")


def uninstall(project_root: Path, agent: str, dry_run: bool) -> None:
    state_path, state = read_state(project_root, agent)
    items = [project_root / item["target"] for item in state.get("items", [])]

    if dry_run:
        for item in items:
            print(f"[dry-run] remove: {item}")
        print(f"[dry-run] remove: {state_path}")
        return

    for item in items:
        remove_path(item)
    remove_path(state_path)
    install_state_dir = project_root / STATE_DIR
    if install_state_dir.exists() and not any(install_state_dir.iterdir()):
        install_state_dir.rmdir()
        parent = install_state_dir.parent
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
    print(f"Uninstalled OneSkills for {agent} from: {project_root}")
    print(f"Platform: {current_platform_name()}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install OneSkills into Codex, Claude, Trae, or other skill-based agents.")
    parser.add_argument("--agent", choices=list_agents(), help="Target agent.")
    parser.add_argument("--project", default=".", help="Target project root. Default: current directory.")
    parser.add_argument("--mode", choices=["copy", "symlink"], default="copy", help="Install mode. Default: copy.")
    parser.add_argument("--with-runtime-assets", action="store_true", help="Also install onescience.json and tpl.slurm into the project root.")
    parser.add_argument("--uninstall", action="store_true", help="Remove items installed by this installer.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing targets during install.")
    parser.add_argument("--skills-dir", help="Custom skills directory, used with --agent generic or to override manifest defaults.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned actions without modifying files.")
    parser.add_argument("--list-agents", action="store_true", help="List supported agents and exit.")
    args = parser.parse_args()

    if args.list_agents:
        for agent in list_agents():
            print(agent)
        return 0

    if not args.agent:
        parser.error("--agent 是必填参数，除非使用 --list-agents")

    project_root = Path(args.project).resolve()
    project_root.mkdir(parents=True, exist_ok=True)

    if args.uninstall:
        uninstall(project_root, args.agent, args.dry_run)
    else:
        install(project_root, args.agent, args.mode, args.with_runtime_assets, args.force, args.skills_dir, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
