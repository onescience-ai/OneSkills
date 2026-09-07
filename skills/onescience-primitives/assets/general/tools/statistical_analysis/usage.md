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
