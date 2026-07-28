#!/usr/bin/env python3
"""Render a PDB/mmCIF structure with the complex-structure visualization template.

The implementation is deliberately dependency-free. It creates either a Codex
HTML fragment or a portable standalone HTML document without network or model
calls during generation or viewing. The pinned 3Dmol.js runtime is vendored
beside this script and embedded into every generated document.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


PRIMITIVE_NAME = "complex_structure_visualization"
PRIMITIVE_VERSION = "1.4.0"
SCHEMA_VERSION = "1.4.0"
DELIVERY_PROFILE = "bundled_3dmol_html_v1"
RENDERER_NAME = "3dmol"
RENDERER_VERSION = "2.5.4"
RENDERER_ASSET = Path("vendor") / "3Dmol-2.5.4.min.js"

PROTEIN_RESIDUES = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE",
    "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
    "ASX", "GLX", "SEC", "PYL", "MSE",
}
DNA_RESIDUES = {"DA", "DC", "DG", "DT", "DI", "DU"}
RNA_RESIDUES = {"A", "C", "G", "U", "I"}
WATER_RESIDUES = {"HOH", "WAT", "H2O", "DOD"}
ION_ELEMENTS = {
    "LI", "NA", "K", "RB", "CS", "MG", "CA", "SR", "BA", "AL", "GA", "IN",
    "TL", "V", "CR", "MN", "FE", "CO", "NI", "CU", "ZN", "Y", "ZR", "NB",
    "MO", "TC", "RU", "RH", "PD", "AG", "CD", "HF", "TA", "W", "RE", "OS",
    "IR", "PT", "AU", "HG", "PB", "BI", "F", "CL", "BR", "I",
}


@dataclass(frozen=True)
class AtomRecord:
    group: str
    atom: str
    resn: str
    chain: str
    resi: int | str | None
    label_chain: str
    label_resi: int | str | None
    b: float | None
    elem: str
    entity: str
    model: int


def _clean(value: str | None) -> str:
    if value is None or value in {".", "?"}:
        return ""
    return value


def _number(value: str | None) -> int | str | None:
    cleaned = _clean(value)
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return cleaned


def _float(value: str | None) -> float | None:
    cleaned = _clean(value)
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _int(value: str | None, default: int = 1) -> int:
    cleaned = _clean(value)
    if not cleaned:
        return default
    try:
        return int(cleaned)
    except ValueError:
        return default


def cif_tokens(text: str) -> Iterator[str]:
    """Yield CIF tokens while preserving apostrophes in unquoted atom names."""

    index = 0
    length = len(text)
    line_start = True
    while index < length:
        character = text[index]
        if character in " \t\r\n":
            line_start = character == "\n" or (line_start and character in " \t\r")
            index += 1
            continue
        if character == "#":
            while index < length and text[index] != "\n":
                index += 1
            line_start = True
            continue
        if character == ";" and line_start:
            index += 1
            if index < length and text[index] == "\r":
                index += 1
            if index < length and text[index] == "\n":
                index += 1
            start = index
            while index < length:
                if text[index] == "\n" and index + 1 < length and text[index + 1] == ";":
                    value = text[start:index]
                    index += 2
                    while index < length and text[index] != "\n":
                        index += 1
                    yield value
                    line_start = True
                    break
                index += 1
            else:
                yield text[start:]
            continue
        if character in {'"', "'"}:
            quote = character
            index += 1
            start = index
            while index < length:
                if text[index] == quote and (
                    index + 1 == length or text[index + 1].isspace()
                ):
                    yield text[start:index]
                    index += 1
                    line_start = False
                    break
                index += 1
            else:
                yield text[start:]
            continue

        start = index
        while index < length and not text[index].isspace():
            index += 1
        yield text[start:index]
        line_start = False


def parse_cif_document(text: str) -> tuple[dict[str, str], list[tuple[list[str], list[list[str]]]]]:
    tokens = list(cif_tokens(text))
    singles: dict[str, str] = {}
    loops: list[tuple[list[str], list[list[str]]]] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        lowered = token.lower()
        if lowered == "loop_":
            index += 1
            headers: list[str] = []
            while index < len(tokens) and tokens[index].startswith("_"):
                headers.append(tokens[index].lower())
                index += 1
            if not headers:
                continue
            values: list[str] = []
            while index < len(tokens):
                candidate = tokens[index]
                control = candidate.lower()
                if (
                    candidate.startswith("_")
                    or control == "loop_"
                    or control == "stop_"
                    or control.startswith("data_")
                    or control.startswith("save_")
                ):
                    break
                values.append(candidate)
                index += 1
            usable = len(values) - (len(values) % len(headers))
            rows = [
                values[offset:offset + len(headers)]
                for offset in range(0, usable, len(headers))
            ]
            loops.append((headers, rows))
            continue
        if token.startswith("_") and index + 1 < len(tokens):
            singles[token.lower()] = tokens[index + 1]
            index += 2
            continue
        index += 1
    return singles, loops


def loop_rows(
    loops: Sequence[tuple[list[str], list[list[str]]]],
    prefix: str,
) -> list[dict[str, str]]:
    normalized = prefix.lower()
    for headers, rows in loops:
        if headers and all(header.startswith(normalized) for header in headers):
            return [dict(zip(headers, row)) for row in rows]
    return []


def role_from_poly_type(poly_type: str) -> str | None:
    normalized = poly_type.lower()
    if "polypeptide" in normalized:
        return "protein"
    if "polydeoxyribonucleotide" in normalized:
        return "dna"
    if "polyribonucleotide" in normalized:
        return "rna"
    return None


def parse_mmcif(text: str) -> tuple[list[AtomRecord], dict[str, object]]:
    singles, loops = parse_cif_document(text)
    entity_roles: dict[str, str] = {}
    for row in loop_rows(loops, "_entity_poly."):
        role = role_from_poly_type(row.get("_entity_poly.type", ""))
        entity_id = _clean(row.get("_entity_poly.entity_id"))
        if role and entity_id:
            entity_roles[entity_id] = role

    atoms: list[AtomRecord] = []
    atom_rows = loop_rows(loops, "_atom_site.")
    if not atom_rows:
        raise ValueError("mmCIF does not contain an _atom_site loop")
    for row in atom_rows:
        model = _int(row.get("_atom_site.pdbx_pdb_model_num"), 1)
        if model != 1:
            continue
        atoms.append(
            AtomRecord(
                group=_clean(row.get("_atom_site.group_pdb")).upper() or "ATOM",
                atom=_clean(
                    row.get("_atom_site.auth_atom_id")
                    or row.get("_atom_site.label_atom_id")
                ),
                resn=_clean(
                    row.get("_atom_site.auth_comp_id")
                    or row.get("_atom_site.label_comp_id")
                ).upper(),
                chain=_clean(
                    row.get("_atom_site.auth_asym_id")
                    or row.get("_atom_site.label_asym_id")
                ) or "_",
                resi=_number(
                    row.get("_atom_site.auth_seq_id")
                    or row.get("_atom_site.label_seq_id")
                ),
                label_chain=_clean(row.get("_atom_site.label_asym_id")) or "_",
                label_resi=_number(row.get("_atom_site.label_seq_id")),
                b=_float(row.get("_atom_site.b_iso_or_equiv")),
                elem=_clean(row.get("_atom_site.type_symbol")).upper(),
                entity=_clean(row.get("_atom_site.label_entity_id")),
                model=model,
            )
        )

    metric_rows = loop_rows(loops, "_ma_qa_metric.")
    local_plddt_ids = {
        _clean(row.get("_ma_qa_metric.id"))
        for row in metric_rows
        if _clean(row.get("_ma_qa_metric.mode")).lower() == "local"
        and "plddt" in _clean(row.get("_ma_qa_metric.name")).lower()
    }
    local_score_map: dict[tuple[str, int | str | None], float] = {}
    local_scores: list[tuple[str, float]] = []
    for row in loop_rows(loops, "_ma_qa_metric_local."):
        if (
            _clean(row.get("_ma_qa_metric_local.metric_id")) in local_plddt_ids
            and _int(row.get("_ma_qa_metric_local.model_id"), 1) == 1
        ):
            score = _float(row.get("_ma_qa_metric_local.metric_value"))
            if score is not None:
                chain = _clean(row.get("_ma_qa_metric_local.label_asym_id")) or "_"
                sequence = _number(row.get("_ma_qa_metric_local.label_seq_id"))
                local_scores.append((chain, score))
                local_score_map[(chain, sequence)] = score

    global_plddt_ids = {
        _clean(row.get("_ma_qa_metric.id"))
        for row in metric_rows
        if _clean(row.get("_ma_qa_metric.mode")).lower() == "global"
        and "plddt" in _clean(row.get("_ma_qa_metric.name")).lower()
    }
    global_quality: float | None = None
    for row in loop_rows(loops, "_ma_qa_metric_global."):
        if (
            _clean(row.get("_ma_qa_metric_global.metric_id")) in global_plddt_ids
            and _int(row.get("_ma_qa_metric_global.model_id"), 1) == 1
        ):
            global_quality = _float(row.get("_ma_qa_metric_global.metric_value"))
            if global_quality is not None:
                break
    if global_quality is None and global_plddt_ids:
        global_quality = _float(singles.get("_ma_qa_metric_global.metric_value"))
    plddt_summary: dict[str, object] | None = None
    if local_scores:
        values = [score for _, score in local_scores]
        chains = sorted({chain for chain, _ in local_scores})
        plddt_summary = {
            "global": global_quality,
            "local_count": len(values),
            "mean": round(sum(values) / len(values), 2),
            "min": min(values),
            "max": max(values),
            "bands": {
                "gte_90": sum(value >= 90 for value in values),
                "70_to_89": sum(70 <= value < 90 for value in values),
                "50_to_69": sum(50 <= value < 70 for value in values),
                "lt_50": sum(value < 50 for value in values),
            },
            "by_chain": {
                chain: {
                    "count": len(chain_values),
                    "mean": round(sum(chain_values) / len(chain_values), 2),
                    "min": min(chain_values),
                    "max": max(chain_values),
                }
                for chain in chains
                for chain_values in [[
                    score for score_chain, score in local_scores if score_chain == chain
                ]]
            },
        }

    metadata: dict[str, object] = {
        "entity_roles": entity_roles,
        "global_quality": global_quality,
        "plddt_summary": plddt_summary,
        "plddt_local_map": local_score_map,
        "plddt_local_metric_ids": sorted(local_plddt_ids),
        "structure_diagnostics": {
            "format": "cif",
            "struct_conf_records": len(loop_rows(loops, "_struct_conf.")),
            "struct_sheet_range_records": len(
                loop_rows(loops, "_struct_sheet_range.")
            ),
            "secondary_structure_source": (
                "input_annotations"
                if (
                    loop_rows(loops, "_struct_conf.")
                    or loop_rows(loops, "_struct_sheet_range.")
                )
                else f"{RENDERER_NAME}-{RENDERER_VERSION}:coordinate_inference"
            ),
        },
    }
    return atoms, metadata


def infer_element(atom_name: str) -> str:
    stripped = re.sub(r"^[0-9]+", "", atom_name.strip()).upper()
    if len(stripped) >= 2 and stripped[:2] in ION_ELEMENTS:
        return stripped[:2]
    return stripped[:1]


def parse_pdb(text: str) -> tuple[list[AtomRecord], dict[str, object]]:
    atoms: list[AtomRecord] = []
    current_model = 1
    saw_model = False
    record_counts: Counter[str] = Counter()
    for line in text.splitlines():
        record = line[:6].strip().upper()
        if record in {"HELIX", "SHEET", "CONECT", "TER"}:
            record_counts[record] += 1
        if record == "MODEL":
            saw_model = True
            current_model = _int(line[10:14].strip(), 1)
            continue
        if record == "ENDMDL" and saw_model and current_model == 1:
            break
        if record not in {"ATOM", "HETATM"} or current_model != 1:
            continue
        atom_name = line[12:16].strip()
        element = line[76:78].strip().upper() or infer_element(atom_name)
        sequence = line[22:26].strip()
        insertion = line[26:27].strip()
        resi: int | str | None = _number(sequence)
        if insertion and resi is not None:
            resi = f"{resi}{insertion}"
        atoms.append(
            AtomRecord(
                group=record,
                atom=atom_name,
                resn=line[17:20].strip().upper(),
                chain=line[21:22].strip() or "_",
                resi=resi,
                label_chain=line[21:22].strip() or "_",
                label_resi=resi,
                b=_float(line[60:66].strip()),
                elem=element,
                entity="",
                model=1,
            )
        )
    if not atoms:
        raise ValueError("PDB does not contain ATOM/HETATM records")
    return atoms, {
        "entity_roles": {},
        "global_quality": None,
        "plddt_summary": None,
        "plddt_local_map": {},
        "plddt_local_metric_ids": [],
        "structure_diagnostics": {
            "format": "pdb",
            "helix_records": record_counts["HELIX"],
            "sheet_records": record_counts["SHEET"],
            "conect_records": record_counts["CONECT"],
            "ter_records": record_counts["TER"],
            "secondary_structure_source": (
                "input_annotations"
                if record_counts["HELIX"] or record_counts["SHEET"]
                else f"{RENDERER_NAME}-{RENDERER_VERSION}:coordinate_inference"
            ),
        },
    }


def polymer_chain_roles(atoms: Sequence[AtomRecord], entity_roles: dict[str, str]) -> dict[str, str]:
    votes: dict[str, Counter[str]] = defaultdict(Counter)
    for atom in atoms:
        if atom.entity in entity_roles:
            votes[atom.chain][entity_roles[atom.entity]] += 5
        if atom.resn in PROTEIN_RESIDUES:
            votes[atom.chain]["protein"] += 1
        elif atom.resn in DNA_RESIDUES:
            votes[atom.chain]["dna"] += 1
        elif atom.resn in RNA_RESIDUES:
            votes[atom.chain]["rna"] += 1
    return {
        chain: counts.most_common(1)[0][0]
        for chain, counts in votes.items()
        if counts
    }


def classify_atom(
    atom: AtomRecord,
    entity_roles: dict[str, str],
    chain_roles: dict[str, str],
) -> str:
    if atom.entity in entity_roles:
        return entity_roles[atom.entity]
    if atom.resn in WATER_RESIDUES:
        return "water"
    if atom.elem in ION_ELEMENTS and (
        atom.group == "HETATM" or atom.resn == atom.elem
    ):
        return "metal"
    if atom.resn in PROTEIN_RESIDUES:
        return "protein"
    if atom.resn in DNA_RESIDUES:
        return "dna"
    if atom.resn in RNA_RESIDUES:
        return "rna"
    if atom.group == "ATOM" and atom.chain in chain_roles:
        return chain_roles[atom.chain]
    if atom.group == "HETATM":
        if atom.chain in chain_roles and atom.resn in {"MSE", "SEC", "PYL"}:
            return chain_roles[atom.chain]
        return "ligand"
    return "other"


def residue_identity(atom: AtomRecord) -> str:
    return f"{atom.chain}:{atom.resi if atom.resi is not None else '?'}:{atom.resn or 'UNK'}"


def summarize_plddt(
    residue_scores: dict[tuple[str, int | str | None], float],
    global_quality: float | None,
) -> dict[str, object] | None:
    if not residue_scores:
        return None
    rows = [
        (chain, score)
        for (chain, _sequence), score in residue_scores.items()
    ]
    values = [score for _, score in rows]
    chains = sorted({chain for chain, _ in rows})
    return {
        "global": global_quality,
        "local_count": len(values),
        "mean": round(sum(values) / len(values), 2),
        "min": min(values),
        "max": max(values),
        "bands": {
            "gte_90": sum(value >= 90 for value in values),
            "70_to_89": sum(70 <= value < 90 for value in values),
            "50_to_69": sum(50 <= value < 70 for value in values),
            "lt_50": sum(value < 50 for value in values),
        },
        "by_chain": {
            chain: {
                "count": len(chain_values),
                "mean": round(sum(chain_values) / len(chain_values), 2),
                "min": min(chain_values),
                "max": max(chain_values),
            }
            for chain in chains
            for chain_values in [[
                score for score_chain, score in rows if score_chain == chain
            ]]
        },
    }


def build_payload(
    atoms: Sequence[AtomRecord],
    parser_metadata: dict[str, object],
    title: str,
    confidence_semantic: str,
    external_atom_plddts: Sequence[float] | None = None,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    entity_roles = dict(parser_metadata.get("entity_roles", {}))
    chain_roles = polymer_chain_roles(atoms, entity_roles)
    records: list[dict[str, object]] = []
    entities: dict[str, dict[str, object]] = {}

    atom_plddts: list[float | None] = []
    validation: dict[str, object] = {
        "compared_atom_count": 0,
        "max_abs_delta": None,
        "mean_abs_delta": None,
        "matches_mmcif_b_factor": None,
    }
    if external_atom_plddts is not None:
        if len(external_atom_plddts) != len(atoms):
            raise ValueError(
                "confidence JSON atom_plddts length does not match structure atom count: "
                f"{len(external_atom_plddts)} != {len(atoms)}"
            )
        atom_plddts = [float(value) for value in external_atom_plddts]
        deltas = [
            abs(value - atom.b)
            for atom, value in zip(atoms, atom_plddts)
            if atom.b is not None
        ]
        if deltas:
            validation = {
                "compared_atom_count": len(deltas),
                "max_abs_delta": round(max(deltas), 6),
                "mean_abs_delta": round(sum(deltas) / len(deltas), 6),
                "matches_mmcif_b_factor": max(deltas) <= 0.02,
            }
            if max(deltas) > 0.02:
                raise ValueError(
                    "confidence JSON atom_plddts do not match mmCIF B_iso_or_equiv "
                    f"(max absolute delta {max(deltas):.4f})"
                )
    elif confidence_semantic == "plddt":
        atom_plddts = [atom.b for atom in atoms]
    else:
        atom_plddts = [None for _ in atoms]

    raw_local_map = parser_metadata.get("plddt_local_map", {})
    residue_plddt: dict[tuple[str, int | str | None], float] = {
        (str(chain), sequence): float(score)
        for (chain, sequence), score in dict(raw_local_map).items()
    }
    ribbon_source = "unavailable"
    if confidence_semantic == "plddt" and residue_plddt:
        ribbon_source = "mmcif:_ma_qa_metric_local"
    elif confidence_semantic == "plddt":
        grouped: dict[tuple[str, int | str | None], list[float]] = defaultdict(list)
        for atom, value in zip(atoms, atom_plddts):
            if value is not None:
                grouped[(atom.label_chain, atom.label_resi)].append(value)
        residue_plddt = {
            key: round(sum(values) / len(values), 4)
            for key, values in grouped.items()
            if values
        }
        if residue_plddt:
            ribbon_source = (
                "af3_confidences_json:atom_plddts(residue_mean)"
                if external_atom_plddts is not None
                else "structure:B_iso_or_equiv(residue_mean)"
            )

    plddt_summary = parser_metadata.get("plddt_summary")
    if confidence_semantic == "plddt" and not plddt_summary:
        global_quality = (
            round(
                sum(value for value in atom_plddts if value is not None)
                / sum(value is not None for value in atom_plddts),
                2,
            )
            if any(value is not None for value in atom_plddts)
            else None
        )
        plddt_summary = summarize_plddt(residue_plddt, global_quality)

    for atom_index, atom in enumerate(atoms):
        role = classify_atom(atom, entity_roles, chain_roles)
        if role in {"protein", "dna", "rna"}:
            entity_id = f"{role}:{atom.chain}"
            role_names = {"protein": "蛋白", "dna": "DNA", "rna": "RNA"}
            label = f"{role_names[role]}链 {atom.chain}"
        elif role == "water":
            entity_id = "water:all"
            label = "水分子"
        else:
            residue_id = residue_identity(atom)
            entity_id = f"{role}:{residue_id}"
            role_names = {"ligand": "配体", "metal": "离子", "other": "其他"}
            label = (
                f"{role_names.get(role, '其他')} {atom.resn or 'UNK'} "
                f"{atom.chain}:{atom.resi if atom.resi is not None else '?'}"
            )

        records.append(
            {
                "a": atom.atom,
                "r": atom.resn,
                "c": atom.chain,
                "i": atom.resi,
                "p": residue_plddt.get((atom.label_chain, atom.label_resi)),
                "ap": atom_plddts[atom_index],
                "role": role,
                "e": entity_id,
            }
        )
        if entity_id not in entities:
            entities[entity_id] = {
                "id": entity_id,
                "label": label,
                "role": role,
                "chain": atom.chain,
                "resi": atom.resi if role not in {"protein", "dna", "rna", "water"} else None,
                "resn": atom.resn if role not in {"protein", "dna", "rna", "water"} else None,
            }

    ordered = sorted(
        entities.values(),
        key=lambda item: (
            str(item["chain"]),
            str(item["resi"] if item["resi"] is not None else ""),
            str(item["resn"] if item["resn"] is not None else ""),
        ),
    )
    manifest: dict[str, object] = {
        "title": title,
        "atom_count": len(records),
        "proteins": [item for item in ordered if item["role"] == "protein"],
        "dna": [item for item in ordered if item["role"] == "dna"],
        "rna": [item for item in ordered if item["role"] == "rna"],
        "ligands": [item for item in ordered if item["role"] == "ligand"],
        "metals": [item for item in ordered if item["role"] == "metal"],
        "waters": [item for item in ordered if item["role"] == "water"],
        "others": [item for item in ordered if item["role"] == "other"],
        "quality_metrics": {
            "plddt": plddt_summary,
        },
        "confidence_provenance": {
            "semantic": confidence_semantic,
            "ribbon_source": ribbon_source,
            "atom_source": (
                "af3_confidences_json:atom_plddts"
                if external_atom_plddts is not None
                else (
                    "structure:B_iso_or_equiv"
                    if confidence_semantic == "plddt"
                    else "unconfirmed"
                )
            ),
            "atom_validation": validation,
            "residue_score_count": len(residue_plddt),
            "atom_score_count": sum(value is not None for value in atom_plddts),
        },
    }
    return records, manifest


def read_json_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(text)
            temporary_path = Path(handle.name)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def build_pae_payload(confidence: dict[str, object] | None) -> dict[str, object] | None:
    if not confidence or "pae" not in confidence:
        return None
    raw_matrix = confidence.get("pae")
    if not isinstance(raw_matrix, list) or not raw_matrix:
        raise ValueError("confidence JSON pae must be a non-empty square matrix")
    size = len(raw_matrix)
    matrix: list[list[float]] = []
    flat_values: list[float] = []
    for row_index, raw_row in enumerate(raw_matrix):
        if not isinstance(raw_row, list) or len(raw_row) != size:
            raise ValueError(
                f"confidence JSON pae row {row_index} has length "
                f"{len(raw_row) if isinstance(raw_row, list) else 'invalid'}, expected {size}"
            )
        row: list[float] = []
        for raw_value in raw_row:
            value = float(raw_value)
            if not math.isfinite(value) or value < 0:
                raise ValueError("confidence JSON pae contains a non-finite or negative value")
            row.append(value)
            flat_values.append(value)
        matrix.append(row)

    token_chain_ids = confidence.get("token_chain_ids")
    token_res_ids = confidence.get("token_res_ids")
    if not isinstance(token_chain_ids, list) or len(token_chain_ids) != size:
        raise ValueError("confidence JSON token_chain_ids length must equal pae dimension")
    if not isinstance(token_res_ids, list) or len(token_res_ids) != size:
        raise ValueError("confidence JSON token_res_ids length must equal pae dimension")
    chains = [str(value) for value in token_chain_ids]
    residues = [
        int(value) if isinstance(value, (int, float)) and float(value).is_integer() else str(value)
        for value in token_res_ids
    ]

    boundaries: list[dict[str, object]] = []
    start = 0
    for index in range(1, size + 1):
        if index == size or chains[index] != chains[start]:
            boundaries.append(
                {
                    "chain": chains[start],
                    "start": start,
                    "end": index - 1,
                    "start_residue": residues[start],
                    "end_residue": residues[index - 1],
                }
            )
            start = index

    scale = 10
    encoded = bytearray()
    max_quantized = 65535
    for value in flat_values:
        quantized = min(max_quantized, max(0, round(value * scale)))
        encoded.extend(int(quantized).to_bytes(2, "little"))
    observed_max = max(flat_values)
    display_max = max(31.75, math.ceil(observed_max * 4) / 4)
    return {
        "available": True,
        "encoding": "uint16-le",
        "scale": scale,
        "size": size,
        "values_b64": base64.b64encode(encoded).decode("ascii"),
        "min": min(flat_values),
        "max": observed_max,
        "mean": sum(flat_values) / len(flat_values),
        "display_max": display_max,
        "token_chain_ids": chains,
        "token_res_ids": residues,
        "chain_boundaries": boundaries,
        "axis_semantics": {
            "x": "scored_token",
            "y": "aligned_token",
            "definition": "pae[i][j]: token j error when aligned on token i",
        },
    }


def resolve_structure_format(path: Path, requested: str) -> str:
    selected = requested
    if selected == "auto":
        selected = "pdb" if path.suffix.lower() == ".pdb" else "cif"
    return "cif" if selected == "mmcif" else selected


def parse_structure(path: Path, requested_format: str) -> tuple[str, str, list[AtomRecord], dict[str, object]]:
    parser_format = resolve_structure_format(path, requested_format)
    structure_text = path.read_text(encoding="utf-8")
    if parser_format == "pdb":
        atoms, parser_metadata = parse_pdb(structure_text)
    else:
        atoms, parser_metadata = parse_mmcif(structure_text)
    return structure_text, parser_format, atoms, parser_metadata


def normalize_confidence_semantic(
    requested: str,
    parser_metadata: dict[str, object],
    confidence: dict[str, object] | None,
) -> str:
    if requested != "auto":
        return requested
    if confidence and isinstance(confidence.get("atom_plddts"), list):
        return "plddt"
    if parser_metadata.get("plddt_local_map"):
        return "plddt"
    return "none"


def build_sample_payload(
    *,
    sample_id: str,
    label: str,
    structure_path: Path,
    requested_format: str,
    confidence_semantic: str,
    confidence_path: Path | None,
    summary_path: Path | None,
    title: str,
) -> dict[str, object]:
    if not structure_path.is_file():
        raise FileNotFoundError(f"sample structure not found: {structure_path}")
    structure_text, parser_format, atoms, parser_metadata = parse_structure(
        structure_path, requested_format
    )
    confidence = (
        read_json_object(confidence_path)
        if confidence_path is not None
        else None
    )
    summary_confidences = (
        read_json_object(summary_path)
        if summary_path is not None
        else None
    )
    semantic = normalize_confidence_semantic(
        confidence_semantic, parser_metadata, confidence
    )
    external_atom_plddts: Sequence[float] | None = None
    if confidence and isinstance(confidence.get("atom_plddts"), list):
        external_atom_plddts = [
            float(value) for value in confidence["atom_plddts"]
        ]
    atom_metadata, manifest = build_payload(
        atoms,
        parser_metadata,
        title,
        semantic,
        external_atom_plddts=external_atom_plddts,
    )
    plddt_summary = manifest.get("quality_metrics", {}).get("plddt")
    runtime_config = {
        "confidence_semantic": semantic,
        "global_quality": (
            plddt_summary.get("global")
            if isinstance(plddt_summary, dict)
            else parser_metadata.get("global_quality")
        ),
        "plddt_summary": plddt_summary,
        "summary_confidences": summary_confidences,
        "source_name": structure_path.name,
        "confidence_source_name": confidence_path.name if confidence_path else None,
        "structure_diagnostics": parser_metadata.get(
            "structure_diagnostics", {}
        ),
        "generator": f"{PRIMITIVE_NAME}/{PRIMITIVE_VERSION}",
        "renderer": {
            "name": RENDERER_NAME,
            "version": RENDERER_VERSION,
            "secondary_structure": "coordinate_inference",
        },
    }
    return {
        "id": sample_id,
        "label": label,
        "title": title,
        "structure_format": parser_format,
        "structure_data": structure_text,
        "atom_metadata": atom_metadata,
        "manifest": manifest,
        "runtime_config": runtime_config,
        "pae": build_pae_payload(confidence),
        "source": {
            "structure_path": str(structure_path),
            "structure_sha256": sha256_file(structure_path),
            "confidence_path": str(confidence_path) if confidence_path else None,
            "confidence_sha256": sha256_file(confidence_path) if confidence_path else None,
            "summary_path": str(summary_path) if summary_path else None,
            "summary_sha256": sha256_file(summary_path) if summary_path else None,
        },
    }


def manifest_path(base: Path, raw_value: object, field: str) -> Path | None:
    if raw_value is None or raw_value == "":
        return None
    if not isinstance(raw_value, str):
        raise ValueError(f"sample field {field} must be a string path")
    path = Path(raw_value)
    return (base / path).resolve() if not path.is_absolute() else path.resolve()


def load_samples_manifest(
    path: Path,
    requested_format: str,
    requested_semantic: str,
    fallback_title: str | None,
) -> tuple[dict[str, object], str]:
    document = read_json_object(path)
    raw_samples = document.get("samples")
    if not isinstance(raw_samples, list) or not raw_samples:
        raise ValueError("samples manifest must contain a non-empty samples array")
    base = path.parent
    root_title = fallback_title or str(document.get("title") or path.stem)
    default_semantic = str(
        document.get("confidence_semantic") or requested_semantic
    )
    samples: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for index, raw_sample in enumerate(raw_samples):
        if not isinstance(raw_sample, dict):
            raise ValueError(f"samples[{index}] must be an object")
        sample_id = str(raw_sample.get("id") or f"sample-{index}")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", sample_id):
            raise ValueError(f"invalid sample id: {sample_id}")
        if sample_id in seen_ids:
            raise ValueError(f"duplicate sample id: {sample_id}")
        seen_ids.add(sample_id)
        structure_path = manifest_path(base, raw_sample.get("structure"), "structure")
        if structure_path is None:
            raise ValueError(f"samples[{index}] is missing structure")
        confidence_path = manifest_path(
            base, raw_sample.get("confidence"), "confidence"
        )
        summary_path = manifest_path(base, raw_sample.get("summary"), "summary")
        sample_title = str(raw_sample.get("title") or root_title)
        label = str(raw_sample.get("label") or sample_id)
        sample_format = str(raw_sample.get("format") or requested_format)
        sample_semantic = str(
            raw_sample.get("confidence_semantic") or default_semantic
        )
        sample_payload = build_sample_payload(
            sample_id=sample_id,
            label=label,
            structure_path=structure_path,
            requested_format=sample_format,
            confidence_semantic=sample_semantic,
            confidence_path=confidence_path,
            summary_path=summary_path,
            title=sample_title,
        )
        if raw_sample.get("ranking_score") is not None:
            summary_values = sample_payload["runtime_config"].get(
                "summary_confidences"
            )
            if not isinstance(summary_values, dict):
                summary_values = {}
                sample_payload["runtime_config"]["summary_confidences"] = summary_values
            summary_values["ranking_score"] = float(raw_sample["ranking_score"])
        samples.append(sample_payload)
    default_sample_id = str(
        document.get("default_sample_id")
        or document.get("default_sample")
        or samples[0]["id"]
    )
    if default_sample_id not in seen_ids:
        raise ValueError(
            f"default sample id {default_sample_id!r} is not present in samples"
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "title": root_title,
        "default_sample_id": default_sample_id,
        "samples": samples,
    }, root_title


def public_manifest(viewer_payload: dict[str, object]) -> dict[str, object]:
    samples = []
    for sample in viewer_payload["samples"]:
        manifest = sample["manifest"]
        pae = sample.get("pae")
        samples.append(
            {
                "id": sample["id"],
                "label": sample["label"],
                "title": sample["title"],
                "structure_format": sample["structure_format"],
                "atom_count": manifest["atom_count"],
                "entity_counts": {
                    key: len(manifest[key])
                    for key in (
                        "proteins",
                        "dna",
                        "rna",
                        "ligands",
                        "metals",
                        "waters",
                        "others",
                    )
                },
                "quality_metrics": manifest["quality_metrics"],
                "confidence_provenance": manifest["confidence_provenance"],
                "pae": (
                    {
                        key: pae[key]
                        for key in (
                            "available",
                            "encoding",
                            "scale",
                            "size",
                            "min",
                            "max",
                            "mean",
                            "display_max",
                            "chain_boundaries",
                            "axis_semantics",
                        )
                    }
                    if pae
                    else {"available": False}
                ),
                "runtime_config": sample["runtime_config"],
                "source": sample["source"],
            }
        )
    return {
        "schema_version": viewer_payload["schema_version"],
        "primitive": viewer_payload.get("primitive", {}),
        "title": viewer_payload["title"],
        "default_sample_id": viewer_payload["default_sample_id"],
        "sample_count": len(samples),
        "samples": samples,
    }


def json_b64(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    return base64.b64encode(encoded).decode("ascii")


def safe_js_string(text: str) -> str:
    value = json.dumps(text, ensure_ascii=False)
    return (
        value.replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def structure_expression(text: str, mode: str) -> str:
    selected_mode = mode
    if selected_mode == "auto":
        selected_mode = "json" if len(text.encode("utf-8")) <= 8_000_000 else "base64"
    if selected_mode == "json":
        return safe_js_string(text)
    payload = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return (
        "new TextDecoder().decode("
        f"Uint8Array.from(atob(\"{payload}\"), character => character.charCodeAt(0))"
        ")"
    )


def standalone_shell(fragment: str, title: str) -> str:
    escaped_title = (
        title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escaped_title}</title>
  <style>
    :root {{
      color-scheme: light dark;
      --background: #f7f8fa;
      --foreground: #16181d;
      --card: #ffffff;
      --card-foreground: #16181d;
      --popover: #ffffff;
      --popover-foreground: #16181d;
      --primary: #222833;
      --primary-foreground: #ffffff;
      --secondary: #e8ebf0;
      --secondary-foreground: #23272f;
      --muted: #edf0f4;
      --muted-foreground: #5f6672;
      --accent: #e7eefc;
      --accent-foreground: #1b315d;
      --border: #d5dae2;
      --input: #c9d0da;
      --ring: #4f6fad;
      --viz-series-1: #3d67b1;
      --viz-series-2: #24877c;
      --viz-series-3: #b87a27;
      --viz-series-4: #a34d69;
      --viz-series-5: #7056a6;
      --viz-series-6: #66717e;
      --font-size-base: 15px;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --background: #111318;
        --foreground: #edf0f5;
        --card: #1a1e25;
        --card-foreground: #edf0f5;
        --popover: #20252d;
        --popover-foreground: #f2f4f8;
        --primary: #e8ecf3;
        --primary-foreground: #171a20;
        --secondary: #292f39;
        --secondary-foreground: #eef1f5;
        --muted: #252a32;
        --muted-foreground: #aeb5c0;
        --accent: #25334c;
        --accent-foreground: #dce7ff;
        --border: #363d49;
        --input: #485160;
        --ring: #91a8d9;
        --viz-series-1: #82a8ed;
        --viz-series-2: #66c5b9;
        --viz-series-3: #e2ae68;
        --viz-series-4: #df8da9;
        --viz-series-5: #b19adc;
        --viz-series-6: #aeb7c4;
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 1rem;
      background: var(--background);
      color: var(--foreground);
      font: 400 var(--font-size-base)/1.45 system-ui, sans-serif;
    }}
    .viz-row, .viz-controls {{
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: .5rem;
    }}
    .viz-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: .7rem;
    }}
    .card {{
      padding: .9rem;
      color: var(--card-foreground);
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: .65rem;
    }}
    .btn, .form-control, .form-select {{
      min-height: 2.25rem;
      border: 1px solid var(--input);
      border-radius: .45rem;
      font: inherit;
    }}
    .btn {{
      padding: .35rem .7rem;
      color: var(--secondary-foreground);
      background: var(--secondary);
      cursor: pointer;
    }}
    .btn-primary {{
      color: var(--primary-foreground);
      background: var(--primary);
      border-color: var(--primary);
    }}
    .btn-ghost {{ background: transparent; }}
    .btn:focus-visible, .form-control:focus-visible, .form-select:focus-visible {{
      outline: 2px solid var(--ring);
      outline-offset: 2px;
    }}
    .btn:disabled {{ cursor: not-allowed; opacity: .55; }}
    .form-label {{ display: grid; gap: .25rem; }}
    .form-control, .form-select {{
      width: 100%;
      padding: .35rem .5rem;
      color: var(--foreground);
      background: var(--background);
    }}
    .form-control-color {{ width: 3.25rem; padding: .2rem; }}
    .form-check {{ display: inline-flex; align-items: center; gap: .3rem; }}
    .text-small {{ font-size: .86em; }}
    .text-muted {{ color: var(--muted-foreground); }}
    .tooltip {{
      z-index: 20;
      padding: .45rem .6rem;
      color: var(--popover-foreground);
      background: var(--popover);
      border: 1px solid var(--border);
      border-radius: .4rem;
      box-shadow: 0 .3rem 1rem color-mix(in srgb, var(--foreground) 16%, transparent);
    }}
  </style>
</head>
<body>
{fragment}
</body>
</html>
"""


