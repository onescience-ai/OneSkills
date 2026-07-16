#!/usr/bin/env python3
"""管理 SCnet 凭据文件 (~/.scnet-chat.env)。"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


SCNET_KEYS = ("SCNET_ACCESS_KEY", "SCNET_SECRET_KEY", "SCNET_USER", "SCNET_REGION")


def default_scnet_env_path() -> Path:
    """返回默认 SCnet 环境文件路径。"""
    return Path.home() / ".scnet-chat.env"


def parse_scnet_env(path: Path) -> dict[str, str]:
    """解析 SCnet 环境文件。"""
    result: dict[str, str] = {}
    if not path.exists():
        return result

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()

    return result


def write_scnet_env(path: Path, access_key: str, secret_key: str, user: str, region: str) -> None:
    """写入 SCnet 凭据到环境文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)

    # 读取现有内容
    existing = parse_scnet_env(path)

    # 更新关键字段
    existing["SCNET_ACCESS_KEY"] = access_key
    existing["SCNET_SECRET_KEY"] = secret_key
    existing["SCNET_USER"] = user
    existing["SCNET_REGION"] = region

    # 写入文件
    lines = [f"{k}={v}" for k, v in existing.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def escape_json(s: str) -> str:
    """按 SCnet 签名规则转义 JSON 字符串。"""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def generate_signature(access_key: str, timestamp: str, user: str, secret_key: str) -> str:
    """生成 SCnet HMAC-SHA256 签名。"""
    data_to_sign = (
        f'{{"accessKey":"{escape_json(access_key)}",'
        f'"timestamp":"{escape_json(timestamp)}",'
        f'"user":"{escape_json(user)}"}}'
    )
    return hmac.new(
        key=secret_key.encode("utf-8"),
        msg=data_to_sign.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest().lower()


def request_scnet_tokens(access_key: str, secret_key: str, user: str, timeout: int) -> dict[str, object]:
    """调用 SCnet token 接口验证凭据。"""
    timestamp = str(int(time.time()))
    signature = generate_signature(access_key, timestamp, user, secret_key)
    request = urllib.request.Request(
        "https://api.scnet.cn/api/user/v3/tokens",
        method="POST",
        headers={
            "user": user,
            "accessKey": access_key,
            "signature": signature,
            "timestamp": timestamp,
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
    return json.loads(body)


def cmd_set(args: argparse.Namespace) -> None:
    """设置 SCnet 凭据。"""
    path = Path(args.scnet_env) if args.scnet_env else default_scnet_env_path()

    write_scnet_env(path, args.access_key, args.secret_key, args.user, args.region)

    print(f"已保存 SCnet 凭据到: {path}")
    print(f"用户: {args.user}")
    print(f"区域: {args.region}")
    print("ACCESS_KEY 和 SECRET_KEY 已保存(不显示明文)")


def cmd_show(args: argparse.Namespace) -> None:
    """显示 SCnet 配置状态(不显示密钥明文)。"""
    path = Path(args.scnet_env) if args.scnet_env else default_scnet_env_path()

    if not path.exists():
        print(f"SCnet 配置文件不存在: {path}")
        return

    env = parse_scnet_env(path)

    print(f"SCnet 配置文件: {path}")
    print(f"配置状态:")
    for key in SCNET_KEYS:
        status = "已设置" if env.get(key) else "未设置"
        if key in {"SCNET_USER", "SCNET_REGION"} and env.get(key):
            print(f"  {key}: {env[key]}")
        else:
            print(f"  {key}: {status}")


def cmd_check_login(args: argparse.Namespace) -> None:
    """尝试获取 SCnet token，验证凭据是否可登录。"""
    path = Path(args.scnet_env) if args.scnet_env else default_scnet_env_path()
    env = parse_scnet_env(path)
    access_key = args.access_key or env.get("SCNET_ACCESS_KEY", "")
    secret_key = args.secret_key or env.get("SCNET_SECRET_KEY", "")
    user = args.user or env.get("SCNET_USER", "")
    region = env.get("SCNET_REGION", "")

    missing = [
        key
        for key, value in [
            ("SCNET_ACCESS_KEY", access_key),
            ("SCNET_SECRET_KEY", secret_key),
            ("SCNET_USER", user),
        ]
        if not value
    ]
    if missing:
        print(json.dumps({
            "connected": False,
            "error_type": "missing_scnet_credentials",
            "missing": missing,
            "message": "SCnet 凭据不完整，请重新提交远程连接信息。",
            "next_action": "ask_user_resubmit_remote_info",
        }, ensure_ascii=False, indent=2))
        return

    try:
        result = request_scnet_tokens(access_key, secret_key, user, args.timeout)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        print(json.dumps({
            "connected": False,
            "error_type": "scnet_login_failed",
            "scnet_user": user,
            "scnet_region": region or None,
            "message": "提供的信息无法连接上远程，请重新提交远程连接信息。",
            "last_error": str(exc),
            "next_action": "ask_user_resubmit_remote_info",
        }, ensure_ascii=False, indent=2))
        return

    code = str(result.get("code", ""))
    data = result.get("data")
    if code == "0" and data:
        print(json.dumps({
            "connected": True,
            "scnet_user": user,
            "scnet_region": region or None,
            "token_count": len(data) if isinstance(data, list) else None,
            "message": "SCnet 登录验证通过。",
        }, ensure_ascii=False, indent=2))
        return

    print(json.dumps({
        "connected": False,
        "error_type": "scnet_login_rejected",
        "scnet_user": user,
        "scnet_region": region or None,
        "message": "提供的信息无法连接上远程，请重新提交远程连接信息。",
        "scnet_message": result.get("message") or result.get("error"),
        "next_action": "ask_user_resubmit_remote_info",
    }, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="管理 SCnet 凭据文件。")
    parser.add_argument("--scnet-env", help="SCnet 环境文件路径(默认: ~/.scnet-chat.env)")

    sub = parser.add_subparsers(dest="command", required=True)

    # set 命令
    p_set = sub.add_parser("set", help="设置 SCnet 凭据")
    p_set.add_argument("--access-key", required=True, help="SCNET_ACCESS_KEY")
    p_set.add_argument("--secret-key", required=True, help="SCNET_SECRET_KEY")
    p_set.add_argument("--user", required=True, help="SCNET_USER")
    p_set.add_argument("--region", required=True, help="SCnet region")
    p_set.set_defaults(func=cmd_set)

    # show 命令
    p_show = sub.add_parser("show", help="显示配置状态(不显示密钥)")
    p_show.set_defaults(func=cmd_show)

    # check-login 命令
    p_check = sub.add_parser("check-login", help="验证 SCnet 凭据是否能登录")
    p_check.add_argument("--access-key", help="SCNET_ACCESS_KEY；未提供时读取配置文件")
    p_check.add_argument("--secret-key", help="SCNET_SECRET_KEY；未提供时读取配置文件")
    p_check.add_argument("--user", help="SCNET_USER；未提供时读取配置文件")
    p_check.add_argument("--timeout", type=int, default=30, help="登录请求超时秒数(默认 30)")
    p_check.set_defaults(func=cmd_check_login)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
