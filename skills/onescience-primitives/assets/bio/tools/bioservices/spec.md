# architecture_overview

bioservices primitive for unified querying of multiple bioinformatics web services including UniProt, KEGG, ChEMBL, and Reactome with consistent API handling.

This primitive is distilled from the source Agent Skill `bioservices`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.9–3.12 and internet access to 40+ bioinformatics web APIs. NCBI BLAST requires a contact email (`NCBI_EMAIL` env var or explicit parameter).

# source_knowledge_outline

- BioServices
- Overview
- When to Use This Skill
- Core Capabilities
- 1. Protein Analysis
- Search for protein by name
- Retrieve FASTA sequence
- Map identifiers between databases
- 2. Pathway Discovery and Analysis
- Search for organisms

# knowledge_assets

- `references/identifier_mapping.md`: Identifier Mapping
- `references/services_reference.md`: Services Reference
- `references/workflow_patterns.md`: Workflow Patterns

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/batch_id_converter.py` (source_script): Batch Id Converter
- `source_payload/scripts/compound_cross_reference.py` (source_script): Compound Cross Reference
- `source_payload/scripts/pathway_analysis.py` (source_script): Pathway Analysis
- `source_payload/scripts/protein_analysis_workflow.py` (source_script): Protein Analysis Workflow

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=3, scripts=4, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/bioservices`.
