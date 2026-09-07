# Primitive Code Migration Batch - 2026-09-07

## Batch Summary

This batch materialized 5 additional source skills into OneScience primitives:

| Source skill | Primitive | Domain / category | Knowledge assets |
| --- | --- | --- | ---: |
| `qiskit` | `general.tools.qiskit` | `general/tools` | 11 |
| `neurokit2` | `bio.tools.neurokit2` | `bio/tools` | 12 |
| `pylabrobot` | `general.tools.pylabrobot` | `general/tools` | 6 |
| `opentrons-integration` | `general.tools.opentrons_integration` | `general/tools` | 7 |
| `scikit-learn` | `general.tools.scikit_learn` | `general/tools` | 8 |

All five primitives now carry the four core files plus `references/`, and their `knowledge_assets` entries match the copied reference count.

## Current Inventory Snapshot

- Source skills with `SKILL.md`: 163
- Target primitive metadata files: 277
- Explicit provenance matches: 53
- Heuristic matches: 2
- Uncovered source skills: 108

## Code Migration Distribution

- `resource_only`: 85
- `resource_with_execution_assets`: 58
- `propose_executor`: 20

## Shape Distribution

- `single_primitive`: 93
- `split_primitives`: 52
- `primitive_plus_executor`: 18

## Notes

- The distillation pipeline now supports reusable JSON plan files and a batch driver.
- This batch was generated from the plan file at `skills/onescience-primitive-distiller/assets/next_batch_2026-09-07.json`.
- The inventory snapshot was refreshed after materialization, so the counts above reflect the new primitives.
