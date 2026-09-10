# architecture_overview

Market research reports primitive for evidence-traceable report scaffolds, market sizing, forecast sensitivity, competitor matrices, claims ledgers, and source-backed narrative assembly.

This primitive is distilled from the source Agent Skill `market-research-reports`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Python 3.11+ standard library for optional offline CLIs. The optional LaTeX template uses XeLaTeX or LuaLaTeX. Online research requires user-approved network access and source-specific terms; bundled scripts make no network, LLM, or image calls.

# source_knowledge_outline

- Market Research Reports
- Purpose
- Operating principles
- Workflow
- 1. Establish the research contract
- 2. Build the evidence plan
- 3. Create the source ledger
- 4. Maintain a claims ledger
- 5. Size the market as scenarios
- Measurement guardrails

# knowledge_assets

- `references/data_analysis_patterns.md`: Data Analysis Patterns
- `references/evidence_model.md`: Evidence Model
- `references/methods_and_ethics.md`: Methods And Ethics
- `references/official_data_sources.md`: Official Data Sources
- `references/report_structure_guide.md`: Report Structure Guide
- `references/sources.md`: Sources
- `references/visual_generation_guide.md`: Visual Generation Guide

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/_common.py` (source_script):  Common
- `source_payload/scripts/audit_claim_citations.py` (source_script): Audit Claim Citations
- `source_payload/scripts/calculate_market_sizing.py` (source_script): Calculate Market Sizing
- `source_payload/scripts/check_unit_consistency.py` (source_script): Check Unit Consistency
- `source_payload/scripts/forecast_sensitivity.py` (source_script): Forecast Sensitivity
- `source_payload/scripts/generate_report_scaffold.py` (source_script): Generate Report Scaffold
- `source_payload/scripts/validate_competitor_matrix.py` (source_script): Validate Competitor Matrix
- `source_payload/scripts/validate_evidence_ledger.py` (source_script): Validate Evidence Ledger
- `source_payload/assets/claims_ledger_template.csv` (source_asset): Claims Ledger Template
- `source_payload/assets/competitor_feature_matrix_template.csv` (source_asset): Competitor Feature Matrix Template
- `source_payload/assets/consistency_check_template.csv` (source_asset): Consistency Check Template
- `source_payload/assets/forecast_sensitivity_template.json` (source_asset): Forecast Sensitivity Template
- `source_payload/assets/FORMATTING_GUIDE.md` (source_asset): Formatting Guide
- `source_payload/assets/market_report_template.tex` (source_asset): Market Report Template
- `source_payload/assets/market_research.sty` (source_asset): Market Research
- `source_payload/assets/market_sizing_scenarios_template.json` (source_asset): Market Sizing Scenarios Template
- `source_payload/assets/report_manifest_template.json` (source_asset): Report Manifest Template
- `source_payload/assets/source_ledger_template.csv` (source_asset): Source Ledger Template

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=7, scripts=8, assets=10. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/market-research-reports`.
