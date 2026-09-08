# typical_workflow

1. State the question, response, treatment factors, and experimental unit.
2. List nuisance factors and decide which must be blocked or stratified.
3. Pick the design family: randomized, blocked, factorial, response-surface, crossover, cluster, or adaptive.
4. Separate true replicates from repeated measurements.
5. Hand off the chosen design to power and analysis planning.

# usage_notes

- Design before looking at outcomes.
- Archive random seeds and allocation schedules when they are generated.
- Use blocking for known nuisance variation instead of hoping analysis will absorb it.
- Treat plate, batch, and run-order effects as design constraints.

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed design guides. Use `content_request: "完整参考资料"` only when the detailed source text is needed; the references are read-only and do not provide execution permission.

The source `doe_designs.py` and `randomization.py` are tracked as migration candidates in the full-skill inventory. They should be wrapped behind a bounded design-matrix contract before being promoted to execution assets.
