"""Probe and invoke the host Agent's `dataset_report` tool.

Implements the four-path probe strategy defined in
references/dataset_report_probe.md:

    1. host tool manifest (via ONESCIENCE_HOST_TOOLS_JSON env var)
    2. HTTP endpoint (ONESCIENCE_DATASET_REPORT_ENDPOINT)
    3. CLI executable (`onescience-dataset-report` on PATH)
    4. Python module (`onescience.report.dataset_report`)

Failure to probe or invoke never blocks the main standardization flow; the
result is surfaced via the returned dict and written into execution_result.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

TOOL_NAME = "dataset_report"
CALL_TIMEOUT_SECONDS = 30


class ProbeResult:
    def __init__(self, available: bool, method: str,
                 details: Optional[Dict[str, Any]] = None) -> None:
        self.available = available
        self.method = method  # host_tool | env_endpoint | cli | python_module | none
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "probe_method": self.method,
            **self.details,
        }


# ----------------------------------------------------------------------
# Probe paths
# ----------------------------------------------------------------------

def _probe_host_tool() -> Optional[ProbeResult]:
    """Path 1: inspect the host Agent's tool manifest.

    Hosts that wish to expose their tool list should set
    ONESCIENCE_HOST_TOOLS_JSON to either:
      - a JSON array of tool descriptors, or
      - a path to a JSON file containing such an array.

    Each descriptor is expected to carry a `name` field.
    """
    raw = os.environ.get("ONESCIENCE_HOST_TOOLS_JSON")
    if not raw:
        return None
    tools: List[Dict[str, Any]] = []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            tools = parsed
        elif isinstance(parsed, str):
            path = Path(parsed).expanduser()
            if path.exists():
                tools = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        # Try treating the value as a bare path.
        path = Path(raw).expanduser()
        if path.exists():
            try:
                tools = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return None
        else:
            return None
    if not isinstance(tools, list):
        return None
    for tool in tools:
        if isinstance(tool, dict) and tool.get("name") == TOOL_NAME:
            return ProbeResult(True, "host_tool",
                               details={"tool_descriptor": tool})
        if isinstance(tool, str) and tool == TOOL_NAME:
            return ProbeResult(True, "host_tool",
                               details={"tool_descriptor": {"name": TOOL_NAME}})
    return None


def _probe_env_endpoint() -> Optional[ProbeResult]:
    endpoint = os.environ.get("ONESCIENCE_DATASET_REPORT_ENDPOINT")
    if not endpoint:
        return None
    insecure = endpoint.startswith("http://")
    return ProbeResult(True, "env_endpoint",
                       details={"endpoint": endpoint, "insecure_transport": insecure})


def _probe_cli() -> Optional[ProbeResult]:
    exe = shutil.which("onescience-dataset-report")
    if not exe:
        return None
    return ProbeResult(True, "cli", details={"executable": exe})


def _probe_python_module() -> Optional[ProbeResult]:
    try:
        from onescience.report.dataset_report import report  # type: ignore
    except Exception:
        return None
    if not callable(report):
        return None
    return ProbeResult(True, "python_module",
                       details={"module": "onescience.report.dataset_report"})


def probe() -> ProbeResult:
    for fn in (_probe_host_tool, _probe_env_endpoint,
               _probe_cli, _probe_python_module):
        result = fn()
        if result is not None:
            return result
    return ProbeResult(False, "none")


# ----------------------------------------------------------------------
# Invocation
# ----------------------------------------------------------------------

def _invoke_env_endpoint(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        import requests  # type: ignore
    except ImportError as exc:
        return {"ok": False, "error": f"requests not installed: {exc}"}
    token = os.environ.get("ONESCIENCE_API_TOKEN", "")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        resp = requests.post(endpoint, json=payload, headers=headers,
                             timeout=CALL_TIMEOUT_SECONDS)
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    ok = 200 <= resp.status_code < 300
    body_preview = (resp.text or "")[:512]
    return {"ok": ok, "status_code": resp.status_code, "body_preview": body_preview}


def _invoke_cli(executable: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    cmd = [
        executable,
        "--name", str(payload["name"]),
        "--target-dir", str(payload["target_dir"]),
        "--source-dir", str(payload.get("source_dir", "")),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=CALL_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout"}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "")[:512],
        "stderr": (proc.stderr or "")[:512],
    }


def _invoke_python_module(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from onescience.report.dataset_report import report  # type: ignore
    except Exception as exc:
        return {"ok": False, "error": f"import failed: {exc}"}
    try:
        result = report(
            name=payload["name"],
            target_dir=payload["target_dir"],
            source_dir=payload.get("source_dir"),
        )
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return {"ok": True, "result": repr(result)[:512]}


def _invoke_host_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Host-tool invocation is indirect: we cannot call the tool ourselves.

    Return a marker instructing the caller (orchestrator / host Agent) to
    dispatch the tool with the given payload.
    """
    return {
        "ok": True,
        "deferred": True,
        "instruction": "host Agent should invoke dataset_report with payload",
    }


def call(payload: Dict[str, Any], probe_result: Optional[ProbeResult] = None
         ) -> Dict[str, Any]:
    """Invoke dataset_report using the first available path.

    Always returns a dict with keys: available / probe_method / called /
    payload / response / error. Never raises.
    """
    probe_result = probe_result or probe()
    out: Dict[str, Any] = {
        "available": probe_result.available,
        "probe_method": probe_result.method,
        "called": False,
        "payload": payload,
        "response": None,
        "error": None,
    }
    if not probe_result.available:
        return out

    method = probe_result.method
    details = probe_result.details
    if method == "host_tool":
        resp = _invoke_host_tool(payload)
    elif method == "env_endpoint":
        resp = _invoke_env_endpoint(details["endpoint"], payload)
    elif method == "cli":
        resp = _invoke_cli(details["executable"], payload)
    elif method == "python_module":
        resp = _invoke_python_module(payload)
    else:
        resp = {"ok": False, "error": f"unknown probe method: {method}"}

    out["called"] = bool(resp.get("ok"))
    out["response"] = resp
    if not resp.get("ok"):
        out["error"] = resp.get("error", "unknown error")
    if details.get("insecure_transport"):
        out["insecure_transport"] = True
    return out


def build_payload(name: str, target_dir: str,
                  source_dir: Optional[str] = None) -> Dict[str, Any]:
    """Construct the canonical three-field payload."""
    payload: Dict[str, Any] = {"name": name, "target_dir": str(target_dir)}
    if source_dir:
        payload["source_dir"] = str(source_dir)
    return payload


# ----------------------------------------------------------------------
# CLI (for manual probing / debugging)
# ----------------------------------------------------------------------

def _cli(argv: Optional[List[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Probe / call dataset_report")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe", help="Print probe result as JSON")

    p_call = sub.add_parser("call", help="Probe then call with payload")
    p_call.add_argument("--name", required=True)
    p_call.add_argument("--target-dir", required=True)
    p_call.add_argument("--source-dir", default=None)

    args = parser.parse_args(argv)
    if args.cmd == "probe":
        print(json.dumps(probe().to_dict(), indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "call":
        payload = build_payload(args.name, args.target_dir, args.source_dir)
        result = call(payload)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["called"] else 1
    return 2


if __name__ == "__main__":
    sys.exit(_cli())
