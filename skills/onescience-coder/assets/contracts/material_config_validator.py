"""Validate generated OneScience MACE/UMA material model configs."""

from __future__ import annotations

import argparse
import sys

from material_config_common import (
    ConfigError,
    load_json_arg,
    raise_if_errors,
    validate_mace,
    validate_uma,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=["mace", "uma"], required=True)
    parser.add_argument("--task-type", required=True)
    parser.add_argument("--config-file")
    parser.add_argument("--config-json")
    parser.add_argument("--context-file")
    parser.add_argument("--context-json")
    parser.add_argument("--allow-foundation-arch-override", action="store_true")
    args = parser.parse_args()
    try:
        config = load_json_arg(args.config_file, args.config_json)
        context = {}
        if args.context_file or args.context_json:
            context = load_json_arg(args.context_file, args.context_json)
        if args.model == "mace":
            errors = validate_mace(
                config,
                context,
                args.task_type,
                allow_foundation_arch_override=args.allow_foundation_arch_override,
            )
        else:
            errors = validate_uma(config, context, args.task_type)
        raise_if_errors(errors)
        sys.stdout.write("Config is valid.\n")
        return 0
    except (ConfigError, ValueError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
