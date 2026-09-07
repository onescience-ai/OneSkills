# when_to_use

Use this primitive when a task involves exploratory scRNA-seq analysis, AnnData-based preprocessing, single-cell visualization, clustering, marker discovery, annotation, or pseudobulk preparation.

# when_not_to_use

- Use a model-specific primitive or executor when the main task is deep generative modeling, label transfer with a fixed trained model, or production inference.
- Use an AnnData or data-format primitive when the task is only about file structure, conversion, or schema validation.
- Use a statistical DE primitive when the main task is replicate-aware differential expression between biological conditions.

# planning_steps

1. Confirm input format, sample metadata, organism, and raw count availability.
2. Bind Scanpy for exploratory preprocessing, dimensionality reduction, clustering, visualization, and marker discovery.
3. Add separate primitives or executor requirements for conversion, batch correction, scVI-style modeling, pseudobulk DE, or report generation when needed.
4. Require checkpoints after QC, preprocessing, clustering, and annotation.
5. Require verification artifacts: processed `.h5ad`, QC plots, embedding plots, marker tables, parameter log, and warnings.

# fallback

- If Scanpy cannot install in the target environment, use a container or delegate to a runtime skill that can create an isolated Python environment.
- If data is too large for memory, consider chunking, sparse-backed storage, or an out-of-core workflow before execution.
- If annotation is ambiguous, return marker evidence and unresolved clusters rather than inventing labels.

# handoff_notes

Executor handoff should include input paths, expected output directory, QC thresholds or threshold-selection policy, sample and batch fields, clustering resolutions, marker genes or references, figure formats, and completion criteria.
