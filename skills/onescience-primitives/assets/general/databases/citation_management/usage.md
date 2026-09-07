# typical_workflow

1. Search at least one broad and one domain-authoritative source.
2. Resolve DOI, PMID, arXiv, or title identifiers.
3. Enrich missing metadata before formatting.
4. Deduplicate and normalize citation keys.
5. Validate references against the source and target venue.

# usage_notes

- Prefer OpenAlex or PubMed for discovery and Crossref for DOI metadata.
- Treat Google Scholar as a supplement because it is scrape-based and rate-limited.
- Preserve the source and access date for each record.
- Do not present unverified metadata as final bibliographic truth.
