# architecture_overview

Public database lookup is a retrieval-planning primitive for documented APIs. It represents endpoint, filter, pagination, provenance, and safety constraints, not a single database implementation.

# input_schema

Typical inputs are target entity, identifiers, accepted identifier formats, organism or domain constraints, date/build constraints, filters, desired fields, and exhaustiveness requirements.

# output_schema

Expected outputs include retrieved records or summaries, endpoints, parameters, access dates, identifier conversions, pagination counts, local filters, and warnings.

# key_dependencies

- network access
- API-specific client, HTTP fetch tool, or shell curl
- optional API keys for selected services
- JSON or tabular parser for response handling

# common_modification_points

- authoritative source selection
- identifier conversion path
- server-side vs local filtering
- pagination and count reconciliation
- rate-limit strategy
- raw vs summarized output

# implementation_risks

- API responses may include untrusted third-party text.
- Pagination omissions can produce incomplete datasets.
- Identifier ambiguity can change downstream conclusions.
- Credentials must never appear in provenance or output.

# provenance

Distilled from `scientific-agent-skills/skills/database-lookup` version `1.3`. Reference files were not copied.
