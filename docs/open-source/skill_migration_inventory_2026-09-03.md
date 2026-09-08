# Skill Migration Inventory

Generated: `2026-09-03`

This inventory is read-only. It does not execute or copy source code.

## Summary

- Source skills with `SKILL.md`: 163
- Target primitive metadata files: 243
- Explicit provenance matches: 19
- Heuristic matches: 2
- Uncovered source skills: 142
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
| `fluidsim` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 81 |
| `pkpd-modeling` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 81 |
| `simpy` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 81 |
| `iso-standards-readiness` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 80 |
| `peer-review` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 80 |
| `geniml` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 79 |
| `geopandas` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 79 |
| `hypothesis-generation` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 79 |
| `opentrons-integration` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 79 |
| `pylabrobot` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 79 |
| `pysam` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 79 |
| `pathml` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 78 |
| `pptx-posters` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 78 |
| `pymoo` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 78 |
| `qutip` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 78 |
| `scientific-slides` | `uncovered` | `split_primitives` | `resource_only` | 78 |
| `scikit-survival` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 78 |
| `lab-hardware-cad` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 77 |
| `neuropixels-analysis` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 77 |
| `pyopenms` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 77 |
| `latchbio-integration` | `uncovered` | `primitive_plus_executor` | `propose_executor` | 76 |
| `market-research-reports` | `uncovered` | `split_primitives` | `resource_only` | 76 |
| `paper-lookup` | `uncovered` | `split_primitives` | `resource_only` | 76 |

## Interpretation

- `explicit_provenance` is auditable integration through `source.distilled_from`.
- `heuristic_*` is a candidate relationship and requires manual review.
- `resource_with_execution_assets` means code may be selectively promoted after allowlist, hash, dependency, and boundary review.
- `propose_executor` is only a candidate; it still requires isolated execution and acceptance evidence.
- `split_primitives` indicates that one source skill appears to contain multiple reusable concerns.
