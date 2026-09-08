# Primitive Code Migration Batch

Date: 2026-09-03

This batch moves selected content from `scientific-agent-skills` into existing OneScience primitives. It is selective integration, not a repository merge.

## Migrated knowledge

The following primitives now contain source-traceable `references/` files. Each file is indexed in `metadata.json.knowledge_assets` with its purpose, source path, media type, and SHA-256:

- `general.workflow-planning.experimental_design`: four design, DOE, randomization, and adaptive-design guides.
- `general.tools.statistical_analysis`: five test-selection, diagnostics, effect-size, Bayesian, and reporting guides.
- `general.workflow-planning.statistical_power`: three effect-size, closed-form, and simulation-power guides.
- `general.visualization.scientific_visualization`: five visualization guides, three Matplotlib style starting points, and publisher planning profiles.

Knowledge assets are read-only. They are returned only through the resource retrieval contract and never grant permission to execute code.

## Migrated execution slice

`general.visualization.scientific_visualization` now contains a small, deterministic execution slice:

- `scripts/palette_audit.py`: bounded JSON CLI for sRGB contrast and heuristic grayscale screening.
- `scripts/_common.py`: shared bounded output and path-validation helpers.
- `assets/color_palettes.py`: bundled palette definitions loaded by the CLI.
- `scripts/export_plan.py`: dated publisher export planning and optional local-file screening.
- `scripts/image_metadata.py`: bounded raster, vector, and XML metadata inspection used by `export_plan.py`.
- `assets/publisher_profiles.json`: local machine-readable publisher snapshots used by `export_plan.py`.

The primitive `spec.md` declares these three files in one `# execution_assets` YAML allowlist. The metadata records `resource_with_execution_assets`, `copied_execution_assets: true`, and `sha256_whitelist`.

The CLIs are network-free, use bounded inputs, refuse implicit overwrite, and report screening results rather than accessibility or publisher-compliance certification. Publisher profiles are dated planning inputs and must be rechecked against the live target-journal page.

## Deliberately deferred code

The following source files remain candidates in the migration inventory and were not copied into executable primitive directories:

- Experimental design: `doe_designs.py`, `randomization.py`.
- Statistical analysis: `assumption_checks.py`.
- Statistical power: `power.py`, `simulate_power.py`.
- Scientific visualization: `figure_export.py`, `style_presets.py`, and `style_preview.py`.

The deferred files need explicit input/output schemas, dependency declarations, seed and resource bounds, and file-boundary review. Library-style modules and plotting or export helpers must be wrapped before promotion; copying them alone would create an ambiguous execution surface.

## Next batch rule

For each source skill, preserve three layers separately:

1. Knowledge: references and distilled workflow guidance.
2. Execution: only reviewed files declared by a primitive allowlist and verified by hash.
3. Migration evidence: the complete source inventory, risk flags, interface signals, and proposed target shape.

Use `docs/open-source/skill_migration_inventory_2026-09-03.json` as the batch queue. Do not mark a source skill fully migrated until its knowledge coverage, execution decision, and target primitive/application mapping are all explicit.
