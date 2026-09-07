# architecture_overview

Citation management is a metadata retrieval and validation primitive. It separates discovery, identifier resolution, enrichment, formatting, deduplication, and final verification.

# input_schema

Typical inputs are search terms or identifiers, source databases, metadata fields, citation style, venue rules, and manuscript or bibliography context.

# output_schema

Expected outputs include normalized citation records, BibTeX or formatted references, duplicate reports, missing-field warnings, and verification provenance.

# key_dependencies

- OpenAlex
- PubMed
- Crossref
- arXiv or DataCite when relevant
- requests or a documented HTTP client

# common_modification_points

- primary metadata source
- identifier conversion route
- missing-field enrichment
- citation key scheme
- duplicate and preprint handling
- venue formatting rules

# implementation_risks

- API metadata is not automatically verified against the publication.
- A preprint may have a published version with different metadata.
- Missing volume, pages, DOI, or authors can break downstream bibliography quality.
- Search snippets are discovery evidence, not final citation verification.

# provenance

Distilled from `scientific-agent-skills/skills/citation-management` version `2.0`. Scripts and templates were not copied.
