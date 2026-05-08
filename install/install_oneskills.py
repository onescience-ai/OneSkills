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
SHARED_REFERENCES_DIR = ROOT / "references"
DEFAULT_RUNTIME_ASSETS = [
    ("onescience.json", "onescience.json"),
    ("skills/onescience-runtime/assets/tpl.slurm", "tpl.slurm"),
]
INSTALL_PROFILES = ("basic", "runtime")
CODEX_BRIDGE_MARKER = "<!-- managed-by: oneskills codex bridge -->"


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


def list_skill_directories() -> list[Path]:
    return sorted(
        item
        for item in (ROOT / "skills").iterdir()
        if item.is_dir() and not item.name.startswith(".") and item.name != "__pycache__"
    )


def append_entry(entries: list[InstallEntry], source: Path, target: Path, seen_targets: set[Path]) -> None:
    if target in seen_targets:
        return
    entries.append(InstallEntry(source=source, target=target))
    seen_targets.add(target)


def build_entries(project_root: Path, manifest: dict, with_runtime_assets: bool) -> list[InstallEntry]:
    entries: list[InstallEntry] = []
    skills_dir = project_root / manifest["skills_dir"]
    seen_targets: set[Path] = set()
    for item in sorted((ROOT / "skills").iterdir()):
        if item.name.startswith(".") or item.name == "__pycache__":
            continue
        append_entry(entries, item, skills_dir / item.name, seen_targets)

    # Installed skills consume ../../references from the namespaced skills root.
    append_entry(entries, SHARED_REFERENCES_DIR, skills_dir.parent / "references", seen_targets)

    for mapping in manifest.get("integration_targets", []):
        source = ROOT / mapping["source"]
        target = project_root / mapping["target"]
        append_entry(entries, source, target, seen_targets)

    if with_runtime_assets:
        for source, target in DEFAULT_RUNTIME_ASSETS:
            append_entry(entries, ROOT / source, project_root / target, seen_targets)

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


def codex_bridge_root() -> Path:
    return Path.home() / ".codex" / "skills"


def codex_bridge_state_path() -> Path:
    return Path.home() / ".codex" / ".oneskills" / "bridge-state.json"


def codex_bridge_skill_file(skill_name: str) -> Path:
    return codex_bridge_root() / skill_name / "SKILL.md"


def build_codex_bridge_content(skill_name: str) -> str:
    project_skill_file = f".codex/oneskills/skills/{skill_name}/SKILL.md"
    project_skill_refs = f".codex/oneskills/skills/{skill_name}/references/"
    project_shared_refs = ".codex/oneskills/references/"
    return "\n".join(
        [
            "---",
            f"name: {skill_name}",
            "description: Bridge skill for Codex. Use the project-local OneSkills installation for this skill in the current project, and resolve skill references against .codex/oneskills instead of the working directory.",
            "---",
            "",
            CODEX_BRIDGE_MARKER,
            f"# {skill_name}",
            "",
            "Use the project-local OneSkills installation for the current project.",
            "",
            "Authoritative skill file:",
            f"- `{project_skill_file}` relative to the current project root",
            "",
            "Reference resolution rules:",
            f"- `./references/...` -> `{project_skill_refs}...`",
            f"- `../../references/...` -> `{project_shared_refs}...`",
            "- Do not resolve these paths against the current working directory textually; resolve them against the project-local skill location above.",
            "",
            "If the authoritative skill file does not exist, tell the user to run the OneSkills installer in the current project first.",
        ]
    ) + "\n"


def read_codex_bridge_state() -> dict:
    path = codex_bridge_state_path()
    if not path.exists():
        return {"projects": []}
    return json.loads(path.read_text(encoding="utf-8"))


def write_codex_bridge_state(projects: list[str]) -> None:
    path = codex_bridge_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"projects": sorted(set(projects))}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def codex_bridge_conflicts(force: bool) -> list[str]:
    conflicts: list[str] = []
    for skill_dir in list_skill_directories():
        target = codex_bridge_skill_file(skill_dir.name)
        if not target.exists():
            continue
        content = target.read_text(encoding="utf-8")
        if CODEX_BRIDGE_MARKER not in content and not force:
            conflicts.append(str(target))
    return conflicts


