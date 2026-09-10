#!/usr/bin/env python3
"""Materialize selected scientific-agent-skills as OneScience primitives.

This helper is intentionally conservative: it copies read-only knowledge files,
optionally preserves source scripts/templates as inert payloads, and writes
primitive metadata/contracts. It never executes source skill code and does not
promote scripts into execution assets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TARGET_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_ASSETS_ROOT = DEFAULT_TARGET_ROOT / "skills" / "onescience-primitives" / "assets"

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
LIST_ITEM_RE = re.compile(r"^\s*[-*]\s+(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class PrimitivePlan:
    skill: str
    domain: str
    category: str
    name: str
    primitive_id: str
    type_: str
    description: str
    tags: tuple[str, ...]


def slug_to_name(value: str) -> str:
    return value.replace("-", "_")


def primitive_type_for(category: str) -> str:
    return {
        "application": "application",
        "components": "component",
        "contracts": "contract",
        "databases": "database",
        "datapipes": "datapipe",
        "datasets": "dataset",
        "models": "model",
        "output-format": "output-format",
        "services": "service",
        "tools": "tool",
        "visualization": "visualization",
        "workflow-planning": "workflow-planning",
    }.get(category, category.rstrip("s") or "primitive")


PLANS: tuple[PrimitivePlan, ...] = (
    PrimitivePlan(
        "rdkit",
        "matchem",
        "tools",
        "rdkit",
        "matchem.tools.rdkit",
        "tool",
        "RDKit cheminformatics primitive for molecules, reactions, descriptors, fingerprints, conformers, and structure-based chemistry workflows.",
        ("rdkit", "cheminformatics", "molecules", "descriptors", "fingerprints"),
    ),
    PrimitivePlan(
        "pymatgen",
        "matchem",
        "tools",
        "pymatgen",
        "matchem.tools.pymatgen",
        "tool",
        "Pymatgen materials-science primitive for crystal structures, compositions, transformations, phase diagrams, and VASP-oriented workflows.",
        ("pymatgen", "materials", "crystal-structure", "vasp", "phase-diagram"),
    ),
    PrimitivePlan(
        "molecular-dynamics",
        "matchem",
        "workflow-planning",
        "molecular_dynamics",
        "matchem.workflow-planning.molecular_dynamics",
        "workflow-planning",
        "Molecular dynamics planning primitive for force-field selection, system preparation, equilibration, production, analysis, and reproducibility checks.",
        ("molecular-dynamics", "md", "simulation", "force-field", "trajectory"),
    ),
    PrimitivePlan(
        "datamol",
        "matchem",
        "tools",
        "datamol",
        "matchem.tools.datamol",
        "tool",
        "Datamol cheminformatics utility primitive for molecule standardization, scaffold handling, descriptors, clustering, and dataset preparation.",
        ("datamol", "cheminformatics", "standardization", "scaffolds", "molecules"),
    ),
    PrimitivePlan(
        "deepchem",
        "matchem",
        "tools",
        "deepchem",
        "matchem.tools.deepchem",
        "tool",
        "DeepChem primitive for molecular machine learning datasets, featurization, model training, evaluation, and uncertainty-aware chemical prediction.",
        ("deepchem", "molecular-ml", "featurization", "toxicity", "QSAR"),
    ),
    PrimitivePlan(
        "molfeat",
        "matchem",
        "tools",
        "molfeat",
        "matchem.tools.molfeat",
        "tool",
        "Molfeat primitive for molecular featurization, fingerprints, embeddings, and chemical machine-learning feature pipelines.",
        ("molfeat", "molecular-features", "fingerprints", "embeddings", "QSAR"),
    ),
    PrimitivePlan(
        "matchms",
        "matchem",
        "tools",
        "matchms",
        "matchem.tools.matchms",
        "tool",
        "MatchMS primitive for mass-spectrometry spectrum processing, metadata cleaning, similarity scoring, and metabolomics library matching.",
        ("matchms", "mass-spectrometry", "metabolomics", "spectra", "similarity"),
    ),
    PrimitivePlan(
        "openpiv",
        "cfd",
        "tools",
        "openpiv",
        "cfd.tools.openpiv",
        "tool",
        "OpenPIV primitive for particle image velocimetry workflows, velocity-field extraction, validation, scaling, and visualization planning.",
        ("openpiv", "piv", "velocity-field", "fluid", "image-analysis"),
    ),
    PrimitivePlan(
        "fluidsim",
        "cfd",
        "tools",
        "fluidsim",
        "cfd.tools.fluidsim",
        "tool",
        "FluidSim primitive for fluid simulation setup, solver selection, parameter planning, diagnostics, and reproducible run organization.",
        ("fluidsim", "cfd", "fluid-simulation", "solver", "diagnostics"),
    ),
    PrimitivePlan(
        "bulk-rnaseq",
        "bio",
        "workflow-planning",
        "bulk_rnaseq",
        "bio.workflow-planning.bulk_rnaseq",
        "workflow-planning",
        "Bulk RNA-seq workflow primitive for count matrices, metadata, QC, differential expression, enrichment, and reporting.",
        ("bulk-rnaseq", "rna-seq", "differential-expression", "counts", "qc"),
    ),
    PrimitivePlan(
        "biopython",
        "bio",
        "tools",
        "biopython",
        "bio.tools.biopython",
        "tool",
        "Biopython primitive for biological sequences, records, annotations, file formats, Entrez-style retrieval planning, and phylogenetic utilities.",
        ("biopython", "sequence-analysis", "fasta", "genbank", "phylogenetics"),
    ),
    PrimitivePlan(
        "pysam",
        "bio",
        "tools",
        "pysam",
        "bio.tools.pysam",
        "tool",
        "Pysam primitive for SAM/BAM/CRAM/VCF access, read filtering, pileups, coverage summaries, and genomic interval workflows.",
        ("pysam", "sam", "bam", "cram", "vcf", "coverage"),
    ),
    PrimitivePlan(
        "genomic-coordinates",
        "bio",
        "datapipes",
        "genomic_coordinates",
        "bio.datapipes.genomic_coordinates",
        "datapipe",
        "Genomic coordinate primitive for intervals, genome builds, BED-like data, coordinate validation, liftover planning, and overlap semantics.",
        ("genomic-coordinates", "bed", "intervals", "genome-build", "liftover"),
    ),
    PrimitivePlan(
        "pathway-enrichment",
        "bio",
        "tools",
        "pathway_enrichment",
        "bio.tools.pathway_enrichment",
        "tool",
        "Pathway enrichment primitive for gene-set selection, ID mapping, over-representation, rank-based enrichment, and interpretation caveats.",
        ("pathway-enrichment", "gene-sets", "gsea", "ora", "id-mapping"),
    ),
    PrimitivePlan(
        "geopandas",
        "general",
        "tools",
        "geopandas",
        "general.tools.geopandas",
        "tool",
        "GeoPandas primitive for geospatial tabular data, CRS handling, spatial joins, overlays, geometry validation, and map-ready outputs.",
        ("geopandas", "geospatial", "crs", "spatial-join", "geometry"),
    ),
    PrimitivePlan(
        "astropy",
        "general",
        "tools",
        "astropy",
        "general.tools.astropy",
        "tool",
        "Astropy primitive for astronomy tables, units, coordinates, FITS files, time handling, and observation-data workflows.",
        ("astropy", "astronomy", "fits", "coordinates", "units"),
    ),
    PrimitivePlan(
        "sympy",
        "general",
        "tools",
        "sympy",
        "general.tools.sympy",
        "tool",
        "SymPy primitive for symbolic mathematics, algebra, calculus, equation solving, code generation, and exact analytical derivations.",
        ("sympy", "symbolic-math", "algebra", "calculus", "equations"),
    ),
    PrimitivePlan(
        "networkx",
        "general",
        "tools",
        "networkx",
        "general.tools.networkx",
        "tool",
        "NetworkX primitive for graph construction, graph algorithms, network metrics, traversal, and reproducible graph-analysis workflows.",
        ("networkx", "graphs", "networks", "algorithms", "centrality"),
    ),
    PrimitivePlan(
        "pyopenms",
        "bio",
        "tools",
        "pyopenms",
        "bio.tools.pyopenms",
        "tool",
        "pyOpenMS mass-spectrometry primitive for feature finding, alignment, identification, quantification, and proteomics workflow planning.",
        ("pyopenms", "mass-spectrometry", "proteomics", "feature-finding", "quantification"),
    ),
    PrimitivePlan(
        "geniml",
        "bio",
        "tools",
        "geniml",
        "bio.tools.geniml",
        "tool",
        "Geniml primitive for genomic language models, BED/region workflows, consensus universes, embeddings, and tokenization planning.",
        ("geniml", "genomics", "language-models", "embeddings", "bed"),
    ),
    PrimitivePlan(
        "cobrapy",
        "bio",
        "tools",
        "cobrapy",
        "bio.tools.cobrapy",
        "tool",
        "COBRApy primitive for constraint-based metabolic modeling, flux balance analysis, reaction rules, and growth-media workflows.",
        ("cobrapy", "metabolic-modeling", "fba", "flux-analysis", "gpr"),
    ),
    PrimitivePlan(
        "tiledbvcf",
        "bio",
        "datapipes",
        "tiledbvcf",
        "bio.datapipes.tiledbvcf",
        "datapipe",
        "TileDB-VCF primitive for variant storage, region queries, population-genomics access, and cloud-backed genomics data workflows.",
        ("tiledbvcf", "vcf", "genomics", "variant-query", "population-genomics"),
    ),
    PrimitivePlan(
        "pydicom",
        "general",
        "tools",
        "pydicom",
        "general.tools.pydicom",
        "tool",
        "pydicom primitive for DICOM inspection, metadata extraction, pixel-data planning, de-identification, and medical-imaging workflows.",
        ("pydicom", "dicom", "medical-imaging", "metadata", "de-identification"),
    ),
    PrimitivePlan(
        "pymoo",
        "general",
        "tools",
        "pymoo",
        "general.tools.pymoo",
        "tool",
        "Pymoo primitive for single-, multi-, and many-objective optimization, constraint handling, and algorithm selection planning.",
        ("pymoo", "optimization", "multi-objective", "pareto", "evolutionary-algorithms"),
    ),
    PrimitivePlan(
        "qutip",
        "general",
        "tools",
        "qutip",
        "general.tools.qutip",
        "tool",
        "QuTiP primitive for quantum object construction, open-system dynamics, steady states, spectra, and solver planning.",
        ("qutip", "quantum", "dynamics", "solver", "open-systems"),
    ),
    PrimitivePlan(
        "scikit-survival",
        "general",
        "tools",
        "scikit_survival",
        "general.tools.scikit_survival",
        "tool",
        "scikit-survival primitive for censored-data analysis, survival modeling, competing risks, and reproducible evaluation planning.",
        ("scikit-survival", "survival-analysis", "censored-data", "competing-risks", "evaluation"),
    ),
    PrimitivePlan(
        "lab-hardware-cad",
        "general",
        "tools",
        "lab_hardware_cad",
        "general.tools.lab_hardware_cad",
        "tool",
        "Lab hardware CAD primitive for fixture design, fabrication planning, parameterized geometry, and inspection-driven iteration.",
        ("lab-hardware-cad", "cad", "lab-hardware", "fabrication", "geometry"),
    ),
    PrimitivePlan(
        "torchdrug",
        "general",
        "tools",
        "torchdrug",
        "general.tools.torchdrug",
        "tool",
        "TorchDrug primitive for molecular deep learning, graph learning, pretraining, generation, and knowledge-graph tasks.",
        ("torchdrug", "molecular-ml", "graph-learning", "generation", "pretraining"),
    ),
    PrimitivePlan(
        "torch-geometric",
        "general",
        "tools",
        "torch_geometric",
        "general.tools.torch_geometric",
        "tool",
        "PyTorch Geometric primitive for graph data, heterogeneous graphs, GNN layers, and graph-learning workflows.",
        ("torch-geometric", "graph-neural-networks", "graphs", "heterogeneous-graphs", "gnn"),
    ),
)


def parse_frontmatter(skill_md: Path) -> tuple[dict[str, Any], str]:
    text = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    metadata: dict[str, Any] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("\"'")
    metadata["_frontmatter_text"] = match.group(1)
    return metadata, match.group(2)


def extract_source_version(frontmatter_text: str | None) -> str:
    if not frontmatter_text:
        return "unknown"
    match = re.search(r"(?m)^\s*version:\s*[\"']?([^\"'\n]+)", frontmatter_text)
    if match:
        return match.group(1).strip()
    return "unknown"


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def clean_title(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ").title()


def extract_headings(body: str, limit: int = 10) -> list[str]:
    headings = [item.strip("` ") for item in HEADING_RE.findall(body)]
    return headings[:limit]


def extract_list_items(body: str, limit: int = 6) -> list[str]:
    items: list[str] = []
    for raw in LIST_ITEM_RE.findall(body):
        text = re.sub(r"`([^`]+)`", r"\1", raw)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\s+", " ", text).strip()
        if 25 <= len(text) <= 180 and text not in items:
            items.append(text)
        if len(items) >= limit:
            break
    return items


def copy_references(skill_root: Path, primitive_root: Path) -> list[dict[str, Any]]:
    source_refs = skill_root / "references"
    if not source_refs.exists():
        return []
    target_refs = primitive_root / "references"
    target_refs.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for source in sorted(path for path in source_refs.rglob("*") if path.is_file()):
        relative_source = source.relative_to(source_refs)
        if any(part.startswith(".") for part in relative_source.parts):
            continue
        target = target_refs / relative_source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        relative_target = target.relative_to(primitive_root).as_posix()
        records.append(
            {
                "path": relative_target,
                "title": clean_title(source),
                "purpose": f"Extended source guidance for {clean_title(source).lower()}.",
                "source": f"scientific-agent-skills/skills/{skill_root.name}/references/{relative_source.as_posix()}",
                "sha256": sha256_file(target),
                "media_type": media_type_for(target),
                "status": "available",
            }
        )
    return records


def copy_source_payloads(skill_root: Path, primitive_root: Path) -> list[dict[str, Any]]:
    payload_root = primitive_root / "source_payload"
    records: list[dict[str, Any]] = []
    for folder in ("scripts", "assets"):
        source_base = skill_root / folder
        if not source_base.exists():
            continue
        target_base = payload_root / folder
        target_base.mkdir(parents=True, exist_ok=True)
        for source in sorted(path for path in source_base.rglob("*") if path.is_file()):
            relative_source = source.relative_to(source_base)
            if source.is_symlink() or any(part.startswith(".") for part in relative_source.parts):
                continue
            target = target_base / relative_source
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            relative_target = target.relative_to(primitive_root).as_posix()
            records.append(
                {
                    "path": relative_target,
                    "kind": "source_script" if folder == "scripts" else "source_asset",
                    "title": clean_title(source),
                    "purpose": (
                        "Preserved source script for later contract review and possible executor promotion."
                        if folder == "scripts"
                        else "Preserved source asset or template for later primitive binding review."
                    ),
                    "source": f"scientific-agent-skills/skills/{skill_root.name}/{folder}/{relative_source.as_posix()}",
                    "sha256": sha256_file(target),
                    "media_type": media_type_for(target),
                    "status": "preserved",
                    "execution_status": "not_whitelisted",
                }
            )
    return records


def media_type_for(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".json": "application/json",
        ".yaml": "application/yaml",
        ".yml": "application/yaml",
        ".csv": "text/csv",
        ".tsv": "text/tab-separated-values",
        ".py": "text/x-python",
        ".sh": "text/x-shellscript",
        ".tex": "application/x-tex",
        ".bst": "application/x-bibtex-style",
        ".html": "text/html",
    }.get(suffix, "application/octet-stream")


def source_file_counts(skill_root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for folder in ("references", "scripts", "assets"):
        base = skill_root / folder
        counts[folder] = (
            sum(1 for path in base.rglob("*") if path.is_file())
            if base.exists()
            else 0
        )
    return counts


def plan_description(plan: PrimitivePlan, source_frontmatter: dict[str, Any]) -> str:
    return plan.description or source_frontmatter.get("description") or (
        f"Source-grounded primitive distilled from `{plan.skill}`."
    )


def write_json(path: Path, document: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def build_metadata(
    plan: PrimitivePlan,
    source_frontmatter: dict[str, Any],
    knowledge_assets: list[dict[str, Any]],
    source_payloads: list[dict[str, Any]],
    counts: dict[str, int],
    *,
    copied_knowledge_references: bool,
    copied_source_payloads: bool,
) -> dict[str, Any]:
    version = "1.0.0"
    source_version = extract_source_version(source_frontmatter.get("_frontmatter_text"))
    description = plan_description(plan, source_frontmatter)
    return {
        "name": plan.name,
        "primitive_id": plan.primitive_id,
        "type": plan.type_,
        "domain": plan.domain,
        "category": plan.category,
        "version": version,
        "visibility": "public",
        "created_at": str(date.today()),
        "updated_at": str(date.today()),
        "provider_kind": "distilled_agent_skill",
        "provider_name": "scientific-agent-skills",
        "source": {
            "distilled_from": f"scientific-agent-skills/skills/{plan.skill}",
            "distilled_from_version": source_version,
            "distillation_status": "resource_only",
            "copied_knowledge_references": copied_knowledge_references,
            "copied_source_payloads": copied_source_payloads,
            "copied_execution_assets": False,
            "source_file_counts": counts,
        },
        "knowledge_assets": knowledge_assets,
        "source_payloads": source_payloads,
        "description": description,
        "tags": list(plan.tags),
        "capabilities": [
            f"Recall source-grounded workflow and API guidance for {plan.skill}.",
            "Expose detailed reference material through knowledge_assets with SHA-256 verification.",
            "Preserve source scripts and templates as non-executable payloads when requested by the distillation plan.",
            "Route execution to a reviewed domain executor or future execution asset when computation is required.",
        ],
        "requirements": [
            "Task-specific scientific inputs, data paths, target environment, and version constraints.",
            "Domain package installation and credentials only when a downstream executor actually runs code.",
            "Manual review of scientific assumptions, provenance, and output validity.",
        ],
        "contracts": {
            "resource_output": "resource_retrieval_result",
            "source_payload_policy": "metadata_indexed_inert_copy",
            "execution_asset_policy": "none",
        },
    }


def build_spec(
    plan: PrimitivePlan,
    source_frontmatter: dict[str, Any],
    body: str,
    knowledge_assets: list[dict[str, Any]],
    source_payloads: list[dict[str, Any]],
    counts: dict[str, int],
) -> str:
    headings = extract_headings(body)
    compatibility = source_frontmatter.get("compatibility", "")
    description = plan_description(plan, source_frontmatter)
    heading_lines = "\n".join(f"- {heading}" for heading in headings) or "- Source skill has no parsed headings."
    asset_lines = "\n".join(
        f"- `{asset['path']}`: {asset['title']}" for asset in knowledge_assets
    ) or "- No reference files were bundled in the source skill."
    payload_lines = "\n".join(
        f"- `{payload['path']}` ({payload['kind']}): {payload['title']}"
        for payload in source_payloads
    ) or "- No source scripts or non-reference assets were copied in this batch."
    return f"""# architecture_overview

