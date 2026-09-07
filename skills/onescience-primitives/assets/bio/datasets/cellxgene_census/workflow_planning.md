# when_to_use

Use this primitive when the task needs population-scale public single-cell or spatial transcriptomics data, atlas metadata, or source dataset discovery.

# when_not_to_use

- Use Scanpy or AnnData for local data analysis.
- Use scvi-tools when the main task is model training.
- Use a private database or service primitive when the data source is not public Census data.

# planning_steps

1. Pin the Census version.
2. Narrow the organism and query scope.
3. Include `is_primary_data == True` unless the task explicitly needs duplicates.
4. Select only the columns and genes needed for the task.
5. Hand off the result as AnnData or metadata to the downstream primitive.

# fallback

- If the query is too broad, reduce the tissue or disease scope.
- If the result is too large for memory, switch to an out-of-core pattern.
- If the needed field is absent, inspect the release schema before expanding the query.

# handoff_notes

Include the Census version, organism, filters, requested columns, and the expected downstream consumer.
