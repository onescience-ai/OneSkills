#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import shutil
import tempfile
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_DIR = ROOT / "install" / "manifests"
CONTRACT_PATH = ROOT / "install" / "contract.json"
PROFILE_TARGETS_PATH = ROOT / "install" / "profile_targets.json"
BRIDGE_TEMPLATE_PATH = ROOT / "install" / "templates" / "bridge_skill.md.tpl"
STATE_DIR = ".oneskills/install-state"
SHARED_REFERENCES_DIR = ROOT / "references"
INTEGRATIONS_DIR = ROOT / "integrations"
GENERIC_AGENT = "generic"
ONESCIENCE_SOURCE_URL = "https://gitee.com/onescience-ai/onescience/releases/download/0.3.0/onescience-0.3.0.zip"
MCP_TOOL_URL = "https://gitee.com/onescience-ai/agent-cloud-interaction-protocol/releases/download/v0.1/scnet-mcp-server.exe"
MCP_TOOL_FILENAME = "scnet-mcp-server.exe"


@dataclass
class InstallEntry:
    source: Path | None
    target: Path
    url: str | None = None
    kind: str = "path"


@dataclass
class InstallPlan:
    bridge_config: dict | None
    skills_dir: str
    entries: list[InstallEntry]
    effective_mode: str
    mode_warning: str | None
    stale_targets: list[Path]


@dataclass
class UninstallPlan:
    bridge_config: dict | None
    state_path: Path
    items: list[Path]


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def current_platform_name() -> str:
    return platform.system() or "Unknown"


def resolve_install_mode(requested_mode: str) -> tuple[str, str | None]:
    system_name = current_platform_name().lower()
    if requested_mode == "symlink" and system_name == "windows":
        return "copy", "Windows 下 symlink 常依赖开发者模式或管理员权限，已自动降级为 copy 模式。"
    return requested_mode, None


