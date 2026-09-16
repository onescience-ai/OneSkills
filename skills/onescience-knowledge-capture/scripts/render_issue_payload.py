"""Render an issue_payload.json into a human-readable Gitee submission card.

本脚本不发起任何网络请求，只把机器用的 issue_payload.json 转成
领域同事可以直接复制粘贴到 Gitee 网页端的提交卡片（标题 / 标签 / 正文），
并把卡片落盘为 submission_card.md，作为人工提 Issue 的持久凭据。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_payload(path: Path) -> dict:
    # 用 utf-8-sig 读，兼容 Windows PowerShell 写出的带 BOM 文件
    with path.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    for key in ("title", "body"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            raise ValueError(f"payload.{key} must be a non-empty string")
    if not isinstance(payload.get("labels", []), list):
        raise ValueError("payload.labels must be a list")
    return payload


def render(payload: dict, repo: str) -> str:
    labels = ", ".join(str(item) for item in payload.get("labels", [])) or "（无）"
    lines = [
        "<!-- 由 render_issue_payload.py 生成，用于 Gitee 网页端人工提交 Issue -->",
        f"<!-- 目标仓库：{repo} -->",
        "",
        "# 提交卡片（复制以下内容到 Gitee 网页）",
        "",
        "## ① 标题（Title）",
        "",
        "```text",
        payload["title"].strip(),
        "```",
        "",
        "## ② 标签（Labels，逐个添加）",
        "",
    ]
    if payload.get("labels"):
        for label in payload["labels"]:
            lines.append(f"- `{label}`")
    else:
        lines.append("- （本贡献无标签）")
    lines += [
        "",
        "## ③ 正文（Body，整段复制）",
        "",
        "---",
        payload["body"].rstrip(),
        "---",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", required=True, type=Path,
                        help="issue_payload.json 路径")
    parser.add_argument("--repo", default="onescience-ai/oneskills-dev",
                        help="目标仓库 owner/name，仅用于渲染提示，不发起请求")
    parser.add_argument("--out", type=Path, default=None,
                        help="输出提交卡片路径；默认写到 payload 同目录的 submission_card.md")
    parser.add_argument("--stdout", action="store_true",
                        help="同时把提交卡片打印到终端")
    args = parser.parse_args()

    try:
        payload = load_payload(args.payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    card = render(payload, args.repo)
    out = args.out or (args.payload.parent / "submission_card.md")
    try:
        out.write_text(card, encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: 无法写入 {out}: {exc}")
        return 1

    print(f"WROTE: {out}")
    print(f"REPO : {args.repo}")
    print(f"TITLE: {payload['title']}")
    print(f"LABELS: {', '.join(map(str, payload.get('labels', []))) or '(none)'}")
    if args.stdout:
        print("\n----- SUBMISSION CARD -----\n")
        print(card)
    print("下一步：按随包携带的操作指南（manual_issue_submission.md / 操作指南.md）在 Gitee 网页端创建 Issue。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
