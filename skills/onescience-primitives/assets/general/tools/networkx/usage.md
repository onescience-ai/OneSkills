# typical_workflow

1. Match the task to `general.tools.networkx` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Creating graphs: Building network structures from data, adding nodes and edges with attributes
- Graph analysis: Computing centrality measures, finding shortest paths, detecting communities, measuring clustering
- Graph algorithms: Running standard algorithms like Dijkstra's, PageRank, minimum spanning trees, maximum flow
- Network generation: Creating synthetic networks (random, scale-free, small-world models) for testing or simulation
- Graph I/O: Reading from or writing to various formats (edge lists, GraphML, JSON, CSV, adjacency matrices)
- Visualization: Drawing and customizing network visualizations with matplotlib or interactive libraries

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
