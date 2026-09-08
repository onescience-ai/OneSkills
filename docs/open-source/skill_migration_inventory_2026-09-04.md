# Skill Migration Inventory

Generated: `2026-09-04`

This inventory is read-only. It does not execute or copy source code.

## Summary

- Source skills with `SKILL.md`: 163
- Target primitive metadata files: 272
- Explicit provenance matches: 48
- Heuristic matches: 2
- Uncovered source skills: 113
- Target metadata requiring regex fallback: 0

## Highest-Priority Candidates

| Skill | Coverage | Shape | Code recommendation | Score |
| --- | --- | --- | --- | ---: |
| `clinical-reports` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 85 |
| `clinical-decision-support` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 84 |
| `neurokit2` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 83 |
| `qiskit` | `uncovered` | `split_primitives` | `propose_executor` | 83 |
| `exploratory-data-analysis` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 82 |
| `matlab` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 82 |
| `treatment-plans` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 82 |
| `pkpd-modeling` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 81 |
| `simpy` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 81 |
| `iso-standards-readiness` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 80 |
| `peer-review` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 80 |
| `hypothesis-generation` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 79 |
| `opentrons-integration` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 79 |
| `pylabrobot` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 79 |
| `pathml` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 78 |
| `pptx-posters` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 78 |
| `scientific-slides` | `uncovered` | `split_primitives` | `resource_only` | 78 |
| `neuropixels-analysis` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 77 |
| `latchbio-integration` | `uncovered` | `primitive_plus_executor` | `propose_executor` | 76 |
| `market-research-reports` | `uncovered` | `split_primitives` | `resource_only` | 76 |
| `paper-lookup` | `uncovered` | `split_primitives` | `resource_only` | 76 |
| `pytdc` | `uncovered` | `single_primitive` | `resource_with_execution_assets` | 76 |
| `pytorch-lightning` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 76 |
| `scikit-learn` | `uncovered` | `primitive_plus_executor` | `propose_executor` | 76 |
| `analytical-method-validation` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 75 |
| `gtars` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 75 |
| `omero-integration` | `uncovered` | `single_primitive` | `resource_only` | 75 |
| `pufferlib` | `uncovered` | `split_primitives` | `resource_only` | 75 |
| `scientific-brainstorming` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 75 |
| `shap` | `uncovered` | `primitive_plus_executor` | `propose_executor` | 75 |

## Interpretation

- `explicit_provenance` is auditable integration through `source.distilled_from`.
- `heuristic_*` is a candidate relationship and requires manual review.
- `resource_with_execution_assets` means code may be selectively promoted after allowlist, hash, dependency, and boundary review.
- `propose_executor` is only a candidate; it still requires isolated execution and acceptance evidence.
- `split_primitives` indicates that one source skill appears to contain multiple reusable concerns.
