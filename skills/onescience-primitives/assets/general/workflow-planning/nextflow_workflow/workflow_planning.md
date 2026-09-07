# when_to_use

Use this primitive when the task involves Nextflow, nf-core, reproducible scientific pipelines, containers, HPC/cloud execution, or workflow debugging.

# when_not_to_use

- Use a domain-specific application primitive when the user only needs a ready-made analysis card and no workflow-runtime detail.
- Use a simple script executor when the task has no pipeline structure.
- Use a database primitive when the task is only data retrieval.

# planning_steps

1. Decide whether the task is running, developing, configuring, or debugging a pipeline.
2. Pin the pipeline revision, Nextflow version, profile, and container strategy.
3. Validate samplesheet and params before real execution.
4. Run a test or stub path when possible.
5. Collect trace, report, timeline, DAG, logs, and published outputs.

# fallback

- If infrastructure is unknown, produce a portable local or test-profile command first.
- If a run failed, inspect work directory, trace, command, and container logs before changing code.
- If offline or HPC constraints apply, plan download and cache strategy.

# handoff_notes

Include pipeline, revision, profile, input samplesheet, params file, executor, container engine, outdir, resume flag, and expected audit artifacts.
