# architecture_overview

Scientific visualization is a figure-planning and review primitive. It emphasizes honest encoding, accessibility, reproducibility, and delivery validation.

# input_schema

Typical inputs are source data paths, variable semantics, units, missingness, estimator choice, uncertainty definition, target medium, and export constraints.

# output_schema

Expected outputs include figure specifications, plotting implementation notes, export requirements, inspection checklist, alt text or data-alternative notes, and provenance metadata.

# key_dependencies

- matplotlib
- seaborn
- plotly
- pillow or pypdf for metadata inspection
- optional kaleido for static Plotly export

# common_modification_points

- figure size and target medium
- estimator and uncertainty interval
- color palette and redundant encodings
- static vs interactive output
- raster/vector export formats
- journal or publisher constraints

# implementation_risks

- Automated export checks do not certify scientific correctness or journal acceptance.
- Color alone is not a sufficient accessibility channel.
- Binning, smoothing, axis limits, and image adjustments can distort evidence.
- Interactive output needs static and accessible fallbacks when used for publication.

# provenance

Distilled from `scientific-agent-skills/skills/scientific-visualization` version `1.1`. References, three style assets, publisher profiles, and the palette-audit execution slice were copied selectively.

# knowledge_assets

- `references/publication_guidelines.md`: figure integrity, accessibility, and deceptive-encoding review.
- `references/color_palettes.md`: palette semantics, contrast, grayscale screening, and redundant encodings.
- `references/journal_requirements.md`: dated publisher snapshots and submission-stage planning constraints.
- `references/matplotlib_examples.md`: scoped Matplotlib, Seaborn, and Plotly patterns.
- `references/sources.md`: source registry with URLs, dates, and versions.
- `references/assets/*.mplstyle`: dated starting-point styles, not compliance presets.
- `references/assets/publisher_profiles.json`: machine-readable planning snapshots, not compliance claims.

All reference paths are read-only knowledge assets and are indexed with SHA-256 in `metadata.json`.

# execution_assets

The following files are the only executable assets returned when `include_execution_assets: true`:

```yaml
execution_assets:
  - path: "scripts/_common.py"
    kind: "other"
    purpose: "Shared bounded JSON output and path-validation helpers imported by the CLI."
    media_type: "text/x-python"
    sha256: "1bbbfb48500af7dd6df98076584085b2b2a24aee3024a7d9ce91dcb27ebd4b15"
  - path: "scripts/palette_audit.py"
    kind: "python_cli"
    purpose: "Audit sRGB background contrast and heuristic pairwise grayscale separation; no network is used."
    media_type: "text/x-python"
    sha256: "3a90b3c9a4a39dde6a341dc3de7b99cd2bca4773c66564fc90cdc2706a5a8165"
  - path: "scripts/export_plan.py"
    kind: "python_cli"
    purpose: "Build a dated publisher export plan and optionally screen a local file; no network is used."
    media_type: "text/x-python"
    sha256: "29e33fbb4a8a4f558e0a190afda50721f7bcb0fabf39a4f2b8f465152d9f20bf"
  - path: "scripts/image_metadata.py"
    kind: "python_cli"
    purpose: "Inspect bounded raster, vector, and XML metadata for export screening; no network is used."
    media_type: "text/x-python"
    sha256: "bd8df685ae0a31f92ab10ac5e5ac7472275d06a62e1543adb94a4de6bfe78693"
  - path: "assets/color_palettes.py"
    kind: "other"
    purpose: "Bundled palette definitions loaded by palette_audit.py without importing Matplotlib."
    media_type: "text/x-python"
    sha256: "173d95887be654867db3602430ade84f6362ae80477c5373de0b44ce40375f57"
  - path: "assets/publisher_profiles.json"
    kind: "other"
    purpose: "Dated local publisher snapshots loaded by export_plan.py; these are planning inputs, not compliance claims."
    media_type: "application/json"
    sha256: "12633ca62d1b7539b40fa31c01aa5b266546a25734961a41fc79250a5b328b9b"
```

# execution_contract

- Inputs are a bundled palette name or one to 32 six-digit sRGB hex colors, an optional background, and screening thresholds.
- Output is deterministic JSON to stdout or to an explicitly named file; existing outputs are never overwritten unless `--force` is supplied.
- The CLI is bounded, network-free, and does not import Matplotlib. It screens contrast and grayscale separation; it does not certify accessibility or publication compliance.
- `figure_export.py`, `style_presets.py`, and `style_preview.py` remain migration candidates pending separate dependency and file-boundary review.
