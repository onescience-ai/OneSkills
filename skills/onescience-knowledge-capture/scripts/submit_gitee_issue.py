"""Validate and optionally submit a Gitee Issue payload."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


def load_payload(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
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
    owner, name = repo.split("/", 1)
    endpoint = f"{api_base.rstrip('/')}/repos/{quote(owner)}/{quote(name)}/issues"
    body = {"title": payload["title"], "body": payload["body"]}
    if payload.get("labels"):
        body["labels"] = ",".join(str(label) for label in payload["labels"])
    for key in ("milestone", "assignee", "collaborators"):
        if payload.get(key) is not None:
            body[key] = payload[key]
    query = urlencode({"access_token": token})
    request = Request(
        f"{endpoint}?{query}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        raw = response.read().decode("utf-8")
        return {"status": response.status, "response": json.loads(raw) if raw else {}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", required=True, type=Path)
    parser.add_argument("--repo", default="onescience-ai/oneskills-dev")
    parser.add_argument("--api-base", default="https://gitee.com/api/v5")
    parser.add_argument("--submit", action="store_true", help="perform the network request")
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
    if not args.submit:
        print("DRY-RUN: no network request made; pass --submit to create the Issue")
        return 0

    token = os.environ.get("GITEE_TOKEN") or os.environ.get("GITEE_ACCESS_TOKEN")
    if not token:
        print("ERROR: set GITEE_TOKEN or GITEE_ACCESS_TOKEN before using --submit")
        return 2
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
