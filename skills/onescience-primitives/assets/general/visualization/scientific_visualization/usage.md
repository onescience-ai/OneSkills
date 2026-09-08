# typical_installation

```bash
uv pip install matplotlib seaborn plotly pillow pypdf
```

# typical_workflow

1. Record audience, medium, variable semantics, units, and provenance.
2. Choose an encoding that preserves the evidence.
3. Add redundant accessibility cues and explicit missing-data handling.
4. Export with explicit dimensions and formats.
5. Inspect the rendered files at final size.

# usage_notes

- Do not alter data to make a figure look cleaner.
- State uncertainty definitions and sample units.
- Keep static and interactive outputs distinct.
- Verify publisher requirements from live official sources when needed.

# migrated_knowledge

Use `content_request: "参考资料"` for the indexed integrity, palette, publisher, plotting, and source-registry materials. Use `content_request: "完整参考资料"` when a detailed guide or dated publisher snapshot is required.

When a deterministic palette screen is needed, request `include_execution_assets: true` and run only the returned `scripts/palette_audit.py` asset with its SHA-256-verified dependencies. Example:

```bash
python skills/onescience-primitives/assets/general/visualization/scientific_visualization/scripts/palette_audit.py --palette okabe_ito_on_white --background FFFFFF --role graphical
```

The result is a screening report, not an accessibility or publisher-compliance certification. The remaining visualization scripts are tracked as migration candidates until their dependency and file-boundary contracts are explicit.

For a dated publisher plan, request the execution assets and run:

```bash
python skills/onescience-primitives/assets/general/visualization/scientific_visualization/scripts/export_plan.py --publisher nature --figure-type combination --width single --phase final
```

Add `--input <local-file>` only when `image_metadata.py` and its required optional reader package are available. The plan compares machine-readable properties with the dated local snapshot and does not replace live journal guidance.
