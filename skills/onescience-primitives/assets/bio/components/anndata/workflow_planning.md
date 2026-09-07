# when_to_use

Use this primitive when the task needs an annotated matrix container, file conversion, concatenation, backed storage, or metadata-aligned slicing.

# when_not_to_use

- Use Scanpy for exploratory single-cell preprocessing and plotting.
- Use scvi-tools for probabilistic modeling.
- Use cellxgene-census for public atlas queries.
- Use a conversion executor when the task is only about moving from R-native objects to h5ad.

# planning_steps

1. Confirm matrix orientation, sample IDs, and raw count availability.
2. Decide between in-memory and backed storage.
3. Preserve raw counts and index alignment before filtering.
4. Choose concat strategy and merge policy.
5. Hand off the resulting AnnData to Scanpy, scvi-tools, or another downstream primitive.

# fallback

- If the input is non-native, convert first.
- If the data is too large, use backed mode or chunked access.
- If metadata is inconsistent, normalize indices before concatenation.

# handoff_notes

Include the source file, expected container layout, whether raw counts must be preserved, and the downstream tool requirements.