{description}

This primitive is distilled from the source Agent Skill `{plan.skill}`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

{compatibility or 'See the migrated references and the source skill for package-specific dependencies. Install dependencies only in the execution environment that needs them.'}

# source_knowledge_outline

{heading_lines}

# knowledge_assets

{asset_lines}

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

{payload_lines}

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references={counts['references']}, scripts={counts['scripts']}, assets={counts['assets']}. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/{plan.skill}`.
"""


def build_usage(plan: PrimitivePlan, body: str) -> str:
    examples = extract_list_items(body)
    example_lines = "\n".join(f"- {item}" for item in examples) or "- Use the source references when detailed package workflow guidance is needed."
    return f"""# typical_workflow

1. Match the task to `{plan.primitive_id}` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

{example_lines}

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.

If `metadata.json.source_payloads` is present, treat those files as preserved migration material only. They can inform future executor design, but they must not be run or imported until promoted through an explicit execution-asset whitelist.
"""


def build_workflow(plan: PrimitivePlan) -> str:
    return f"""# when_to_use

Use this primitive when the task explicitly involves `{plan.skill}`, its scientific workflow, or its associated artifacts and data structures.

# when_not_to_use

- Use a more specific existing OneScience primitive when the task is already routed to a narrower model, component, dataset, or visualization primitive.
- Use an executor only when actual computation is required and the runtime dependencies are available.
- Do not use this primitive to bypass domain validation, credentials, or package installation requirements.

# planning_steps

1. Identify the scientific object, data type, package version, and intended result.
2. Retrieve the most relevant migrated reference files.
3. Extract required inputs, assumptions, parameters, and validation checks.
4. Decide whether the task can be answered as planning guidance or needs execution.
5. Record provenance, limitations, and downstream resource dependencies.

# handoff_notes

Pass `primitive_id: {plan.primitive_id}`, source references used, package/version assumptions, input artifacts, output expectations, and unresolved validation risks to the next workflow step.
"""


def materialize(
    plan: PrimitivePlan,
    source_root: Path,
    assets_root: Path,
    *,
    force: bool,
    copy_knowledge_references: bool,
    copy_source_payloads_enabled: bool,
) -> dict[str, Any]:
    skill_root = source_root / "skills" / plan.skill
    skill_md = skill_root / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"missing source SKILL.md for {plan.skill}: {skill_md}")

    primitive_root = assets_root / plan.domain / plan.category / plan.name
    if primitive_root.exists():
        if not force:
            raise FileExistsError(f"target exists; rerun with --force: {primitive_root}")
        shutil.rmtree(primitive_root)
    primitive_root.mkdir(parents=True, exist_ok=True)

    frontmatter, body = parse_frontmatter(skill_md)
    knowledge_assets = copy_references(skill_root, primitive_root) if copy_knowledge_references else []
    source_payloads = copy_source_payloads(skill_root, primitive_root) if copy_source_payloads_enabled else []
    counts = source_file_counts(skill_root)

    write_json(
        primitive_root / "metadata.json",
        build_metadata(
            plan,
            frontmatter,
            knowledge_assets,
            source_payloads,
            counts,
            copied_knowledge_references=copy_knowledge_references,
            copied_source_payloads=copy_source_payloads_enabled,
        ),
    )
    write_text(primitive_root / "spec.md", build_spec(plan, frontmatter, body, knowledge_assets, source_payloads, counts))
    write_text(primitive_root / "usage.md", build_usage(plan, body))
    write_text(primitive_root / "workflow_planning.md", build_workflow(plan))

    return {
        "skill": plan.skill,
        "primitive_id": plan.primitive_id,
        "path": str(primitive_root.relative_to(assets_root).as_posix()),
        "knowledge_assets": len(knowledge_assets),
        "source_payloads": len(source_payloads),
        "copied_knowledge_references": copy_knowledge_references,
        "copied_source_payloads": copy_source_payloads_enabled,
        "source_file_counts": counts,
    }


def coerce_tags(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(item.strip() for item in value.split(",") if item.strip())
    if isinstance(value, list):
        return tuple(str(item).strip() for item in value if str(item).strip())
    raise SystemExit("plan tags must be a list or comma-separated string")


def primitive_plan_from_mapping(item: dict[str, Any]) -> PrimitivePlan:
    missing = [key for key in ("skill", "domain", "category") if not item.get(key)]
    if missing:
        raise SystemExit(f"plan entry missing required field(s): {', '.join(missing)}")
    skill = str(item["skill"])
    domain = str(item["domain"])
    category = str(item["category"])
    name = str(item.get("name") or item.get("primitive_name") or slug_to_name(skill))
    primitive_id = str(item.get("primitive_id") or f"{domain}.{category}.{name}")
    type_ = str(item.get("type") or item.get("type_") or primitive_type_for(category))
    description = str(item.get("description") or "")
    return PrimitivePlan(
        skill=skill,
        domain=domain,
        category=category,
        name=name,
        primitive_id=primitive_id,
        type_=type_,
        description=description,
        tags=coerce_tags(item.get("tags")),
    )


def load_plan_file(path: Path) -> list[PrimitivePlan]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise SystemExit(f"invalid plan JSON: {path}: {error}") from error
    if isinstance(document, list):
        entries = document
    elif isinstance(document, dict):
        entries = document.get("plans") or document.get("skills")
    else:
        entries = None
    if not isinstance(entries, list):
        raise SystemExit("plan file must be a JSON list or an object with a plans/skills list")
    if not entries:
        raise SystemExit("plan file contains no entries")
    plans: list[PrimitivePlan] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise SystemExit("each plan entry must be a JSON object")
        plans.append(primitive_plan_from_mapping(entry))
    return plans


def select_plans(names: list[str] | None, plan_file: Path | None = None) -> list[PrimitivePlan]:
    available_plans = load_plan_file(plan_file) if plan_file else list(PLANS)
    if not names:
        return available_plans
    by_skill = {plan.skill: plan for plan in available_plans}
    missing = [name for name in names if name not in by_skill]
    if missing:
        raise SystemExit(f"unknown configured skill(s): {', '.join(missing)}")
    return [by_skill[name] for name in names]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--target-root", type=Path, default=DEFAULT_TARGET_ROOT)
    parser.add_argument("--plan-file", type=Path, help="JSON plan file; defaults to the built-in migration plan")
    parser.add_argument("--skill", action="append", help="configured source skill to materialize; repeatable")
    parser.add_argument(
        "--copy-knowledge-references",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="copy source references into primitive knowledge_assets",
    )
    parser.add_argument(
        "--copy-source-payloads",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="copy source scripts/assets into inert source_payload records",
    )
    parser.add_argument("--force", action="store_true", help="overwrite primitive metadata/docs and copied references")
    parser.add_argument("--dry-run", action="store_true", help="print selected plans without writing")
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    assets_root = (args.target_root.resolve() / "skills" / "onescience-primitives" / "assets")
    plans = select_plans(args.skill, args.plan_file)
    if args.dry_run:
        for plan in plans:
            print(f"{plan.skill}\t{plan.primitive_id}\t{plan.domain}/{plan.category}/{plan.name}")
        return 0

    results = [
        materialize(
            plan,
            source_root,
            assets_root,
            force=args.force,
            copy_knowledge_references=args.copy_knowledge_references,
            copy_source_payloads_enabled=args.copy_source_payloads,
        )
        for plan in plans
    ]
    print(json.dumps({"materialized": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
