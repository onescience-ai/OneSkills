"""Validate and optionally submit a Gitee Issue payload.

Two submission backends are supported:

1. gitee-cli (preferred): the official ``@gitee/gitee-cli`` tool.  The user
   authenticates once with ``gitee auth login``; no token needs to be passed
   per invocation.  This matches the org-wide dcu-feedback workflow.
2. HTTP API (fallback): direct ``POST /api/v5/repos/{owner}/issues`` call that
   reads a token from the ``GITEE_TOKEN`` / ``GITEE_ACCESS_TOKEN`` env var.

The ``--method`` flag selects the backend (``auto`` tries gitee-cli first and
falls back to the HTTP API).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


def load_payload(path: Path) -> dict:
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


def submit(payload: dict, repo: str, api_base: str, token: str) -> dict:
    """Create a Gitee Issue via POST /repos/{owner}/issues.

    NOTE: Gitee's create-issue endpoint does NOT include {repo} in the path.
    The repo name is passed as a body parameter.  Using the intuitive but
    wrong path /repos/{owner}/{repo}/issues returns 404.
    """
    owner, name = repo.split("/", 1)
    endpoint = f"{api_base.rstrip('/')}/repos/{quote(owner)}/issues"
    body = {
        "access_token": token,
        "repo": name,
        "title": payload["title"],
        "body": payload["body"],
    }
    if payload.get("labels"):
        body["labels"] = ",".join(str(label) for label in payload["labels"])
    for key in ("milestone", "assignee", "collaborators"):
        if payload.get(key) is not None:
            body[key] = payload[key]
    request = Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        raw = response.read().decode("utf-8")
        return {"status": response.status, "response": json.loads(raw) if raw else {}}


def find_gitee_cli() -> str | None:
    """Resolve the full path of the gitee-cli executable, or None if absent.

    On Windows the command is a ``.CMD`` shim that ``subprocess`` cannot run by
    bare name, so we always resolve the absolute path via ``shutil.which``.
    """
    return shutil.which("gitee")


def gitee_cli_argv() -> list[str] | None:
    """Return the argv prefix used to invoke gitee-cli, or None if absent.

    On Windows ``shutil.which("gitee")`` resolves to the npm ``gitee.cmd``
    batch shim, which runs ``node <pkg>/bin/index.js %*``.  A batch shim
    CANNOT forward arguments containing newlines: cmd.exe splits the command
    line at the first LF, so a multi-line ``-b <body>`` is truncated to its
    first line and every flag placed after it (``--json``, ``--labels``) is
    silently dropped.  That is why issues created through the shim came out
    with a one-line body, no labels and no machine-readable number.

    To avoid this we bypass the shim and call ``node`` directly on the CLI
    entrypoint; node's argv parsing preserves embedded newlines intact.  On
    non-Windows platforms the ``gitee`` shell wrapper handles multi-line
    arguments fine, so it is used as-is.
    """
    gitee = find_gitee_cli()
    if gitee is None:
        return None
    if os.name == "nt" and gitee.lower().endswith((".cmd", ".bat")):
        node = shutil.which("node")
        index_js = (
            Path(gitee).parent
            / "node_modules" / "@gitee" / "gitee-cli" / "bin" / "index.js"
        )
        if node and index_js.exists():
            return [node, str(index_js)]
    return [gitee]


def gitee_cli_ready() -> bool:
    """Return True if gitee-cli is installed AND authenticated.

    Authentication is set up once via ``gitee auth login``; the token is stored
    in the CLI's local config, so no env var is needed at call time.
    """
    argv = gitee_cli_argv()
    if argv is None:
        return False
    try:
        result = subprocess.run(
            argv + ["--no-tui", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=15,
            encoding="utf-8",
            errors="replace",
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, OSError):
        return False


def _parse_cli_text(raw: str) -> dict:
    """Parse gitee-cli's plain-text success line into a response dict.

    gitee-cli drops ``--json`` when the issue body contains newlines and
    instead prints a single line like::

        Created issue #IKHC3U: https://gitee.com/<owner>/<repo>/issues/IKHC3U

    Extract the number and URL so callers get the same shape as the JSON path.
    """
    match = re.search(r"#([A-Za-z0-9]+):\s*(https?://\S+)", raw)
    if match:
        return {"number": match.group(1), "html_url": match.group(2)}
    return {"raw": raw}


def submit_via_cli(payload: dict, repo: str) -> dict:
    """Create a Gitee Issue via gitee-cli.

    Effective command (argv form, see gitee_cli_argv for the node-direct
    invocation used on Windows)::

        gitee --no-tui issue create -R <repo> -t <title> --json \
            [--labels <l1,l2>] -b <body> [-a <assignee>]

    Auth is handled by the CLI's stored credentials (see `gitee auth login`).
    """
    argv = gitee_cli_argv()
    if argv is None:
        raise RuntimeError("gitee-cli not found in PATH")
    # NOTE: ``--json`` and ``--labels`` are placed BEFORE ``-b <body>`` so that
    # they survive even on a platform whose shell wrapper still truncates a
    # multi-line body argument.  With the node-direct argv (see gitee_cli_argv)
    # the full body is preserved regardless of ordering.
    cmd = argv + [
        "--no-tui", "issue", "create",
        "-R", repo,
        "-t", payload["title"],
        "--json",
    ]
    if payload.get("labels"):
        cmd += ["--labels", ",".join(str(label) for label in payload["labels"])]
    cmd += ["-b", payload["body"]]
    if payload.get("assignee"):
        cmd += ["-a", str(payload["assignee"])]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(detail or "gitee-cli exited with non-zero status")
    raw = (result.stdout or "").strip()
    try:
        response = json.loads(raw) if raw else {}
        if not isinstance(response, dict):
            response = {"raw": raw}
    except json.JSONDecodeError:
        # Multi-line body makes gitee-cli ignore --json and print plain text.
        response = _parse_cli_text(raw)
    return {"status": 201, "response": response}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", required=True, type=Path)
    parser.add_argument("--repo", default="onescience-ai/oneskills")
    parser.add_argument("--api-base", default="https://gitee.com/api/v5")
    parser.add_argument("--submit", action="store_true", help="perform the network request")
    parser.add_argument(
        "--method",
        choices=["auto", "cli", "api"],
        default="auto",
        help="auto: prefer gitee-cli, fall back to HTTP API (default); "
             "cli: force gitee-cli (needs `gitee auth login`); "
             "api: force HTTP API (needs GITEE_TOKEN env var)",
    )
    args = parser.parse_args()

    try:
        payload = load_payload(args.payload)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"PAYLOAD: {args.payload}")
    print(f"REPOSITORY: {args.repo}")
    print(f"TITLE: {payload['title']}")
    print(f"LABELS: {', '.join(map(str, payload.get('labels', [])))}")
    print(f"METHOD: {args.method}")
    if not args.submit:
        print("DRY-RUN: no network request made; pass --submit to create the Issue")
        return 0

    # Decide which backend to use.
    use_cli = False
    if args.method in ("auto", "cli"):
        if gitee_cli_ready():
            use_cli = True
        elif args.method == "cli":
            print("ERROR: --method cli requested but gitee-cli is not installed "
                  "or not authenticated. Run `gitee auth login` first.")
            return 2

    if use_cli:
        print("BACKEND: gitee-cli (authenticated via `gitee auth login`)")
        try:
            result = submit_via_cli(payload, args.repo)
        except (subprocess.SubprocessError, RuntimeError, OSError) as exc:
            print(f"ERROR: gitee-cli submission failed: {exc}")
            return 1
    else:
        token = os.environ.get("GITEE_TOKEN") or os.environ.get("GITEE_ACCESS_TOKEN")
        if not token:
            print("ERROR: no authenticated gitee-cli and no GITEE_TOKEN env var.\n"
                  "  Option A (recommended): run `gitee auth login` once.\n"
                  "  Option B: set GITEE_TOKEN / GITEE_ACCESS_TOKEN env var.")
            return 2
        print("BACKEND: HTTP API (GITEE_TOKEN)")
        try:
            result = submit(payload, args.repo, args.api_base, token)
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            print(f"ERROR: Gitee returned HTTP {exc.code}: {detail}")
            return 1
        except URLError as exc:
            print(f"ERROR: network request failed: {exc.reason}")
            return 1
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"ERROR: invalid Gitee response: {exc}")
            return 1

    response = result.get("response", {})
    print(f"SUBMITTED: HTTP {result.get('status')}")
    if response.get("number") is not None:
        print(f"ISSUE_NUMBER: {response['number']}")
    if response.get("html_url"):
        print(f"ISSUE_URL: {response['html_url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
