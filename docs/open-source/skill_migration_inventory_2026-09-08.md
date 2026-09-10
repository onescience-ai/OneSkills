# Skill Migration Inventory

Generated: `2026-09-08`

This inventory is read-only. It does not execute or copy source code.

## Summary

- Source skills with `SKILL.md`: 163
- Target primitive metadata files: 308
- Explicit provenance matches: 91
- Heuristic matches: 3
- Uncovered source skills: 69
- Target metadata requiring regex fallback: 0

## Highest-Priority Candidates

| Skill | Coverage | Shape | Code recommendation | Score |
| --- | --- | --- | --- | ---: |
| `hypogenic` | `uncovered` | `split_primitives` | `resource_only` | 74 |
| `protocolsio-integration` | `uncovered` | `split_primitives` | `resource_only` | 74 |
| `autoskill` | `uncovered` | `single_primitive` | `resource_only` | 73 |
| `relsa-severity-assessment` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 73 |
| `imaging-data-commons` | `uncovered` | `single_primitive` | `resource_with_execution_assets` | 72 |
| `liteparse` | `uncovered` | `primitive_plus_executor` | `propose_executor` | 72 |
| `matplotlib` | `uncovered` | `primitive_plus_executor` | `propose_executor` | 72 |
| `waypoint-bio` | `uncovered` | `primitive_plus_executor` | `propose_executor` | 72 |
| `arbor` | `uncovered` | `primitive_plus_executor` | `propose_executor` | 71 |
| `xlsx` | `uncovered` | `single_primitive` | `resource_only` | 71 |
| `onekgpd` | `uncovered` | `split_primitives` | `propose_executor` | 70 |
| `get-available-resources` | `uncovered` | `single_primitive` | `resource_with_execution_assets` | 69 |
| `medchem` | `uncovered` | `primitive_plus_executor` | `propose_executor` | 69 |
| `pathogen-variant-surveillance` | `uncovered` | `single_primitive` | `resource_with_execution_assets` | 69 |
| `bids` | `uncovered` | `single_primitive` | `resource_with_execution_assets` | 68 |
| `deeptools` | `uncovered` | `split_primitives` | `resource_with_execution_assets` | 68 |
| `infographics` | `uncovered` | `single_primitive` | `resource_only` | 68 |
| `labarchive-integration` | `uncovered` | `single_primitive` | `resource_only` | 68 |
| `open-notebook` | `uncovered` | `single_primitive` | `resource_with_execution_assets` | 68 |
| `hugging-science` | `uncovered` | `single_primitive` | `resource_with_execution_assets` | 67 |
| `ontology-term-resolution` | `uncovered` | `single_primitive` | `resource_with_execution_assets` | 67 |
| `scientific-schematics` | `uncovered` | `single_primitive` | `resource_only` | 66 |
| `exa-search` | `uncovered` | `single_primitive` | `resource_only` | 65 |
| `pacsomatic` | `uncovered` | `single_primitive` | `resource_with_execution_assets` | 65 |
| `ncats-arax` | `uncovered` | `single_primitive` | `resource_only` | 64 |
| `aeon` | `uncovered` | `single_primitive` | `resource_only` | 63 |
| `generate-image` | `uncovered` | `single_primitive` | `resource_only` | 63 |
| `geomaster` | `uncovered` | `single_primitive` | `resource_only` | 63 |
| `ginkgo-cloud-lab` | `uncovered` | `single_primitive` | `resource_only` | 63 |
| `modal` | `uncovered` | `single_primitive` | `resource_only` | 63 |

## Interpretation

- `explicit_provenance` is auditable integration through `source.distilled_from`.
- `heuristic_*` is a candidate relationship and requires manual review.
- `resource_with_execution_assets` means code may be selectively promoted after allowlist, hash, dependency, and boundary review.
- `propose_executor` is only a candidate; it still requires isolated execution and acceptance evidence.
- `split_primitives` indicates that one source skill appears to contain multiple reusable concerns.
