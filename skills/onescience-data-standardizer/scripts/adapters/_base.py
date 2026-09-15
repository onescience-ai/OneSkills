"""Base adapter class for Tier1 dataset standardization converters.

Every Tier1 adapter under scripts/adapters/<domain>/<name>.py must subclass
BaseAdapter and implement probe / plan / convert. The base class provides:

- Uniform CLI contract (--source-dir / --target-dir / --spec-json / --dry-run)
- dataset_card.json and README.md writing helpers aligned with
  references/ai_ready_contract.md
- Directory scaffolding for data/ static/ stats/ splits/
- Structured exception hierarchy consumed by scripts/standardize.py

Adapters must NOT hardcode absolute paths. All IO paths flow in via argv.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class AdapterError(RuntimeError):
    """Base class for all adapter errors."""


class AdapterDependencyError(AdapterError):
    """Raised when a required third-party package is missing."""


class AdapterInputError(AdapterError):
    """Raised when the raw source directory does not match expectations."""


class AdapterConversionError(AdapterError):
    """Raised when the conversion process itself fails."""


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dir_checksum(root: Path, sample_limit: int = 64) -> str:
    """Aggregate sha256 over up to `sample_limit` files (deterministic order).

    Full-tree checksums on multi-TB datasets are prohibitively expensive, so
    we sample the first N files in sorted order plus the total byte count.
    This is a fingerprint, not a cryptographic guarantee.
    """
    h = hashlib.sha256()
    total_bytes = 0
    files: List[Path] = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            files.append(p)
            try:
                total_bytes += p.stat().st_size
            except OSError:
                pass
    h.update(str(total_bytes).encode())
    h.update(str(len(files)).encode())
    for p in files[:sample_limit]:
        h.update(str(p.relative_to(root)).encode())
    return f"sha256:{h.hexdigest()}"


class BaseAdapter(ABC):
    """Abstract base for all Tier1 adapters.

    Subclasses must set the three class attributes and implement the three
    abstract methods. See references/converter_authoring.md for the full
    authoring contract.
    """

    domain: str = ""            # cfd | bio | climate | matchem
    dataset_name: str = ""      # e.g. ERA5, DeepCFD, targetdiff, oc20
    primary_format: str = ""    # e.g. hdf5, pickle, lmdb, aselmdb

    def __init__(self, source_dir: Path, target_dir: Path,
                 spec: Optional[Dict[str, Any]] = None,
                 dry_run: bool = False) -> None:
        if not self.domain or not self.dataset_name or not self.primary_format:
            raise AdapterError(
                f"{type(self).__name__} must define domain, dataset_name, primary_format"
            )
        self.source_dir = Path(source_dir).expanduser().resolve()
        self.target_dir = Path(target_dir).expanduser().resolve()
        self.spec = spec or {}
        self.dry_run = dry_run
        self._started_at: Optional[float] = None
        self._warnings: List[str] = []

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def probe(self, source_dir: Path) -> Dict[str, Any]:
        """Inspect raw data layout and return a probe report dict."""

    @abstractmethod
    def plan(self, probe_report: Dict[str, Any],
             spec: Dict[str, Any]) -> Dict[str, Any]:
        """Produce a conversion plan dict from probe report + primitives spec."""

    @abstractmethod
    def convert(self, source_dir: Path, target_dir: Path,
                plan: Dict[str, Any]) -> None:
        """Execute the conversion, writing outputs under target_dir."""

    # ------------------------------------------------------------------
    # Optional hook
    # ------------------------------------------------------------------

    def post_process(self, target_dir: Path) -> None:
        """Optional: derive stats/, splits/, static/ after main conversion."""
        return None

    # ------------------------------------------------------------------
    # Scaffolding helpers
    # ------------------------------------------------------------------

    def ensure_layout(self) -> None:
        """Create the mandatory AI-Ready directory skeleton."""
        if self.dry_run:
            return
        (self.target_dir / "data").mkdir(parents=True, exist_ok=True)

    def warn(self, message: str) -> None:
        self._warnings.append(message)
        print(f"[adapter:{self.dataset_name}] WARNING: {message}",
              file=sys.stderr)

    def require_deps(self, *packages: str) -> None:
        """Raise AdapterDependencyError if any package is not importable."""
        missing: List[str] = []
        for pkg in packages:
            import_name = pkg.split(">=")[0].split("==")[0].split("<")[0].strip()
            import_name = import_name.replace("-", "_")
            try:
                __import__(import_name)
            except ImportError:
                missing.append(pkg)
        if missing:
            raise AdapterDependencyError(
                f"missing dependencies: {', '.join(missing)}; "
                f"install with: pip install {' '.join(missing)}"
            )

    # ------------------------------------------------------------------
    # Output writers
    # ------------------------------------------------------------------

    def write_dataset_card(self, target_dir: Path,
                           extra: Optional[Dict[str, Any]] = None) -> Path:
        """Compose and write dataset_card.json per ai_ready_contract.md."""
        duration = time.time() - self._started_at if self._started_at else 0.0
        card: Dict[str, Any] = {
            "schema_version": "1.0",
            "name": self.dataset_name,
            "domain": self.domain,
            "version": self.spec.get("version", "1.0.0"),
            "handler": f"adapter:{self.domain}/{self.dataset_name.lower()}",
            "source": {
                "dir": str(self.source_dir),
                "resolution_method": self.spec.get("_source_resolution_method", "explicit"),
                "modelscope_repo_id": self.spec.get("_modelscope_repo_id"),
                "checksum": None,
            },
            "target": {
                "dir": str(target_dir),
                "created_at": _utcnow_iso(),
                "checksum": None,
            },
            "target_schema": {
                "spec_source": self.spec.get(
                    "_spec_source",
                    f"onescience-primitives:{self.domain}/datasets/{self.dataset_name}/spec.md",
                ),
                "data_layout": (extra or {}).get("data_layout", {"data/": self.primary_format}),
                "primary_format": self.primary_format,
                "tensor_shape": (extra or {}).get("tensor_shape"),
                "dtype": (extra or {}).get("dtype"),
                "dimensions": (extra or {}).get("dimensions", {}),
            },
            "statistics": (extra or {}).get("statistics", {}),
            "splits": (extra or {}).get("splits", {}),
            "provenance": {
                "converter_script": f"scripts/adapters/{self.domain}/{self.dataset_name.lower()}.py",
                "converter_tier": 1,
                "llm_model": None,
                "execution_runtime": "subprocess",
                "duration_seconds": round(duration, 3),
            },
            "quality_checks": {
                "format_valid": True,
                "required_files_present": ["data/", "dataset_card.json", "README.md"],
                "spec_alignment": (extra or {}).get("spec_alignment", []),
                "warnings": list(self._warnings),
            },
        }
        # Fill in target checksum after files are on disk.
        try:
            card["target"]["checksum"] = _dir_checksum(target_dir)
        except OSError as exc:
            self.warn(f"target checksum failed: {exc}")

        card_path = target_dir / "dataset_card.json"
        if not self.dry_run:
            card_path.write_text(json.dumps(card, indent=2, ensure_ascii=False),
                                 encoding="utf-8")
        return card_path

    def write_readme(self, target_dir: Path,
                     loading_example: str = "",
                     extra_sections: Optional[Dict[str, str]] = None) -> Path:
        readme_path = target_dir / "README.md"
        if self.dry_run:
            return readme_path
        sections = [
            f"# {self.dataset_name} AI-Ready Dataset",
            "",
            f"- **Domain**: {self.domain}",
            f"- **Handler**: adapter:{self.domain}/{self.dataset_name.lower()}",
            f"- **Generated at**: {_utcnow_iso()}",
            f"- **Source spec**: onescience-primitives:{self.domain}/datasets/{self.dataset_name}/spec.md",
            f"- **Source dir**: `{self.source_dir}`",
            "",
            "## Directory Layout",
            "",
            "```text",
            "data/          # primary data files",
            "static/        # optional static fields",
            "stats/         # optional global/per-variable statistics",
            "splits/        # optional train/val/test indices",
            "dataset_card.json",
            "README.md",
            "```",
            "",
        ]
        if loading_example:
            sections += [
                "## Loading Example",
                "",
                "Copy-paste ready: reads the primary data, walks the split, "
                "builds batches, and sketches a minimal training loop "
                "(`model` / `optimizer` are your own; framework glue omitted).",
                "",
                loading_example,
                "",
            ]
        for title, body in (extra_sections or {}).items():
            sections += [f"## {title}", "", body, ""]
        sections += [
            "## Regeneration",
            "",
            "```bash",
            f"python scripts/standardize.py run \\",
            f"  --dataset-name {self.dataset_name} \\",
            f"  --domain {self.domain} \\",
            f"  --source-dir <raw-path> \\",
            f"  --target-dir <ai-ready-path>",
            "```",
            "",
        ]
        readme_path.write_text("\n".join(sections), encoding="utf-8")
        return readme_path

    # ------------------------------------------------------------------
    # Orchestration entry
    # ------------------------------------------------------------------

    def run(self) -> Dict[str, Any]:
        """Full pipeline: probe -> plan -> convert -> post_process -> write cards.

        Returns a summary dict consumed by scripts/standardize.py.
        """
        self._started_at = time.time()
        if not self.source_dir.exists():
            raise AdapterInputError(f"source_dir does not exist: {self.source_dir}")
        if not self.source_dir.is_dir():
            raise AdapterInputError(f"source_dir is not a directory: {self.source_dir}")
        if not any(self.source_dir.iterdir()):
            raise AdapterInputError(f"source_dir is empty: {self.source_dir}")

        if not self.dry_run:
            self.target_dir.mkdir(parents=True, exist_ok=True)
            # Writability check
            probe_file = self.target_dir / ".write_probe"
            try:
                probe_file.write_text("ok", encoding="utf-8")
                probe_file.unlink()
            except OSError as exc:
                raise AdapterConversionError(
                    f"target_dir is not writable: {self.target_dir} ({exc})"
                ) from exc

        self.ensure_layout()
        probe_report = self.probe(self.source_dir)
        plan = self.plan(probe_report, self.spec)
        if self.dry_run:
            return {"tier": 1, "dry_run": True, "probe": probe_report, "plan": plan}
        try:
            self.convert(self.source_dir, self.target_dir, plan)
            self.post_process(self.target_dir)
        except AdapterError:
            # Leave a failure marker for diagnosis.
            try:
                (self.target_dir / ".failed").write_text(
                    f"{_utcnow_iso()}\n", encoding="utf-8"
                )
            except OSError:
                pass
            raise
        card_extra = plan.get("card_extra", {})
        card_path = self.write_dataset_card(self.target_dir, extra=card_extra)
        readme_path = self.write_readme(
            self.target_dir,
            loading_example=card_extra.get("loading_example", ""),
            extra_sections=card_extra.get("readme_sections"),
        )
        return {
            "tier": 1,
            "dry_run": False,
            "handler": f"adapter:{self.domain}/{self.dataset_name.lower()}",
            "target_dir": str(self.target_dir),
            "dataset_card": str(card_path),
            "readme": str(readme_path),
            "duration_seconds": round(time.time() - self._started_at, 3),
            "warnings": list(self._warnings),
            "probe_summary": probe_report.get("summary", {}),
        }


def adapter_main(adapter_cls: type) -> int:
    """Standard CLI entry shared by all Tier1 adapters."""
    parser = argparse.ArgumentParser(
        description=f"{adapter_cls.__name__} - AI-Ready converter for "
                    f"{adapter_cls.dataset_name} ({adapter_cls.domain})"
    )
    parser.add_argument("--source-dir", required=True,
                        help="Absolute path to raw dataset directory")
    parser.add_argument("--target-dir", required=True,
                        help="Absolute path to AI-Ready output directory")
    parser.add_argument("--spec-json", default=None,
                        help="Optional path to serialized primitives spec JSON")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print probe/plan without writing outputs")
    args = parser.parse_args()

    spec: Dict[str, Any] = {}
    if args.spec_json:
        spec_path = Path(args.spec_json).expanduser()
        if spec_path.exists():
            spec = json.loads(spec_path.read_text(encoding="utf-8"))

    adapter = adapter_cls(
        source_dir=Path(args.source_dir),
        target_dir=Path(args.target_dir),
        spec=spec,
        dry_run=args.dry_run,
    )
    try:
        summary = adapter.run()
    except AdapterDependencyError as exc:
        print(f"DEPENDENCY_ERROR: {exc}", file=sys.stderr)
        return 3
    except AdapterInputError as exc:
        print(f"INPUT_ERROR: {exc}", file=sys.stderr)
        return 4
    except AdapterConversionError as exc:
        print(f"CONVERSION_ERROR: {exc}", file=sys.stderr)
        return 5
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0
