#!/usr/bin/env python3
"""Validate variable counts and channel totals for paper2code specs.

Input is a JSON file with a minimal schema:

{
  "groups": [
    {
      "name": "pressure",
      "variables": ["z", "u", "v", "w", "q", "t"],
      "levels": 13,
      "time_steps": 1,
      "declared_variable_count": 6,
      "declared_channels": 78
    },
    {
      "name": "lat_lon",
      "items": [{"name": "lat_lon", "scalar_channels": 2}],
      "declared_channels": 2
    }
  ],
  "totals": [
    {"name": "input_dynamic", "groups": ["pressure", "surface"], "time_steps": 2, "declared_channels": 172}
  ]
}

Use "variables" for one-channel scalar variables. Use "items" when an item
expands into multiple scalar channels, such as lat/lon -> 2 channels.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _as_number(value: Any, default: int = 1) -> int:
    if value is None:
        return default
    if not isinstance(value, int):
        raise TypeError(f"expected integer, got {value!r}")
    return value


def _group_items(group: dict[str, Any]) -> list[dict[str, Any]]:
    if "items" in group:
        return list(group["items"])
    return [{"name": name, "scalar_channels": 1} for name in group.get("variables", [])]


def audit(payload: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    group_channels: dict[str, int] = {}

    for group in payload.get("groups", []):
        name = str(group.get("name", "<unnamed>"))
        items = _group_items(group)
        levels = _as_number(group.get("levels"), 1)
        time_steps = _as_number(group.get("time_steps"), 1)
        variable_count = len(items)
        base_channels = 0

        for item in items:
            scalar_channels = _as_number(item.get("scalar_channels"), 1)
            base_channels += scalar_channels

        computed_channels = base_channels * levels * time_steps
        group_channels[name] = computed_channels

        declared_count = group.get("declared_variable_count")
        if declared_count is not None and declared_count != variable_count:
            issues.append(
                f"{name}: declared_variable_count={declared_count}, "
                f"but listed variables/items={variable_count}"
            )

        declared_base = group.get("declared_base_channels")
        if declared_base is not None and declared_base != base_channels:
            issues.append(
                f"{name}: declared_base_channels={declared_base}, "
                f"but item scalar channels sum to {base_channels}"
            )

        declared_channels = group.get("declared_channels")
        if declared_channels is not None and declared_channels != computed_channels:
            issues.append(
                f"{name}: declared_channels={declared_channels}, "
                f"but computed {base_channels} * levels {levels} * "
                f"time_steps {time_steps} = {computed_channels}"
            )

    for total in payload.get("totals", []):
        name = str(total.get("name", "<unnamed-total>"))
        groups = list(total.get("groups", []))
        missing = [group for group in groups if group not in group_channels]
        if missing:
            issues.append(f"{name}: unknown groups in total: {', '.join(missing)}")
            continue

        time_steps = _as_number(total.get("time_steps"), 1)
        computed = sum(group_channels[group] for group in groups) * time_steps
        extra_channels = _as_number(total.get("extra_channels"), 0)
        computed += extra_channels

        declared_channels = total.get("declared_channels")
        if declared_channels is not None and declared_channels != computed:
            issues.append(
                f"{name}: declared_channels={declared_channels}, "
                f"but computed sum({groups}) * time_steps {time_steps} "
                f"+ extra_channels {extra_channels} = {computed}"
            )

    return issues


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: variable_channel_audit.py <ledger.json>", file=sys.stderr)
        return 2

    payload = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    issues = audit(payload)
    if issues:
        for issue in issues:
            print(f"ERROR: {issue}")
        return 1

    print("OK: variable counts and channel totals are consistent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
