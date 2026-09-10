# Primitive Code Migration Batch - 2026-09-08c

## Batch Summary

This batch materialized 5 additional source skills into OneScience primitives:

| Source skill | Primitive | Domain / category | Knowledge assets | Source payloads |
| --- | --- | --- | ---: | ---: |
| `paper-lookup` | `general.databases.public_database_lookup` | `general/databases` | 11 | 5 |
| `pytdc` | `bio.tools.pytdc` | `bio/tools` | 4 | 6 |
| `gtars` | `bio.tools.gtars` | `bio/tools` | 6 | 8 |
| `bioservices` | `bio.tools.bioservices` | `bio/tools` | 3 | 4 |
| `omero-integration` | `bio.application.omero_integration` | `bio/application` | 9 | 5 |

All five primitives now carry the four core files plus copied `references/` and inert `source_payload/` copies of source scripts/templates. Source payloads are indexed in `metadata.json.source_payloads` and remain non-executable until explicitly promoted.

## Current Inventory Snapshot

- Source skills with `SKILL.md`: 163
- Target primitive metadata files: 295
- Explicit provenance matches: 78
- Heuristic matches: 3
- Uncovered source skills: 82

## Code Migration Distribution

- `resource_only`: 85
- `resource_with_execution_assets`: 58
- `propose_executor`: 20

## Shape Distribution

- `single_primitive`: 93
- `split_primitives`: 52
- `primitive_plus_executor`: 18

## Notes

- This batch used the reusable batch driver and JSON plan file.
- The inventory snapshot was refreshed after materialization, so the counts above reflect the new primitives.
- The new `source_payload` layer keeps source scripts and static assets available for later executor design without turning them into execution assets now.