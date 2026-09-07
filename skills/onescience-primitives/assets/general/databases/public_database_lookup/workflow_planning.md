# when_to_use

Use this primitive when the task asks for reproducible facts or datasets from named public databases and APIs.

# when_not_to_use

- Use web search only for exploratory discovery, not reproducible database-backed retrieval.
- Use a domain-specific database primitive when one exists for the selected database.
- Use local file analysis primitives when the data are already available locally.

# planning_steps

1. Define target entity, identifiers, fields, scope, and completeness need.
2. Select authoritative source and endpoint family.
3. Plan identifier conversions, filters, rate limits, and pagination.
4. Retrieve in bounded batches and reconcile counts.
5. Report provenance and limitations with the result.

# fallback

- If a database requires credentials, use anonymous or free alternatives when acceptable.
- If an identifier fails, try documented conversion routes.
- If counts disagree, stop and report incompleteness before drawing conclusions.

# handoff_notes

Include source database, endpoint, parameters, identifier conversions, access date, pagination state, local filters, and warnings.
