# Primitive Code Migration Batch - 2026-09-08d

## Batch Summary

This batch materialized 5 additional source skills into OneScience primitives:

| Source skill | Primitive | Domain / category | Knowledge assets | Source payloads |
| --- | --- | --- | ---: | ---: |
| `scientific-brainstorming` | `general.workflow-planning.scientific_brainstorming` | `general/workflow-planning` | 5 | 4 |
| `market-research-reports` | `general.application.market_research_reports` | `general/application` | 7 | 18 |
| `pufferlib` | `general.tools.pufferlib` | `general/tools` | 5 | 9 |
| `pymc` | `general.tools.pymc` | `general/tools` | 5 | 4 |
| `stable-baselines3` | `general.tools.stable_baselines3` | `general/tools` | 4 | 3 |

All five primitives now carry the four core files plus copied `references/` and inert `source_payload/` copies of source scripts/templates. Source payloads are indexed in `metadata.json.source_payloads` and remain non-executable until explicitly promoted.

## Current Inventory Snapshot

- Source skills with `SKILL.md`: 163
- Target primitive metadata files: 300
- Explicit provenance matches: 83
- Heuristic matches: 3
- Uncovered source skills: 77

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