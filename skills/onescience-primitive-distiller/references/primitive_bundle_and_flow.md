# Primitive Bundle and Distillation Flow

## Conclusion

No. A primitive is not limited to four files.

The four core files are only the minimum bundle:

- `metadata.json`
- `spec.md`
- `usage.md`
- `workflow_planning.md`

They are the smallest unit that can be retrieved, reasoned about, and bound into a plan.

## Bundle Layers

### 1. Core bundle

The core bundle carries the primitive identity, contract, usage surface, and workflow guidance.

### 2. Knowledge layer

Optional `references/` files extend the primitive with read-only source guidance, examples, migration notes, or upstream explanations.

Every copied reference should be registered in `metadata.json.knowledge_assets` with:

- relative path
- title
- purpose
- source locator
- SHA-256
- media type

### 3. Execution layer

`scripts/` and other runnable assets are optional.

They may only be promoted when the source path, license, dependency surface, side effects, and hashes are reviewed and the primitive explicitly declares an execution asset policy.

### 4. Source payload layer

`source_payload/` is an optional preservation layer for scripts, templates, and static files copied from a source skill.

These files are indexed in `metadata.json.source_payloads` with relative path, source locator, SHA-256, media type, and `execution_status: not_whitelisted`. They preserve migration material for future executor work, but they are inert by default and must not be run, imported, or returned as `execution_assets`.

Promoting any source payload into `scripts/` or an execution whitelist requires a separate review of inputs, outputs, dependencies, side effects, and validation checks.

### 5. Consumer dependency layer

When another primitive depends on the distilled capability, record it through:

- `primitive_dependencies`
- `provider`
- `provenance`
- `contracts`

That keeps integration auditable without creating a permanent bridge skill.

## Distillation Flow

1. Inventory the source skill or third-party capability.
2. Classify the target shape: primitive, expert, executor, or split.
3. Distill the source knowledge into the core bundle.
4. Normalize `primitive_id`, provider metadata, and provenance.
5. Decide whether references or execution assets should be copied.
6. Optionally preserve source scripts/templates as inert `source_payloads` when the next migration step needs them.
7. Connect consumers that already depend on the capability.
8. Return a result that records what was created, what was withheld, and what still needs review.

## Decision Rules

- `resource_only`: default for documentation, planning knowledge, workflows, databases, datasets, output formats, and unstable code.
- `resource_with_execution_assets`: only when runnable assets are necessary and can be safely whitelisted.
- `propose_executor`: when the source has stable inputs, outputs, and repeatable validation evidence.
- `propose_expert`: when the main value is judgment, fallback, or planning rather than fixed execution.
- `split`: when one source skill mixes tools, databases, workflows, output formats, or multiple task chains.

## Practical Rule

If a source skill can be answered fully with retrieval and planning, keep it at the core bundle plus references.

If it requires deterministic runnable behavior, promote only the reviewed execution assets.

If it contains multiple distinct responsibilities, split it into multiple primitives.

## Example Shape

```text
skills/onescience-primitives/assets/<domain>/<category>/<primitive_name>/
  metadata.json
  spec.md
  usage.md
  workflow_planning.md
  references/          # optional
  source_payload/      # optional, inert source scripts/templates for review
  scripts/             # optional, only after review
```

The bundle is therefore a layered primitive, not a fixed four-file ceiling.
