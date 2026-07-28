#!/usr/bin/env python3
"""Static validation for generated complex-structure visualization HTML."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from pathlib import Path


REQUIRED_MARKERS = {
    "default_view": 'data-builtin-view="default"',
    "plddt_view": 'data-builtin-view="plddt"',
    "add_view": 'data-action="add-view"',
    "onescience_title": "OneScience Visualization",
    "sequence_filter": "data-sequence-filter",
    "sequence_hover_link": "viewer.setHoverable(",
    "custom_view_preview": 'data-action="preview-view"',
    "custom_view_delete": "csv-custom-view-delete",
    "dynamic_bonds": "data-dynamic-bonds",
    "dynamic_bonds_off": 'data-action="bonds-off"',
    "possible_hydrogen_bond_candidates": "function putativeHydrogenBonds(",
    "hydrogen_bond_distance_gate": "distance < 2.4 || distance > 3.5",
    "hydrogen_bond_angle_gate": "donorAngle < 100 ||",
    "hydrogen_bond_dashed_cylinders": "function drawPutativeHydrogenBonds(",
    "hydrogen_bond_dashed_style": "dashed: true",
    "double_bond_order_resolution": "function displayedBondOrder(",
    "double_bond_parallel_offsets": "offsets = [-0.1, 0.1]",
    "sample_selector": "data-sample-select",
    "viewer_stage": 'class="csv-stage"',
    "pae_canvas": "data-pae-canvas",
    "pae_axis_x": "Scored token / residue",
    "pae_axis_y": "Aligned token / residue",
    "protein_ribbon_default": 'proteinRep: "ribbon"',
    "nucleic_slab_default": "nucleicSlab: true",
    "ligand_sticks_default": 'ligandRep: "sticks"',
    "metal_spheres_default": 'metalRep: "spheres"',
    "water_hidden_default": 'waterRep: "hidden"',
    "rcsb_visual_preset": 'visualPreset: "rcsb"',
    "rcsb_protein_auto_width": "thickness: 0.26",
    "rcsb_protein_beta_arrows": "tubes: false",
    "rcsb_nucleic_backbone_width": "width: 0.8",
    "rcsb_nucleic_backbone_thickness": "thickness: 0.18",
    "structure_model": "viewer.addModel(structureData, format, {",
    "secondary_structure_enabled": "noComputeSecondaryStructure: false",
    "secondary_structure_diagnostics": "collectSecondaryStructureInfo()",
    "runtime_ready_state": 'root.dataset.vizState = "ready"',
    "renderer_version": 'data-csv-engine="3dmol-2.5.4"',
    "plddt_very_high": "#0053D6",
    "plddt_high": "#65CBF3",
    "plddt_low": "#FFDB13",
    "plddt_very_low": "#FF7D45",
    "alphafold_header": "#b9d4f1",
}

ENGINE_PATTERN = re.compile(
    r'<script\s+data-csv-engine="3dmol-2\.5\.4"\s+'
    r'data-sha256="([0-9a-f]{64})"\s*>(.*?)</script>',
    re.DOTALL,
)
PAYLOAD_PATTERN = re.compile(
    r"const viewerPayload\s*=\s*JSON\.parse\(.*?"
    r'atob\("([A-Za-z0-9+/=]+)"\)',
    re.DOTALL,
)


def validate_manifest(
    manifest: dict[str, object],
    *,
    html_path: Path,
    inline_renderer_sha256: str | None,
    expect_samples: int | None,
    require_pae: bool,
    require_plddt_provenance: bool,
) -> dict[str, bool]:
    raw_samples = manifest.get("samples")
    samples = raw_samples if isinstance(raw_samples, list) else []
    primitive = manifest.get("primitive")
    output = manifest.get("output")
    checks = {
        "manifest_schema": manifest.get("schema_version") == "1.4.0",
        "primitive_profile": (
            isinstance(primitive, dict)
            and primitive.get("name") == "complex_structure_visualization"
            and primitive.get("version") == "1.4.0"
            and primitive.get("delivery_profile") == "bundled_3dmol_html_v1"
            and primitive.get("renderer") == "3dmol"
            and primitive.get("renderer_version") == "2.5.4"
            and primitive.get("standard_template") is True
        ),
        "renderer_manifest_matches_html": (
            isinstance(primitive, dict)
            and inline_renderer_sha256 is not None
            and primitive.get("renderer_sha256") == inline_renderer_sha256
        ),
        "html_manifest_binding": (
            isinstance(output, dict)
            and output.get("html_bytes") == html_path.stat().st_size
            and output.get("html_sha256")
            == hashlib.sha256(html_path.read_bytes()).hexdigest()
        ),
        "sample_ids_unique": len(
            {
                sample.get("id")
                for sample in samples
                if isinstance(sample, dict)
            }
        ) == len(samples),
        "default_sample_exists": manifest.get("default_sample_id")
        in {
            sample.get("id")
            for sample in samples
            if isinstance(sample, dict)
        },
    }
    if expect_samples is not None:
        checks["expected_sample_count"] = len(samples) == expect_samples
    if require_pae:
        checks["pae_available_all_samples"] = bool(samples) and all(
            isinstance(sample, dict)
            and isinstance(sample.get("pae"), dict)
            and sample["pae"].get("available") is True
            and isinstance(sample["pae"].get("size"), int)
            and sample["pae"]["size"] > 0
            and sample["pae"].get("encoding") == "uint16-le"
            and sample["pae"].get("axis_semantics", {}).get("x")
            == "scored_token"
            and sample["pae"].get("axis_semantics", {}).get("y")
            == "aligned_token"
            for sample in samples
        )
    if require_plddt_provenance:
        checks["plddt_provenance_all_samples"] = bool(samples) and all(
            isinstance(sample, dict)
            and isinstance(sample.get("confidence_provenance"), dict)
            and sample["confidence_provenance"].get("semantic") == "plddt"
            and sample["confidence_provenance"].get("residue_score_count", 0) > 0
            and sample["confidence_provenance"].get("atom_score_count", 0) > 0
            and sample["confidence_provenance"].get("ribbon_source")
            != "unavailable"
            for sample in samples
        )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--max-bytes", type=int)
    parser.add_argument("--expect-fragment", action="store_true")
    parser.add_argument("--expect-samples", type=int)
    parser.add_argument("--require-pae", action="store_true")
    parser.add_argument("--require-plddt-provenance", action="store_true")
    args = parser.parse_args()

    path = args.html.resolve()
    text = path.read_text(encoding="utf-8")
    checks = {name: marker in text for name, marker in REQUIRED_MARKERS.items()}
    checks["no_placeholders"] = not re.search(r"__CSV_[A-Z0-9_]+__", text)
    engine_match = ENGINE_PATTERN.search(text)
    inline_renderer_sha256: str | None = None
    if engine_match:
        inline_renderer_sha256 = hashlib.sha256(
            engine_match.group(2).encode("utf-8")
        ).hexdigest()
    checks["inline_renderer_present"] = engine_match is not None
    checks["inline_renderer_hash"] = bool(
        engine_match
        and inline_renderer_sha256 == engine_match.group(1)
    )
    checks["no_external_script_src"] = not re.search(
        r"<script\b[^>]*\bsrc\s*=", text, re.IGNORECASE
    )
    payload_match = PAYLOAD_PATTERN.search(text)
    payload: dict[str, object] | None = None
    if payload_match:
        try:
            decoded = base64.b64decode(payload_match.group(1), validate=True)
            raw_payload = json.loads(decoded.decode("utf-8"))
            payload = raw_payload if isinstance(raw_payload, dict) else None
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            payload = None
    checks["embedded_payload_valid"] = bool(
        payload
        and payload.get("schema_version") == "1.4.0"
        and isinstance(payload.get("samples"), list)
        and payload.get("samples")
    )
    max_bytes = args.max_bytes
    if max_bytes is None:
        max_bytes = 2_000_000 if args.expect_fragment else 20_000_000
    checks["size_limit"] = path.stat().st_size <= max_bytes
    application_text = (
        text[:engine_match.start()] + text[engine_match.end():]
        if engine_match
        else text
    )
    checks["no_runtime_data_fetch"] = not re.search(
        r"\b(fetch|XMLHttpRequest|WebSocket)\s*\(", application_text
    )
    if args.expect_fragment:
        checks["fragment_only"] = not re.search(
            r"<!doctype|<html\b|<head\b|<body\b", text, re.IGNORECASE
        )
    if args.manifest:
        manifest_path = args.manifest.resolve()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("--manifest must contain a JSON object")
        checks.update(
            validate_manifest(
                manifest,
                html_path=path,
                inline_renderer_sha256=inline_renderer_sha256,
                expect_samples=args.expect_samples,
                require_pae=args.require_pae,
                require_plddt_provenance=args.require_plddt_provenance,
            )
        )
    elif args.expect_samples is not None or args.require_pae or args.require_plddt_provenance:
        raise ValueError(
            "--manifest is required with --expect-samples, --require-pae, "
            "or --require-plddt-provenance"
        )
    passed = all(checks.values())
    result = {
        "path": str(path),
        "bytes": path.stat().st_size,
        "passed": passed,
        "checks": checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
