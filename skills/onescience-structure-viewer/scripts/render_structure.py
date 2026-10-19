#!/usr/bin/env python3
"""Render a 3D visualization HTML for a POSCAR / XYZ / CONTCAR file.

    python3 render_structure.py structures/POSCAR \
        --contract model_contract.json \
        --outdir structures --basename view \
        --title "Cu(111) + H2O + CO2 + K" \
        --subtitle "form A / gate PASS"

Emits:
  <outdir>/<basename>.html       self-contained 3D viewer (3Dmol.js via CDN)
  <outdir>/structure.json        the raw payload (for programmatic reuse)

Exit code: 0 = OK, 2 = input error.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import viz_core as V  # noqa: E402


def _notes_from_contract(contract: dict) -> str:
    """Turn a model_contract.json into a compact HTML notes block."""
    if not contract:
        return ""
    lines = []
    if contract.get("system"):
        lines.append(f"<b>System</b>: <code>{contract['system']}</code>")
    slab = contract.get("slab") or {}
    if slab:
        bits = []
        if slab.get("layers"):         bits.append(f"layers = {slab['layers']}")
        if slab.get("fix_bottom_layers") is not None:
            bits.append(f"fixed bottom = {slab['fix_bottom_layers']}")
        if slab.get("vacuum_min"):     bits.append(f"vacuum &ge; {slab['vacuum_min']} &Aring;")
        if bits:
            lines.append("<b>Slab</b>: " + ", ".join(bits))
    species = contract.get("species") or {}
    if species:
        rows = []
        for name, spec in species.items():
            role = spec.get("role", "-")
            cnt = spec.get("count", "-")
            extra = ""
            if spec.get("mode"):        extra += f" mode={spec['mode']}"
            if spec.get("solvent_model"): extra += f" model={spec['solvent_model']}"
            if spec.get("layers_min"):   extra += f" layers_min={spec['layers_min']}"
            rows.append(f"<li><b>{name}</b> &times; {cnt} &mdash; <i>{role}</i>{extra}</li>")
        lines.append("<b>Species</b>:<ul style='margin:4px 0 4px 18px;padding:0'>" + "".join(rows) + "</ul>")
    if contract.get("delivery_form"):
        lines.append(f"<b>Delivery</b>: form {contract['delivery_form']}")
    if contract.get("output_species_order"):
        lines.append("<b>POSCAR order</b>: <code>" +
                     " ".join(contract["output_species_order"]) + "</code>")
    return "<br>".join(lines)


def _notes_from_gate(gate_path: Path) -> str:
    """Extract PASS/FAIL/WARN counts from a gate.json produced by
    check_geometry.py, so the viewer shows the gate summary inline."""
    try:
        g = json.loads(gate_path.read_text(encoding="utf-8"))
    except Exception:
        return ""
    items = g.get("items") or g.get("gates") or []
    if not items:
        return ""
    counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "INFO": 0}
    for it in items:
        st = (it.get("status") or "").upper()
        if st in counts:
            counts[st] += 1
    fails = [it for it in items if (it.get("status") or "").upper() == "FAIL"]
    html = ("<b>Gate</b>: "
            f"<span style='color:#7bd88f'>{counts['PASS']} PASS</span> / "
            f"<span style='color:#ffcf6b'>{counts['WARN']} WARN</span> / "
            f"<span style='color:#ff8080'>{counts['FAIL']} FAIL</span>")
    if fails:
        html += "<ul style='margin:4px 0 4px 18px;padding:0;color:#ffb0b0'>"
        for f in fails[:8]:
            html += f"<li>{f.get('gate','?')}: {f.get('detail','')[:180]}</li>"
        html += "</ul>"
    return html


def main() -> int:
    ap = argparse.ArgumentParser(description="Render 3D visualization HTML from POSCAR/XYZ.")
    ap.add_argument("structure", help="input POSCAR / CONTCAR / XYZ")
    ap.add_argument("--contract", help="optional model_contract.json (adds role notes)")
    ap.add_argument("--gate-json", help="optional gate.json from check_geometry.py")
    ap.add_argument("--outdir", default=None, help="output directory (default: alongside structure)")
    ap.add_argument("--basename", default="view", help="output html basename (default: view)")
    ap.add_argument("--title", default=None)
    ap.add_argument("--subtitle", default=None)
    ap.add_argument("--notes", default=None, help="extra HTML notes appended to sidebar")
    ap.add_argument("--template", default=None, help="custom viewer_template.html path")
    ap.add_argument("--bond-tol", type=float, default=0.45,
                    help="covalent-radius slack for bond detection (default 0.45 A)")
    ap.add_argument("--bond-max", type=float, default=2.6,
                    help="upper bond length cutoff (default 2.6 A)")
    ap.add_argument("--no-json", action="store_true", help="skip writing structure.json")
    args = ap.parse_args()

    struct_path = Path(args.structure)
    if not struct_path.is_file():
        print("[ERROR] structure not found: %s" % struct_path, file=sys.stderr)
        return 2

    try:
        struct = V.load_structure(struct_path)
    except Exception as exc:
        print("[ERROR] failed to parse %s: %s" % (struct_path, exc), file=sys.stderr)
        return 2

    contract = None
    if args.contract:
        try:
            contract = json.loads(Path(args.contract).read_text(encoding="utf-8"))
        except Exception as exc:
            print("[WARN] could not read contract %s: %s" % (args.contract, exc),
                  file=sys.stderr)

    notes_parts = []
    if contract:
        notes_parts.append(_notes_from_contract(contract))
    if args.gate_json:
        notes_parts.append(_notes_from_gate(Path(args.gate_json)))
    if args.notes:
        notes_parts.append(args.notes)
    notes_html = "<hr style='border:0;border-top:1px solid #2a3050;margin:8px 0'>".join(
        [p for p in notes_parts if p]
    )

    # Assign per-atom group labels from the contract when possible, so the
    # viewer can offer role-based visibility toggles.
    if contract and contract.get("framework", {}).get("elements"):
        fw = set(contract["framework"]["elements"])
        ion_els = {name for name, spec in (contract.get("species") or {}).items()
                   if spec.get("role") == "ion"}
        adsorbate_els = set()
        for name, spec in (contract.get("species") or {}).items():
            if spec.get("role") == "adsorbate":
                adsorbate_els.update(_elements_of_formula(name))
        solvent_els = set()
        for name, spec in (contract.get("species") or {}).items():
            if spec.get("role") == "solvent":
                solvent_els.update(_elements_of_formula(name))
        for a in struct.atoms:
            if a.el in fw:
                a.group = "slab"
            elif a.el in ion_els:
                a.group = "ion"
            elif a.el in adsorbate_els and a.el not in solvent_els:
                a.group = "adsorbate"
            elif a.el in solvent_els:
                a.group = "solvent"

    payload = V.build_payload(
        struct,
        title=args.title or struct.comment or struct_path.name,
        subtitle=args.subtitle or "",
        notes_html=notes_html,
        contract=contract,
        source_files=[str(struct_path.resolve())]
                     + ([args.contract] if args.contract else [])
                     + ([args.gate_json] if args.gate_json else []),
        bond_tol=args.bond_tol,
        bond_max_len=args.bond_max,
    )

    outdir = Path(args.outdir) if args.outdir else struct_path.parent
    paths = V.write_outputs(payload, outdir, basename=args.basename,
                            template_path=args.template,
                            write_json=not args.no_json)

    # --- copy 3Dmol-min.js alongside view.html (CSP-safe local serving) ---
    _assets = Path(__file__).resolve().parent.parent / "assets"
    _src_js = _assets / "3Dmol-min.js"
    _dst_js = outdir / "3Dmol-min.js"
    if _src_js.is_file() and _src_js != _dst_js:
        shutil.copy2(str(_src_js), str(_dst_js))

    print("[OK] html : %s" % paths["html"])
    if "json" in paths:
        print("[OK] json : %s" % paths["json"])
    print("     atoms: %d (%s)" % (payload["n_atoms"], payload["formula"]))
    print("     bonds: %d   fixed: %d   cell: %.2f x %.2f x %.2f A"
          % (len(payload["bonds"]), payload["n_fixed"],
             *payload["cell_lengths"]))
    return 0


def _elements_of_formula(formula: str) -> set:
    """Extract the set of element symbols from a formula like 'CO2' or 'H2O'."""
    import re
    return set(re.findall(r"[A-Z][a-z]?", formula or ""))


if __name__ == "__main__":
    sys.exit(main())
