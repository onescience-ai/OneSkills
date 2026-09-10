# architecture_overview

Public database lookup primitive for scholarly literature search, citation discovery, DOI and PMID resolution, open-access retrieval, and provenance-traceable result aggregation across academic APIs.

This primitive is distilled from the source Agent Skill `paper-lookup`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Needs network access and curl. The bundled scripts require Python 3.11+ and use only the standard library. No credentials are required; NCBI_API_KEY, S2_API_KEY, CORE_API_KEY, and OPENALEX_API_KEY raise rate limits or unlock full text where noted.

# source_knowledge_outline

- Paper Lookup
- Core Workflow
- Database Selection Guide
- By Use Case
- Cross-Database Queries
- Common Identifier Formats
- API Keys and Access
- Making API Calls
- Request guidelines
- Error recovery

# knowledge_assets

- `references/arxiv.md`: Arxiv
- `references/biorxiv.md`: Biorxiv
- `references/core.md`: Core
- `references/crossref.md`: Crossref
- `references/europepmc.md`: Europepmc
- `references/medrxiv.md`: Medrxiv
- `references/openalex.md`: Openalex
- `references/pmc.md`: Pmc
- `references/pubmed.md`: Pubmed
- `references/semantic-scholar.md`: Semantic Scholar
- `references/unpaywall.md`: Unpaywall

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/_common.py` (source_script):  Common
- `source_payload/scripts/arxiv_atom.py` (source_script): Arxiv Atom
- `source_payload/scripts/jats_to_text.py` (source_script): Jats To Text
- `source_payload/scripts/openalex_abstract.py` (source_script): Openalex Abstract
- `source_payload/scripts/paginate.py` (source_script): Paginate

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=11, scripts=5, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/paper-lookup`.
