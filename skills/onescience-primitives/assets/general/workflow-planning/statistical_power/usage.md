# typical_workflow

1. Confirm the design and primary estimand.
2. Choose the effect-size scale and target alpha/power.
3. Calculate sample size or detectable effect.
4. Adjust for attrition, clustering, or multiplicity.
5. Record assumptions and hand off the target to experimental execution.

# usage_notes

- Use sensitivity analysis when planning is uncertain.
- State whether the reported N is per group, total, or effective sample size.
- Preserve the effect-size rationale and any pilot-data assumptions.
- Recalculate when the design changes.

# migrated_knowledge

Use `content_request: "参考资料"` for the indexed effect-size, closed-form, and simulation-based power guides. Use `content_request: "完整参考资料"` for the source text needed to justify a nonstandard calculation.

The source `power.py` and `simulate_power.py` are intentionally retained as migration candidates. A future executor should accept a declarative design, seed, and effect-size grid and return a bounded JSON sensitivity table rather than expose arbitrary Python execution.
