# Primitive Code Migration Batch - 2026-09-08f

## Batch Summary

This batch materialized 4 additional source skills into OneScience primitives:

| Source skill | Primitive | Domain / category | Knowledge assets | Source payloads |
| --- | --- | --- | ---: | ---: |
| `dnanexus-integration` | `bio.application.dnanexus_integration` | `bio/application` | 9 | 2 |
| `markitdown` | `general.output-format.markitdown` | `general/output-format` | 7 | 3 |
| `arboreto` | `bio.tools.arboreto` | `bio/tools` | 3 | 1 |
| `timesfm-forecasting` | `general.tools.timesfm_forecasting` | `general/tools` | 7 | 2 |

All four primitives now carry the four core files plus copied `references/` and inert `source_payload/` copies of source scripts. Source payloads are indexed in `metadata.json.source_payloads` and remain non-executable until explicitly promoted.

## Current Inventory Snapshot

- Source skills with `SKILL.md`: 163
- Target primitive metadata files: 308
- Explicit provenance matches: 91
- Heuristic matches: 3
- Uncovered source skills: 69

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