def install_codex_bridges(force: bool, dry_run: bool) -> None:
    conflicts = codex_bridge_conflicts(force)
    if conflicts:
        conflict_text = "\n".join(f"- {item}" for item in conflicts)
        raise SystemExit(f"发现已存在且非 OneSkills 管理的 Codex bridge，请使用 --force 覆盖：\n{conflict_text}")

    for skill_dir in list_skill_directories():
        target = codex_bridge_skill_file(skill_dir.name)
        if dry_run:
            print(f"[dry-run] bridge: {skill_dir.name} -> {target}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(build_codex_bridge_content(skill_dir.name), encoding="utf-8")


def register_codex_bridge_project(project_root: Path, dry_run: bool) -> None:
    state_path = codex_bridge_state_path()
    state = read_codex_bridge_state()
    projects = set(state.get("projects", []))
    projects.add(str(project_root))
    if dry_run:
        print(f"[dry-run] bridge-state: register {project_root} -> {state_path}")
        return
    write_codex_bridge_state(sorted(projects))


def remove_codex_bridge_file(path: Path) -> None:
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8")
    if CODEX_BRIDGE_MARKER not in content:
        return
    path.unlink()
    parent = path.parent
    if parent.exists() and not any(parent.iterdir()):
        parent.rmdir()


def unregister_codex_bridge_project(project_root: Path, dry_run: bool) -> None:
    state_path = codex_bridge_state_path()
    state = read_codex_bridge_state()
    projects = {item for item in state.get("projects", []) if item != str(project_root)}
    if dry_run:
        print(f"[dry-run] bridge-state: unregister {project_root} -> {state_path}")
        if not projects:
            for skill_dir in list_skill_directories():
                print(f"[dry-run] bridge-remove: {codex_bridge_skill_file(skill_dir.name)}")
            print(f"[dry-run] bridge-remove: {state_path}")
        return
    if projects:
        write_codex_bridge_state(sorted(projects))
        return
    for skill_dir in list_skill_directories():
        remove_codex_bridge_file(codex_bridge_skill_file(skill_dir.name))
    remove_path(state_path)
    state_dir = state_path.parent
    if state_dir.exists() and not any(state_dir.iterdir()):
        state_dir.rmdir()


def write_state(project_root: Path, agent: str, mode: str, profile: str, entries: list[InstallEntry]) -> Path:
    state_path = project_root / STATE_DIR / f"{agent}.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with_runtime_assets = profile == "runtime"
    payload = {
        "agent": agent,
        "mode": mode,
        "profile": profile,
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


def load_existing_state(project_root: Path, agent: str) -> dict | None:
    state_path = project_root / STATE_DIR / f"{agent}.json"
    if not state_path.exists():
        return None
    return json.loads(state_path.read_text(encoding="utf-8"))


def install(project_root: Path, agent: str, mode: str, profile: str, force: bool, skills_dir_override: str | None, dry_run: bool) -> None:
    manifest = load_manifest(agent, skills_dir_override)
    with_runtime_assets = profile == "runtime"
    entries = build_entries(project_root, manifest, with_runtime_assets)
    effective_mode, mode_warning = resolve_install_mode(mode)
    existing_state = load_existing_state(project_root, agent)
    current_targets = {entry.target for entry in entries}
    stale_targets: list[Path] = []
    if existing_state:
        for item in existing_state.get("items", []):
            target = project_root / item["target"]
            if target not in current_targets:
                stale_targets.append(target)
    conflicts = [entry.target for entry in entries if entry.target.exists() or entry.target.is_symlink()]
    if conflicts and not force:
        conflict_text = "\n".join(f"- {path}" for path in conflicts)
        raise SystemExit(f"发现已存在的目标路径，请使用 --force 覆盖：\n{conflict_text}")

    if dry_run:
        print(f"[dry-run] platform: {current_platform_name()}")
        if mode_warning:
            print(f"[dry-run] note: {mode_warning}")
        print(f"[dry-run] profile: {profile}")
        for target in stale_targets:
            print(f"[dry-run] remove stale: {target}")
        for entry in entries:
            print(f"[dry-run] {effective_mode}: {entry.source.relative_to(ROOT)} -> {entry.target}")
        if agent == "codex":
            install_codex_bridges(force, dry_run=True)
            register_codex_bridge_project(project_root, dry_run=True)
        return

    if mode_warning:
        print(f"Note: {mode_warning}")

    for target in stale_targets:
        remove_path(target)

    for entry in entries:
        if entry.target.exists() or entry.target.is_symlink():
            remove_path(entry.target)
        if effective_mode == "copy":
            install_copy(entry.source, entry.target)
        else:
            install_symlink(entry.source, entry.target)

    if agent == "codex":
        install_codex_bridges(force, dry_run=False)
        register_codex_bridge_project(project_root, dry_run=False)

    state_path = write_state(project_root, agent, effective_mode, profile, entries)
    print(f"Installed OneSkills for {agent} into: {project_root}")
    print(f"Platform: {current_platform_name()}")
    print(f"Mode: {effective_mode}")
    print(f"Profile: {profile}")
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
        if agent == "codex":
            unregister_codex_bridge_project(project_root, dry_run=True)
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
    if agent == "codex":
        unregister_codex_bridge_project(project_root, dry_run=False)
    print(f"Uninstalled OneSkills for {agent} from: {project_root}")
    print(f"Platform: {current_platform_name()}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install OneSkills into Codex, Claude, Trae, or other skill-based agents.")
    parser.add_argument("--agent", choices=list_agents(), help="Target agent.")
    parser.add_argument("--project", default=".", help="Target project root. Default: current directory.")
    parser.add_argument("--mode", choices=["copy", "symlink"], default="copy", help="Install mode. Default: copy.")
    parser.add_argument(
        "--profile",
        choices=INSTALL_PROFILES,
        default="basic",
        help="Install profile. basic: install skills/references/integrations only; runtime: also install onescience.json and tpl.slurm. Default: basic.",
    )
    parser.add_argument("--with-runtime-assets", action="store_true", help="Compatibility alias for --profile runtime.")
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
    profile = "runtime" if args.with_runtime_assets else args.profile

    if args.uninstall:
        uninstall(project_root, args.agent, args.dry_run)
    else:
        install(project_root, args.agent, args.mode, profile, args.force, args.skills_dir, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
