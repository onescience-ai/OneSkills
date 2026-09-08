# typical_installation

```bash
uv pip install "pingouin>=0.6" "scipy>=1.11" "statsmodels>=0.14.6" pandas matplotlib seaborn
uv pip install "pymc>=5.0" "arviz>=1.0"
```

# typical_workflow

1. State the hypothesis and variables before inspecting outcomes.
2. Inspect data quality, missingness, group sizes, and raw distributions.
3. Choose the test or model that matches the design.
4. Check assumptions and document remedial choices.
5. Report estimates, uncertainty, effect sizes, diagnostics, and limitations.

# usage_notes

- Label exploratory analyses separately from planned analyses.
- Correct for multiple comparisons when running test families.
- Report non-significant results and sensitivity limits.
- Keep the runnable analysis script or notebook with the result.

# migrated_knowledge

Use `content_request: "参考资料"` for the indexed test-selection, diagnostic, effect-size, Bayesian, and reporting guides. Use `content_request: "完整参考资料"` when the detailed guidance is required.

The source `assumption_checks.py` is intentionally not executable in this primitive yet: it has plotting side effects, optional scientific dependencies, and no bounded JSON input/output contract. Use it as migration evidence while designing a domain-neutral diagnostics executor.
