# architecture_overview

The Census is a versioned public atlas corpus, not a local single-cell analysis package. This primitive captures query patterns, version pinning, and downstream handoff boundaries.

# input_schema

Typical inputs are organism names, obs and var filters, dataset or tissue selectors, Census versions, and optional spatial or embedding requirements.

# output_schema

Expected outputs include metadata frames, AnnData slices, presence matrices, source H5AD URIs, and query summaries.

# key_dependencies

- cellxgene-census
- tiledbsoma or tiledbsoma-ml when large or ML workflows are needed
- anndata for returned slices
- Scanpy for downstream analysis
- optional spatial extras for spatial Census access

# common_modification_points

- census_version pinning
- is_primary_data filtering
- obs and var column selection
- organism and tissue granularity
- query size limits and out-of-core processing
- downstream AnnData handoff strategy

# implementation_risks

- Unpinned Census versions can drift between runs.
- Missing is_primary_data can double-count cells.
- Overly broad queries can exhaust memory.
- The primitive is for public Census access only; private datasets need different resources.

# provenance

Distilled from `scientific-agent-skills/skills/cellxgene-census` version `1.2`. Execution scripts were not copied.
