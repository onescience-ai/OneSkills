# architecture_overview

Nextflow workflow is a reproducible scientific pipeline primitive. It captures dataflow, configuration, runtime profile, and nf-core conventions rather than embedding a complete pipeline.

# input_schema

Typical inputs are pipeline name or .nf path, revision, samplesheet, params file, profile, executor, container engine, output directory, and resume policy.

# output_schema

Expected outputs include run command, configuration plan, expected published results, trace/report/timeline/DAG artifacts, and debugging notes.

# key_dependencies

- nextflow
- Java 17 or newer
- optional nf-core tools
- Docker, Singularity, Apptainer, Conda, Wave, or another runtime profile
- optional HPC or cloud executor configuration

# common_modification_points

- pipeline revision and Nextflow engine version
- profile selection
- samplesheet schema
- process resources and retry strategy
- publishDir and output layout
- container and cache policy

# implementation_risks

- Running unpinned latest pipelines harms reproducibility.
- Container profiles are not interchangeable without checking infrastructure.
- Cached `-resume` results depend on inputs, scripts, and environment.
- Hardcoded paths in params or config can break portability.

# provenance

Distilled from `scientific-agent-skills/skills/nextflow` version `1.1`. Execution assets were not copied.
