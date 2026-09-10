# Primitive Code Migration Batch - 2026-09-08e

## Batch Summary

This batch materialized 4 additional source skills into OneScience primitives:

| Source skill | Primitive | Domain / category | Knowledge assets | Source payloads |
| --- | --- | --- | ---: | ---: |
| `latchbio-integration` | `bio.application.latchbio_integration` | `bio/application` | 9 | 1 |
| `shap` | `general.tools.shap` | `general/tools` | 8 | 1 |
| `etetoolkit` | `bio.tools.etetoolkit` | `bio/tools` | 5 | 2 |
| `flowio` | `bio.tools.flowio` | `bio/tools` | 5 | 1 |

All four primitives now carry the four core files plus copied `references/` and inert `source_payload/` copies of source scripts. Source payloads are indexed in `metadata.json.source_payloads` and remain non-executable until explicitly promoted.

## Current Inventory Snapshot

- Source skills with `SKILL.md`: 163
- Target primitive metadata files: 304
- Explicit provenance matches: 87
- Heuristic matches: 3
- Uncovered source skills: 73

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
- The new `source_payload` layer keeps source scripts available for later executor design without turning them into execution assets now.
