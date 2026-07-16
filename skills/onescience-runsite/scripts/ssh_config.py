#!/usr/bin/env python3
"""管理 SSH 配置文件 (~/.ssh/config)。"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def default_ssh_config_path() -> Path:
    """返回默认 SSH 配置文件路径。"""
    return Path.home() / ".ssh" / "config"


def safe_alias(host: str) -> str:
    """生成安全的 Host 别名。"""
    value = re.sub(r"[^A-Za-z0-9_.-]+", "-", host.strip()).strip("-").lower()
    return f"onescience-{value or 'remote'}"


def upsert_ssh_host(
    path: Path,
    alias: str,
    host: str,
    port: int,
    user: str,
    identity: str
) -> None:
    """新增或更新 SSH Host 块,保持幂等性。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    lines = existing.splitlines()
    start: int | None = None
    end = len(lines)

    # 查找已有的 Host 块
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.lower().startswith("host "):
            continue
        names = stripped.split()[1:]
        if alias in names:
            start = idx
            end = len(lines)
            for j in range(idx + 1, len(lines)):
                if lines[j].strip().lower().startswith("host "):
                    end = j
                    break
            break

    # 构建新的 Host 块
    block = [
        f"Host {alias}",
        f"    HostName {host}",
        f"    Port {port}",
        f"    User {user}",
        f"    IdentityFile {identity}",
    ]

    # 更新或追加
    if start is None:
        new_lines = lines[:]
        if new_lines and new_lines[-1].strip():
            new_lines.append("")
        new_lines.extend(block)
    else:
        new_lines = lines[:start] + block + lines[end:]

    # 写入文件
    path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def read_ssh_hosts(path: Path) -> list[dict[str, str]]:
    """读取 SSH 配置文件中的所有 Host。"""
    if not path.exists():
        return []

    hosts = []
    current_host = None

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("host "):
            if current_host:
                hosts.append(current_host)
            names = stripped.split()[1:]
            current_host = {"alias": names[0] if names else "unknown"}
        elif current_host and stripped:
            if stripped.lower().startswith("hostname "):
                current_host["hostname"] = stripped.split(maxsplit=1)[1]
            elif stripped.lower().startswith("port "):
                current_host["port"] = stripped.split(maxsplit=1)[1]
            elif stripped.lower().startswith("user "):
                current_host["user"] = stripped.split(maxsplit=1)[1]
            elif stripped.lower().startswith("identityfile "):
                current_host["identity_file"] = stripped.split(maxsplit=1)[1]

    if current_host:
        hosts.append(current_host)

    return hosts


def find_ssh_host(path: Path, alias: str) -> dict[str, str] | None:
    """按 Host 别名查找 SSH 配置。"""
    for host in read_ssh_hosts(path):
        if host.get("alias") == alias:
            return host
    return None


def extract_bad_permission_path(output: str) -> str | None:
    """从 OpenSSH bad permissions 错误中提取私钥路径。"""
    match = re.search(r"Permissions for ['\"]([^'\"]+)['\"]", output)
    if match:
        return match.group(1)
    return None


def is_bad_permission_error(output: str) -> bool:
    lowered = output.lower()
    return "bad permissions" in lowered or "are too open" in lowered


