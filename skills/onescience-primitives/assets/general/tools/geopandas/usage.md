# typical_workflow

1. Match the task to `general.tools.geopandas` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Treat exact coordinates, addresses, parcel boundaries, trajectories, and
- Never automatically load a URL, cloud URI, GDAL /vsi* path, archive, or
- GDAL/OGR drivers, GEOS, PROJ, pyogrio, Shapely, pyproj, and their wheels are a
- Do not open macro-enabled office files or nested archives through permissive
- Read only named database secrets such as GEOPANDAS_POSTGIS_PASSWORD; use a
- Every derived artifact needs source hashes/versions, CRS, operation parameters,

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
