# typical_workflow

1. Match the task to `bio.tools.pysam` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- AlignmentFile and AlignedSegment for SAM/BAM/CRAM
- VariantFile, VariantHeader, and VariantRecord for VCF/BCF
- FastaFile for indexed FASTA and FastxFile for sequential FASTA/FASTQ
- TabixFile for BGZF-compressed, tabix-indexed BED/GFF/GTF/custom tables
- pysam.samtools and pysam.bcftools for wrapped command dispatchers
- fetch() returns alignment records overlapping a region.

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
