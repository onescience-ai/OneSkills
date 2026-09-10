# when_to_use

Use this primitive when the task explicitly involves `pufferlib`, its scientific workflow, or its associated artifacts and data structures.

# when_not_to_use

- Use a more specific existing OneScience primitive when the task is already routed to a narrower model, component, dataset, or visualization primitive.
- Use an executor only when actual computation is required and the runtime dependencies are available.
- Do not use this primitive to bypass domain validation, credentials, or package installation requirements.

# planning_steps

1. Identify the scientific object, data type, package version, and intended result.
2. Retrieve the most relevant migrated reference files.
3. Extract required inputs, assumptions, parameters, and validation checks.
4. Decide whether the task can be answered as planning guidance or needs execution.
5. Record provenance, limitations, and downstream resource dependencies.

# handoff_notes

Pass `primitive_id: general.tools.pufferlib`, source references used, package/version assumptions, input artifacts, output expectations, and unresolved validation risks to the next workflow step.
