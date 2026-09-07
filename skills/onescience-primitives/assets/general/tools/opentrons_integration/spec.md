# architecture_overview

Opentrons Integration primitive for Protocol API v2 workflows, robot-specific liquid handling, deck and labware setup, modules, runtime parameters, and simulation.

This primitive is distilled from the source Agent Skill `opentrons-integration`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.10+ and uv for local simulation. Flex examples target opentrons 9.1.1 and API 2.29; the separate OT-2 line targets API 2.28 and uses opentrons 9.0.0 as its local compatibility simulator. Physical execution requires compatible hardware, current robot software, and the appropriate Opentrons App.

# source_knowledge_outline

- Opentrons Integration
- Overview
- Safety Boundary
- Choose the Right Interface
- Required Intake
- Install and Simulate
- Protocol Skeletons
- Flex, API 2.29
- OT-2, API 2.28
- Authoring Workflow

# knowledge_assets

- `references/api_reference.md`: Api Reference
- `references/liquid_handling.md`: Liquid Handling
- `references/migration-api-2-19-to-2-29.md`: Migration Api 2 19 To 2 29
- `references/modules_and_deck.md`: Modules And Deck
- `references/protocol_authoring.md`: Protocol Authoring
- `references/sources.md`: Sources
- `references/validation_and_operations.md`: Validation And Operations

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=7, scripts=6, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/opentrons-integration`.