def load_profile_catalog() -> dict[str, dict[str, object]]:
    data = json.loads(PROFILE_TARGETS_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("install/profile_targets.json 根节点必须是对象")
    normalized: dict[str, dict[str, object]] = {}
    for profile, value in data.items():
        if isinstance(value, list):
            normalized[profile] = {"skills": "all", "assets": value}
            continue
        if not isinstance(value, dict):
            raise SystemExit("install/profile_targets.json 的 profile 配置必须是对象或列表")
        skills = value.get("skills", "all")
        assets = value.get("assets", [])
        if skills != "all" and not (
            isinstance(skills, list) and all(isinstance(item, str) and item.strip() for item in skills)
        ):
            raise SystemExit("install/profile_targets.json.profile.skills 必须是 \"all\" 或非空字符串列表")
        if not isinstance(assets, list):
            raise SystemExit("install/profile_targets.json.profile.assets 必须是列表")
        normalized[profile] = {"skills": skills, "assets": assets}
    return normalized


PROFILE_CATALOG = load_profile_catalog()
INSTALL_PROFILES = tuple(PROFILE_CATALOG)


def load_install_contract() -> dict:
    data = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("install/contract.json 根节点必须是对象")

    state_schema_version = data.get("state_schema_version")
    bridge_marker = data.get("bridge_marker")
    legacy_bridge_markers = data.get("legacy_bridge_markers")
    supported_bridge_kinds = data.get("supported_bridge_kinds")
    bridge_template_tokens = data.get("required_bridge_template_tokens")

    if not isinstance(state_schema_version, int) or state_schema_version < 1:
        raise SystemExit("install/contract.json.state_schema_version 必须是正整数")
    if not isinstance(bridge_marker, str) or not bridge_marker.strip():
        raise SystemExit("install/contract.json.bridge_marker 必须是非空字符串")
    if not isinstance(legacy_bridge_markers, list) or not all(isinstance(item, str) and item.strip() for item in legacy_bridge_markers):
        raise SystemExit("install/contract.json.legacy_bridge_markers 必须是非空字符串列表")
    if not isinstance(supported_bridge_kinds, list) or not all(isinstance(item, str) and item.strip() for item in supported_bridge_kinds):
        raise SystemExit("install/contract.json.supported_bridge_kinds 必须是非空字符串列表")
    if not isinstance(bridge_template_tokens, list) or not all(isinstance(item, str) and item.strip() for item in bridge_template_tokens):
        raise SystemExit("install/contract.json.required_bridge_template_tokens 必须是非空字符串列表")

    return data


INSTALL_CONTRACT = load_install_contract()
STATE_SCHEMA_VERSION = INSTALL_CONTRACT["state_schema_version"]
BRIDGE_MARKER = INSTALL_CONTRACT["bridge_marker"]
LEGACY_BRIDGE_MARKERS = set(INSTALL_CONTRACT["legacy_bridge_markers"])
SUPPORTED_BRIDGE_KINDS = set(INSTALL_CONTRACT["supported_bridge_kinds"])
REQUIRED_BRIDGE_TEMPLATE_TOKENS = set(INSTALL_CONTRACT["required_bridge_template_tokens"])


def load_bridge_template() -> str:
    content = BRIDGE_TEMPLATE_PATH.read_text(encoding="utf-8")
    missing_tokens = [token for token in sorted(REQUIRED_BRIDGE_TEMPLATE_TOKENS) if token not in content]
    if missing_tokens:
        missing_text = ", ".join(missing_tokens)
        raise SystemExit(f"install bridge 模板缺少占位符: {missing_text}")
    return content


BRIDGE_TEMPLATE = load_bridge_template()


def namespace_root_from_skills_dir(skills_dir: str) -> str:
    return PurePosixPath(skills_dir).parent.as_posix()


def manifest_skills_dir(manifest: dict) -> str:
    return (PurePosixPath(manifest["namespace_root"]) / "skills").as_posix()


def build_generic_manifest(skills_dir_override: str | None, require_skills_dir: bool) -> dict:
    if require_skills_dir and not skills_dir_override:
        raise SystemExit("--agent generic 时必须提供 --skills-dir")
    manifest = {
        "agent": GENERIC_AGENT,
        "integration_sources": [],
    }
    if skills_dir_override:
        manifest["namespace_root"] = namespace_root_from_skills_dir(skills_dir_override)
    return manifest


def load_manifest(agent: str, skills_dir_override: str | None, require_skills_dir: bool = True) -> dict:
    if agent == GENERIC_AGENT:
        return build_generic_manifest(skills_dir_override, require_skills_dir=require_skills_dir)
    manifest_path = MANIFEST_DIR / f"{agent}.json"
    if not manifest_path.exists():
        raise SystemExit(f"不支持的 agent: {agent}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if skills_dir_override:
        manifest["namespace_root"] = namespace_root_from_skills_dir(skills_dir_override)
    return manifest


def resolve_bridge_config(manifest: dict) -> dict | None:
    bridge = manifest.get("bridge")
    if bridge is None:
        return None
    if not isinstance(bridge, dict):
        raise SystemExit(f"{manifest.get('agent', 'unknown')} manifest 的 bridge 必须是对象")

    kind = bridge.get("kind")
    root = bridge.get("root")
    state_path = bridge.get("state_path")
    if kind not in SUPPORTED_BRIDGE_KINDS:
        raise SystemExit(f"{manifest.get('agent', 'unknown')} manifest 的 bridge.kind 非法: {kind}")
    if not isinstance(root, str) or not root.strip():
        raise SystemExit(f"{manifest.get('agent', 'unknown')} manifest 的 bridge.root 必须是非空字符串")
    if not isinstance(state_path, str) or not state_path.strip():
        raise SystemExit(f"{manifest.get('agent', 'unknown')} manifest 的 bridge.state_path 必须是非空字符串")

    return {
        "agent": manifest.get("agent", "unknown"),
        "kind": kind,
        "root": Path(root).expanduser(),
        "state_path": Path(state_path).expanduser(),
    }


def list_agents() -> list[str]:
    agents = sorted(p.stem for p in MANIFEST_DIR.glob("*.json"))
    agents.append(GENERIC_AGENT)
    return agents


def list_skill_directories(selected_skill_names: set[str] | None = None) -> list[Path]:
    directories = sorted(
        item
        for item in (ROOT / "skills").iterdir()
        if item.is_dir()
        and not item.name.startswith(".")
        and item.name != "__pycache__"
        and item.name != "references"
    )
    if selected_skill_names is None:
        return directories
    return [item for item in directories if item.name in selected_skill_names]


def append_entry(entries: list[InstallEntry], source: Path, target: Path, seen_targets: set[Path]) -> None:
    if target in seen_targets:
        return
    entries.append(InstallEntry(source=source, target=target))
    seen_targets.add(target)


def append_url_entry(
    entries: list[InstallEntry],
    url: str,
    target: Path,
    seen_targets: set[Path],
    kind: str,
) -> None:
    if target in seen_targets:
        return
    entries.append(InstallEntry(source=None, target=target, url=url, kind=kind))
    seen_targets.add(target)


def skill_names_for_profile(profile: str) -> set[str] | None:
    config = PROFILE_CATALOG.get(profile, {})
    if not isinstance(config, dict):
        return None
    skills = config.get("skills", "all")
    if skills == "all":
        return None
    if isinstance(skills, list):
        return {item for item in skills if isinstance(item, str) and item.strip()}
    return None


def profile_assets(profile: str) -> list[dict[str, str]]:
    config = PROFILE_CATALOG.get(profile, {})
    if not isinstance(config, dict):
        return []
    assets = config.get("assets", [])
    return assets if isinstance(assets, list) else []


def build_entries(
    project_root: Path,
    manifest: dict,
    profile: str,
    agent: str,
    with_onescience_source: bool = True,
    onescience_source_url: str = ONESCIENCE_SOURCE_URL,
) -> list[InstallEntry]:
    entries: list[InstallEntry] = []
    namespace_root = project_root / manifest["namespace_root"]
    skills_dir = namespace_root / "skills"
    seen_targets: set[Path] = set()
    selected_skill_names = skill_names_for_profile(profile)
    for item in sorted((ROOT / "skills").iterdir()):
        if item.name.startswith(".") or item.name == "__pycache__" or item.name == "references":
            continue
        if selected_skill_names is not None and item.name not in selected_skill_names:
            continue
        append_entry(entries, item, skills_dir / item.name, seen_targets)

    # Installed skills consume ../../references from the namespaced skills root.
    append_entry(entries, SHARED_REFERENCES_DIR, namespace_root / "references", seen_targets)

    if agent == "codex" and with_onescience_source:
        append_url_entry(
            entries,
            onescience_source_url,
            namespace_root / "onescience",
            seen_targets,
            "onescience_source",
        )

    integrations_root = namespace_root / "integrations"
    for source_rel in manifest.get("integration_sources", []):
        source = INTEGRATIONS_DIR / source_rel
        target = integrations_root / source_rel
        append_entry(entries, source, target, seen_targets)

    for mapping in profile_assets(profile):
        append_entry(entries, ROOT / mapping["source"], project_root / mapping["target"], seen_targets)

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


def remove_empty_dir(path: Path) -> None:
    if path.exists() and not any(path.iterdir()):
        path.rmdir()


def codex_mcp_tool_path(project_root: Path) -> Path:
    return project_root / ".codex" / "oneskills" / "mcp-tools" / MCP_TOOL_FILENAME


def install_codex_mcp_tools(project_root: Path, force: bool, dry_run: bool) -> Path:
    target = codex_mcp_tool_path(project_root)
    if dry_run:
        action = "overwrite" if target.exists() else "download"
        print(f"[dry-run] mcp-tools: {action} {MCP_TOOL_URL} -> {target}")
        return target

    if target.exists() and target.is_dir():
        if not force:
            raise SystemExit(f"发现已存在的 MCP tools 目录，请使用 --force 覆盖：{target}")
        remove_path(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    temp_target = target.with_suffix(target.suffix + ".tmp")
    remove_path(temp_target)
    try:
        urllib.request.urlretrieve(MCP_TOOL_URL, temp_target)
        remove_path(target)
        temp_target.replace(target)
    except Exception as exc:
        remove_path(temp_target)
        raise SystemExit(f"下载 Codex MCP tool 失败：{MCP_TOOL_URL}") from exc
    return target


def safe_extract_zip(zip_path: Path, extract_dir: Path) -> None:
    extract_root = extract_dir.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            member_target = (extract_dir / member.filename).resolve()
            try:
                member_target.relative_to(extract_root)
            except ValueError:
                raise SystemExit(f"Refusing unsafe zip member path: {member.filename}")
        archive.extractall(extract_dir)


def find_archive_content_root(extract_dir: Path) -> Path:
    children = [item for item in extract_dir.iterdir() if item.name != "__MACOSX"]
    if len(children) == 1 and children[0].is_dir():
        return children[0]
    return extract_dir


def install_onescience_source(url: str, target: Path, force: bool, dry_run: bool) -> None:
    if dry_run:
        action = "overwrite" if target.exists() else "download"
        print(f"[dry-run] onescience-source: {action} {url} -> {target}")
        return
    if target.exists() or target.is_symlink():
        if not force:
            raise SystemExit(f"OneScience 源码目录已存在，请使用 --force 覆盖：{target}")
        remove_path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="onescience-source-") as tmpdir:
        tmp_path = Path(tmpdir)
        zip_path = tmp_path / "onescience.zip"
        try:
            urllib.request.urlretrieve(url, zip_path)
            extract_dir = tmp_path / "extract"
            extract_dir.mkdir()
            safe_extract_zip(zip_path, extract_dir)
            content_root = find_archive_content_root(extract_dir)
            shutil.copytree(
                content_root,
                target,
                ignore=shutil.ignore_patterns(".git", ".DS_Store", "__pycache__", "*.pyc"),
            )
        except Exception as exc:
            remove_path(target)
            raise SystemExit(f"下载或解压 OneScience 源码失败：{url}") from exc


def install_copy(source: Path, target: Path) -> None:
    ensure_parent(target)
    if source.is_dir():
        shutil.copytree(source, target, ignore=shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc"))
    else:
        shutil.copy2(source, target)


def install_symlink(source: Path, target: Path) -> None:
    ensure_parent(target)
    target.symlink_to(source, target_is_directory=source.is_dir())


def bridge_skill_file(bridge_root: Path, skill_name: str) -> Path:
    return bridge_root / skill_name / "SKILL.md"


def managed_bridge_markers() -> set[str]:
    return {BRIDGE_MARKER, *LEGACY_BRIDGE_MARKERS}


def is_managed_bridge_content(content: str) -> bool:
    return any(marker in content for marker in managed_bridge_markers())


def build_bridge_content(skill_name: str, skills_dir: str) -> str:
    skills_root = PurePosixPath(skills_dir)
    project_skill_file = (skills_root / skill_name / "SKILL.md").as_posix()
    project_skill_refs = (skills_root / skill_name / "references").as_posix() + "/"
    project_shared_refs = (skills_root.parent / "references").as_posix() + "/"
    project_onescience_source = (skills_root.parent / "onescience").as_posix() + "/"
    return BRIDGE_TEMPLATE.format(
        skill_name=skill_name,
        bridge_marker=BRIDGE_MARKER,
        project_skill_file=project_skill_file,
        project_skill_refs=project_skill_refs,
        project_shared_refs=project_shared_refs,
        project_onescience_source=project_onescience_source,
    )


def read_bridge_state(state_path: Path) -> dict:
    if not state_path.exists():
        return {"projects": []}
    return read_json(state_path)


def write_bridge_state(state_path: Path, projects: list[str]) -> None:
    payload = {"projects": sorted(set(projects))}
    write_json(state_path, payload)


def bridge_conflicts(bridge_config: dict, force: bool, selected_skill_names: set[str] | None = None) -> list[str]:
    conflicts: list[str] = []
    for skill_dir in list_skill_directories(selected_skill_names):
        target = bridge_skill_file(bridge_config["root"], skill_dir.name)
        if not target.exists():
            continue
        content = target.read_text(encoding="utf-8")
        if not is_managed_bridge_content(content) and not force:
            conflicts.append(str(target))
    return conflicts


def install_bridges(
    bridge_config: dict,
    skills_dir: str,
    force: bool,
    dry_run: bool,
    selected_skill_names: set[str] | None = None,
) -> None:
    conflicts = bridge_conflicts(bridge_config, force, selected_skill_names)
    if conflicts:
        conflict_text = "\n".join(f"- {item}" for item in conflicts)
        raise SystemExit(f"发现已存在且非 OneSkills 管理的 bridge，请使用 --force 覆盖：\n{conflict_text}")

    for skill_dir in list_skill_directories(selected_skill_names):
        target = bridge_skill_file(bridge_config["root"], skill_dir.name)
        if dry_run:
            print(f"[dry-run] bridge: {skill_dir.name} -> {target}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(build_bridge_content(skill_dir.name, skills_dir), encoding="utf-8")


def register_bridge_project(bridge_config: dict, project_root: Path, dry_run: bool) -> None:
    state_path = bridge_config["state_path"]
    state = read_bridge_state(state_path)
    projects = set(state.get("projects", []))
    projects.add(str(project_root))
    if dry_run:
        print(f"[dry-run] bridge-state: register {project_root} -> {state_path}")
        return
    write_bridge_state(state_path, sorted(projects))


def remove_bridge_file(path: Path) -> None:
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8")
    if not is_managed_bridge_content(content):
        return
    path.unlink()
    remove_empty_dir(path.parent)


def unregister_bridge_project(bridge_config: dict, project_root: Path, dry_run: bool) -> None:
    state_path = bridge_config["state_path"]
    state = read_bridge_state(state_path)
    projects = {item for item in state.get("projects", []) if item != str(project_root)}
    if dry_run:
        print(f"[dry-run] bridge-state: unregister {project_root} -> {state_path}")
        if not projects:
            for skill_dir in list_skill_directories():
                print(f"[dry-run] bridge-remove: {bridge_skill_file(bridge_config['root'], skill_dir.name)}")
            print(f"[dry-run] bridge-remove: {state_path}")
        return
    if projects:
        write_bridge_state(state_path, sorted(projects))
        return
    for skill_dir in list_skill_directories():
        remove_bridge_file(bridge_skill_file(bridge_config["root"], skill_dir.name))
    remove_path(state_path)
    remove_empty_dir(state_path.parent)


def state_file_path(project_root: Path, agent: str) -> Path:
    return project_root / STATE_DIR / f"{agent}.json"


def write_state(
    project_root: Path,
    agent: str,
    mode: str,
    profile: str,
    entries: list[InstallEntry],
    mcp_tool_path: Path | None = None,
) -> Path:
    state_path = state_file_path(project_root, agent)
    payload = {
        "schema_version": STATE_SCHEMA_VERSION,
        "agent": agent,
        "mode": mode,
        "profile": profile,
        "targets": [str(entry.target.relative_to(project_root)) for entry in entries],
    }
    if mcp_tool_path:
        payload["mcp_tools"] = {
            "url": MCP_TOOL_URL,
            "target": str(mcp_tool_path.relative_to(project_root)),
        }
    write_json(state_path, payload)
    return state_path


def read_state(project_root: Path, agent: str) -> tuple[Path, dict]:
    state_path = state_file_path(project_root, agent)
    if not state_path.exists():
        raise SystemExit(f"未找到 {agent} 的安装记录：{state_path}")
    return state_path, read_json(state_path)


def load_existing_state(project_root: Path, agent: str) -> dict | None:
    state_path = state_file_path(project_root, agent)
    if not state_path.exists():
        return None
    return read_json(state_path)


def iter_state_targets(state: dict) -> list[str]:
    targets = state.get("targets")
    if isinstance(targets, list):
        return [item for item in targets if isinstance(item, str) and item.strip()]

    items = state.get("items")
    if isinstance(items, list):
        legacy_targets: list[str] = []
        for item in items:
            if isinstance(item, dict):
                target = item.get("target")
                if isinstance(target, str) and target.strip():
                    legacy_targets.append(target)
        return legacy_targets

    return []


def collect_stale_targets(
    project_root: Path,
    existing_state: dict | None,
    current_targets: set[Path],
    agent: str,
    with_mcp_tools: bool,
) -> list[Path]:
    stale_targets: list[Path] = []
    if not existing_state:
        return stale_targets
    for target_str in iter_state_targets(existing_state):
        target = project_root / target_str
        if target not in current_targets:
            stale_targets.append(target)
    existing_mcp_tools = existing_state.get("mcp_tools")
    current_mcp_tool = codex_mcp_tool_path(project_root) if agent == "codex" and with_mcp_tools else None
    if existing_mcp_tools:
        existing_mcp_target = project_root / existing_mcp_tools["target"]
        if existing_mcp_target != current_mcp_tool:
            stale_targets.append(existing_mcp_target)
    return stale_targets


def collect_conflicts(entries: list[InstallEntry]) -> list[Path]:
    return [entry.target for entry in entries if entry.target.exists() or entry.target.is_symlink()]


def build_install_plan(
    project_root: Path,
    agent: str,
    mode: str,
    profile: str,
    skills_dir_override: str | None,
    with_onescience_source: bool = True,
    onescience_source_url: str = ONESCIENCE_SOURCE_URL,
    with_mcp_tools: bool = False,
) -> InstallPlan:
    manifest = load_manifest(agent, skills_dir_override)
    bridge_config = resolve_bridge_config(manifest)
    skills_dir = manifest_skills_dir(manifest)
    entries = build_entries(project_root, manifest, profile, agent, with_onescience_source, onescience_source_url)
    effective_mode, mode_warning = resolve_install_mode(mode)
    existing_state = load_existing_state(project_root, agent)
    current_targets = {entry.target for entry in entries}
    stale_targets = collect_stale_targets(project_root, existing_state, current_targets, agent, with_mcp_tools)
    return InstallPlan(
        bridge_config=bridge_config,
        skills_dir=skills_dir,
        entries=entries,
        effective_mode=effective_mode,
        mode_warning=mode_warning,
        stale_targets=stale_targets,
    )


def print_install_plan(plan: InstallPlan, profile: str, onescience_source_url: str) -> None:
    print(f"[dry-run] platform: {current_platform_name()}")
    if plan.mode_warning:
        print(f"[dry-run] note: {plan.mode_warning}")
    print(f"[dry-run] profile: {profile}")
    for target in plan.stale_targets:
        print(f"[dry-run] remove stale: {target}")
    for entry in plan.entries:
        if entry.kind == "onescience_source":
            install_onescience_source(entry.url or onescience_source_url, entry.target, force=False, dry_run=True)
        else:
            assert entry.source is not None
            print(f"[dry-run] {plan.effective_mode}: {entry.source.relative_to(ROOT)} -> {entry.target}")


def execute_install_entries(entries: list[InstallEntry], mode: str, onescience_source_url: str, force: bool) -> None:
    for entry in entries:
        if entry.target.exists() or entry.target.is_symlink():
            remove_path(entry.target)
        if entry.kind == "onescience_source":
            install_onescience_source(entry.url or onescience_source_url, entry.target, force, dry_run=False)
        else:
            assert entry.source is not None
            if mode == "copy":
                install_copy(entry.source, entry.target)
            else:
                install_symlink(entry.source, entry.target)


def profile_has_assets(profile: str) -> bool:
    return bool(profile_assets(profile))


def build_uninstall_plan(project_root: Path, agent: str, skills_dir_override: str | None) -> UninstallPlan:
    manifest = load_manifest(agent, skills_dir_override, require_skills_dir=False)
    bridge_config = resolve_bridge_config(manifest)
    state_path, state = read_state(project_root, agent)
    items = [project_root / target for target in iter_state_targets(state)]
    mcp_tools = state.get("mcp_tools")
    if mcp_tools:
        items.append(project_root / mcp_tools["target"])
    return UninstallPlan(
        bridge_config=bridge_config,
        state_path=state_path,
        items=items,
    )


def print_uninstall_plan(plan: UninstallPlan) -> None:
    for item in plan.items:
        print(f"[dry-run] remove: {item}")
    print(f"[dry-run] remove: {plan.state_path}")


def install(
    project_root: Path,
    agent: str,
    mode: str,
    profile: str,
    force: bool,
    skills_dir_override: str | None,
    dry_run: bool,
    with_mcp_tools: bool,
    with_onescience_source: bool = True,
    onescience_source_url: str = ONESCIENCE_SOURCE_URL,
) -> None:
    plan = build_install_plan(
        project_root,
        agent,
        mode,
        profile,
        skills_dir_override,
        with_onescience_source=with_onescience_source,
        onescience_source_url=onescience_source_url,
        with_mcp_tools=with_mcp_tools,
    )
    conflicts = collect_conflicts(plan.entries)
    if conflicts and not force:
        conflict_text = "\n".join(f"- {path}" for path in conflicts)
        raise SystemExit(f"发现已存在的目标路径，请使用 --force 覆盖：\n{conflict_text}")

    selected_skill_names = skill_names_for_profile(profile)
    if dry_run:
        print_install_plan(plan, profile, onescience_source_url)
        if agent == "codex" and with_mcp_tools:
            install_codex_mcp_tools(project_root, force, dry_run=True)
        if plan.bridge_config:
            install_bridges(
                plan.bridge_config,
                plan.skills_dir,
                force,
                dry_run=True,
                selected_skill_names=selected_skill_names,
            )
            register_bridge_project(plan.bridge_config, project_root, dry_run=True)
        return

    if plan.mode_warning:
        print(f"Note: {plan.mode_warning}")

    for target in plan.stale_targets:
        remove_path(target)

    execute_install_entries(plan.entries, plan.effective_mode, onescience_source_url, force)

    mcp_tool_path: Path | None = None
    if agent == "codex" and with_mcp_tools:
        mcp_tool_path = install_codex_mcp_tools(project_root, force, dry_run=False)
    if plan.bridge_config:
        install_bridges(
            plan.bridge_config,
            plan.skills_dir,
            force,
            dry_run=False,
            selected_skill_names=selected_skill_names,
        )
        register_bridge_project(plan.bridge_config, project_root, dry_run=False)

    state_path = write_state(project_root, agent, plan.effective_mode, profile, plan.entries, mcp_tool_path)
    print(f"Installed OneSkills for {agent} into: {project_root}")
    print(f"Platform: {current_platform_name()}")
    print(f"Mode: {plan.effective_mode}")
    print(f"Profile: {profile}")
    print(f"State: {state_path}")
    if profile_has_assets(profile):
        print(f"Profile assets: enabled ({profile})")
    if mcp_tool_path:
        print(f"MCP tool: {mcp_tool_path}")
    if agent == "codex" and with_onescience_source:
        ns = PurePosixPath(plan.skills_dir).parent.as_posix()
        print(f"OneScience source: {ns}/onescience")


def uninstall(project_root: Path, agent: str, skills_dir_override: str | None, dry_run: bool) -> None:
    plan = build_uninstall_plan(project_root, agent, skills_dir_override)

    if dry_run:
        print_uninstall_plan(plan)
        if plan.bridge_config:
            unregister_bridge_project(plan.bridge_config, project_root, dry_run=True)
        return

    for item in plan.items:
        remove_path(item)
    remove_path(plan.state_path)
    install_state_dir = project_root / STATE_DIR
    if install_state_dir.exists() and not any(install_state_dir.iterdir()):
        install_state_dir.rmdir()
        remove_empty_dir(install_state_dir.parent)
    if plan.bridge_config:
        unregister_bridge_project(plan.bridge_config, project_root, dry_run=False)
    print(f"Uninstalled OneSkills for {agent} from: {project_root}")
    print(f"Platform: {current_platform_name()}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install OneSkills into supported skill-based agents.")
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
    parser.add_argument("--skip-mcp-tools", action="store_true", help="Codex only: do not download bundled MCP tool binary.")
    parser.add_argument(
        "--skip-onescience-source",
        action="store_true",
        help="Codex only: do not install the local OneScience source snapshot used by code-reading skills.",
    )
    parser.add_argument(
        "--onescience-source-url",
        default=ONESCIENCE_SOURCE_URL,
        help="OneScience source zip URL. Default: OneScience 0.3.0 release zip.",
    )
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
        uninstall(project_root, args.agent, args.skills_dir, args.dry_run)
    else:
        install(
            project_root,
            args.agent,
            args.mode,
            profile,
            args.force,
            args.skills_dir,
            args.dry_run,
            with_mcp_tools=args.agent == "codex" and not args.skip_mcp_tools,
            with_onescience_source=args.agent != "codex" or not args.skip_onescience_source,
            onescience_source_url=args.onescience_source_url,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