def replace_template(
    template: str,
    viewer_payload: object,
    root_id: str,
    renderer_source: str,
    renderer_sha256: str,
) -> str:
    if "</script" in renderer_source.lower():
        raise ValueError("vendored renderer contains an unsafe </script sequence")
    values = {
        "__CSV_ROOT_ID__": root_id,
        "__CSV_SAMPLE_PAYLOAD_B64__": json_b64(viewer_payload),
        "__CSV_THREEDMOL_RUNTIME__": renderer_source,
        "__CSV_THREEDMOL_SHA256__": renderer_sha256,
    }
    rendered = template
    for placeholder, value in values.items():
        rendered = rendered.replace(placeholder, value)
    leftovers = sorted(set(re.findall(r"__CSV_[A-Z0-9_]+__", rendered)))
    if leftovers:
        raise ValueError(f"unresolved template placeholders: {', '.join(leftovers)}")
    return rendered


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create an interactive complex-structure visualization."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Input .cif/.mmcif/.pdb file (legacy single-sample mode)",
    )
    parser.add_argument(
        "legacy_output",
        nargs="?",
        type=Path,
        help="Output .html file (legacy single-sample mode)",
    )
    parser.add_argument(
        "--samples-manifest",
        type=Path,
        help="JSON manifest containing one or more structure/confidence sample triplets",
    )
    parser.add_argument(
        "--output",
        dest="output_option",
        type=Path,
        help="Output .html path (required with --samples-manifest)",
    )
    parser.add_argument(
        "--template",
        type=Path,
        help="Debug-only template override; requires --allow-custom-template",
    )
    parser.add_argument(
        "--allow-custom-template",
        action="store_true",
        help="Allow a non-standard template and mark the run as a debug override",
    )
    parser.add_argument(
        "--format",
        choices=("auto", "cif", "mmcif", "pdb"),
        default="auto",
        help="Input format",
    )
    parser.add_argument(
        "--confidence-semantic",
        choices=("auto", "none", "plddt", "b_factor", "external"),
        default="auto",
        help="Meaning of the confidence field; auto detects AF3 pLDDT metadata",
    )
    parser.add_argument(
        "--confidence-json",
        type=Path,
        help="AF3 *_confidences.json for atom pLDDT and PAE (single-sample mode)",
    )
    parser.add_argument(
        "--summary-confidence-json",
        type=Path,
        help="AF3 *_summary_confidences.json (single-sample mode)",
    )
    parser.add_argument("--fragment", action="store_true", help="Write an HTML fragment")
    parser.add_argument(
        "--root-id",
        default="complex-structure-viewer",
        help="Unique DOM root ID",
    )
    parser.add_argument("--title", help="Document/manifest title")
    parser.add_argument(
        "--embed-mode",
        choices=("auto", "json", "base64"),
        default="auto",
        help="How to embed structure text",
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        help="Optional JSON path for the parsed structure manifest",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.template and not args.allow_custom_template:
        raise ValueError(
            "--template is disabled for the standard delivery profile; "
            "use --allow-custom-template only for explicit debugging"
        )
    script_path = Path(__file__).resolve()
    template_path = (
        args.template.resolve()
        if args.template
        else script_path.with_name("interactive_template.html")
    )
    if not template_path.is_file():
        raise FileNotFoundError(f"template not found: {template_path}")
    renderer_path = script_path.parent / RENDERER_ASSET
    if not renderer_path.is_file():
        raise FileNotFoundError(f"vendored renderer not found: {renderer_path}")
    renderer_source = renderer_path.read_text(encoding="utf-8").rstrip("\r\n")
    renderer_sha256 = hashlib.sha256(
        renderer_source.encode("utf-8")
    ).hexdigest()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", args.root_id):
        raise ValueError("--root-id must be a CSS-safe identifier of at most 64 characters")

    if args.samples_manifest:
        if args.input is not None or args.legacy_output is not None:
            raise ValueError(
                "do not combine positional input/output with --samples-manifest"
            )
        if args.output_option is None:
            raise ValueError("--output is required with --samples-manifest")
        manifest_path_value = args.samples_manifest.resolve()
        if not manifest_path_value.is_file():
            raise FileNotFoundError(
                f"samples manifest not found: {manifest_path_value}"
            )
        output_path = args.output_option.resolve()
        viewer_payload, title = load_samples_manifest(
            manifest_path_value,
            args.format,
            args.confidence_semantic,
            args.title,
        )
        input_summary = str(manifest_path_value)
    else:
        if args.input is None:
            raise ValueError("input structure is required in single-sample mode")
        output_value = args.output_option or args.legacy_output
        if output_value is None:
            raise ValueError("output path is required")
        input_path = args.input.resolve()
        if not input_path.is_file():
            raise FileNotFoundError(f"input structure not found: {input_path}")
        output_path = output_value.resolve()
        confidence_path = args.confidence_json.resolve() if args.confidence_json else None
        summary_path = (
            args.summary_confidence_json.resolve()
            if args.summary_confidence_json
            else None
        )
        if confidence_path is not None and not confidence_path.is_file():
            raise FileNotFoundError(f"confidence JSON not found: {confidence_path}")
        if summary_path is not None and not summary_path.is_file():
            raise FileNotFoundError(
                f"summary confidence JSON not found: {summary_path}"
            )
        title = args.title or input_path.stem
        sample = build_sample_payload(
            sample_id="sample-0",
            label=title,
            structure_path=input_path,
            requested_format=args.format,
            confidence_semantic=args.confidence_semantic,
            confidence_path=confidence_path,
            summary_path=summary_path,
            title=title,
        )
        viewer_payload = {
            "schema_version": SCHEMA_VERSION,
            "title": title,
            "default_sample_id": sample["id"],
            "samples": [sample],
        }
        input_summary = str(input_path)

    viewer_payload["primitive"] = {
        "name": PRIMITIVE_NAME,
        "version": PRIMITIVE_VERSION,
        "delivery_profile": DELIVERY_PROFILE,
        "renderer": RENDERER_NAME,
        "renderer_version": RENDERER_VERSION,
        "renderer_asset": str(RENDERER_ASSET).replace("\\", "/"),
        "renderer_sha256": renderer_sha256,
        "standard_template": args.template is None,
    }
    template = template_path.read_text(encoding="utf-8")
    fragment = replace_template(
        template=template,
        viewer_payload=viewer_payload,
        root_id=args.root_id,
        renderer_source=renderer_source,
        renderer_sha256=renderer_sha256,
    )
    output_text = fragment if args.fragment else standalone_shell(fragment, title)
    write_text_atomic(output_path, output_text)

    delivery_manifest = public_manifest(viewer_payload)
    delivery_manifest["output"] = {
        "html_path": str(output_path),
        "html_sha256": sha256_file(output_path),
        "html_bytes": output_path.stat().st_size,
        "template_path": str(template_path),
        "template_sha256": sha256_file(template_path),
        "generator_path": str(script_path),
        "generator_sha256": sha256_file(script_path),
    }

    manifest_output = args.manifest_output
    if manifest_output:
        manifest_path = manifest_output.resolve()
        write_text_atomic(
            manifest_path,
            json.dumps(delivery_manifest, ensure_ascii=False, indent=2)
            + "\n",
        )

    summary = {
        "input": input_summary,
        "output": str(output_path),
        "fragment": args.fragment,
        "embed_mode": args.embed_mode,
        "sample_count": delivery_manifest["sample_count"],
        "default_sample_id": delivery_manifest["default_sample_id"],
        "samples": [
            {
                "id": sample["id"],
                "atom_count": sample["atom_count"],
                "pae_size": sample["pae"].get("size"),
                "confidence_semantic": sample["runtime_config"]["confidence_semantic"],
            }
            for sample in delivery_manifest["samples"]
        ],
        "bytes": output_path.stat().st_size,
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
