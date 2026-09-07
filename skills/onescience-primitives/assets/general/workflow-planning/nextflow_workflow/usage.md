# typical_installation

```bash
curl -s https://get.nextflow.io | bash
uv pip install nf-core
```

# common_usage

```bash
nextflow run nf-core/rnaseq -r 3.14.0 -profile test,docker --outdir results
nextflow run nf-core/rnaseq -r 3.14.0 -profile docker --input samplesheet.csv --genome GRCh38 --outdir results -resume
```

# usage_notes

- Smoke-test with a bundled test profile before real data.
- Pin the pipeline revision and engine version.
- Use params files and config profiles instead of hardcoded paths.
- Emit trace, report, timeline, and DAG artifacts for auditability.