def fix_windows_identity_permissions(identity: str) -> tuple[bool, str]:
    """用 icacls 修复 Windows OpenSSH 私钥权限过宽问题。"""
    user = os.environ.get("USERNAME") or os.getlogin()
    normalized_identity = re.sub(r"\\+", r"\\", identity.replace("/", "\\"))
    normalized_identity = str(Path(normalized_identity).expanduser())
    command = ["icacls", normalized_identity, "/grant:r", f"{user}:F"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
    except Exception as exc:
        return False, str(exc)
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output.strip()


def run_ssh_probe(config_path: Path, alias: str, connect_timeout: int) -> subprocess.CompletedProcess[str]:
    command = [
        "ssh",
        "-F",
        str(config_path),
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={connect_timeout}",
        "-o",
        "StrictHostKeyChecking=accept-new",
        alias,
        "true",
    ]
    return subprocess.run(command, capture_output=True, text=True, timeout=connect_timeout + 10)


def cmd_add(args: argparse.Namespace) -> None:
    """添加或更新 SSH Host 配置。"""
    path = Path(args.ssh_config) if args.ssh_config else default_ssh_config_path()
    alias = args.alias or safe_alias(args.host)

    upsert_ssh_host(path, alias, args.host, args.port, args.user, args.identity)

    print(f"已保存 SSH 配置到: {path}")
    print(f"Host 别名: {alias}")
    print(f"主机: {args.host}")
    print(f"端口: {args.port}")
    print(f"用户: {args.user}")
    print(f"身份文件: {args.identity}")


def cmd_list(args: argparse.Namespace) -> None:
    """列出所有 SSH Host。"""
    path = Path(args.ssh_config) if args.ssh_config else default_ssh_config_path()
    hosts = read_ssh_hosts(path)

    if not hosts:
        print(f"未找到 SSH 配置: {path}")
        return

    print(f"SSH 配置文件: {path}")
    print(f"找到 {len(hosts)} 个 Host:")
    print()
    for host in hosts:
        print(f"Host: {host.get('alias', 'unknown')}")
        if "hostname" in host:
            print(f"  HostName: {host['hostname']}")
        if "port" in host:
            print(f"  Port: {host['port']}")
        if "user" in host:
            print(f"  User: {host['user']}")
        if "identity_file" in host:
            print(f"  IdentityFile: {host['identity_file']}")
        print()


def cmd_check(args: argparse.Namespace) -> None:
    """检查 SSH 是否能连接远程；Windows 私钥权限过宽时自动修复后重试。"""
    path = Path(args.ssh_config) if args.ssh_config else default_ssh_config_path()
    host = find_ssh_host(path, args.alias)

    if not host:
        print(json.dumps({
            "connected": False,
            "error_type": "missing_ssh_host",
            "message": f"未找到 SSH Host 配置: {args.alias}",
            "next_action": "ask_user_resubmit_remote_info",
        }, ensure_ascii=False, indent=2))
        return

    attempts = 0
    permission_fix_attempted = False
    last_output = ""

    while attempts < args.max_attempts:
        attempts += 1
        try:
            result = run_ssh_probe(path, args.alias, args.connect_timeout)
        except FileNotFoundError:
            print(json.dumps({
                "connected": False,
                "attempts": attempts,
                "error_type": "ssh_not_found",
                "message": "未找到 ssh 命令，无法验证远程连接。",
                "next_action": "ask_user_resubmit_remote_info",
            }, ensure_ascii=False, indent=2))
            return
        except subprocess.TimeoutExpired as exc:
            last_output = str(exc)
            continue

        last_output = ((result.stdout or "") + (result.stderr or "")).strip()
        if result.returncode == 0:
            print(json.dumps({
                "connected": True,
                "attempts": attempts,
                "host_alias": args.alias,
                "message": "SSH 连接验证通过。",
            }, ensure_ascii=False, indent=2))
            return

        if (
            platform.system().lower() == "windows"
            and not permission_fix_attempted
            and is_bad_permission_error(last_output)
        ):
            identity = extract_bad_permission_path(last_output) or host.get("identity_file")
            if identity:
                fixed, fix_output = fix_windows_identity_permissions(identity)
                permission_fix_attempted = True
                if fixed:
                    continue
                last_output = f"{last_output}\n\nicacls 修复失败: {fix_output}"

    print(json.dumps({
        "connected": False,
        "attempts": attempts,
        "host_alias": args.alias,
        "error_type": "ssh_connection_failed",
        "message": "提供的信息无法连接上远程，请重新提交远程连接信息。",
        "last_error": last_output[-1200:],
        "next_action": "ask_user_resubmit_remote_info",
    }, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="管理 SSH 配置文件。")
    parser.add_argument("--ssh-config", help="SSH 配置文件路径(默认: ~/.ssh/config)")

    sub = parser.add_subparsers(dest="command", required=True)

    # add 命令
    p_add = sub.add_parser("add", help="添加或更新 SSH Host")
    p_add.add_argument("--alias", help="Host 别名(可选,默认自动生成)")
    p_add.add_argument("--host", required=True, help="主机名或 IP")
    p_add.add_argument("--port", type=int, default=22, help="端口(默认 22)")
    p_add.add_argument("--user", required=True, help="用户名")
    p_add.add_argument("--identity", required=True, help="身份文件路径")
    p_add.set_defaults(func=cmd_add)

    # list 命令
    p_list = sub.add_parser("list", help="列出所有 SSH Host")
    p_list.set_defaults(func=cmd_list)

    # check 命令
    p_check = sub.add_parser("check", help="验证 SSH 是否能连接远程")
    p_check.add_argument("--alias", required=True, help="要验证的 SSH Host 别名")
    p_check.add_argument("--max-attempts", type=int, default=3, help="最多尝试次数(默认 3)")
    p_check.add_argument("--connect-timeout", type=int, default=10, help="连接超时秒数(默认 10)")
    p_check.set_defaults(func=cmd_check)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
