# typical_workflow

1. Match the task to `general.tools.qiskit` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Use V2 primitive interfaces and PUB inputs. Do not write new V1 Sampler, Estimator, or QuantumInstance code.
- Runtime primitives accept ISA circuits; they do not perform layout, routing, and basis translation for you.
- Apply the transpiler layout to Estimator observables with observable.apply_layout(isa_circuit.layout).
- Use mode=backend, mode=session, or mode=batch for Runtime primitives.
- Use EstimatorV2 for resilience levels and expectation-value mitigation. Sampler has different noise-management options and no Estimator-style resilience levels.
- Read Sampler output by classical register name. Bitstrings are displayed most-significant bit first; Qiskit qubit 0 is conventionally the least-significant bit.

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
