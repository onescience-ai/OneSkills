---
name: onescience-data-analyzer
description: OneScience 数据分析执行技能（type=executor）。负责数据分析、可视化与报告输出，不涉及任务规划。接收规划好的任务，调用工作流执行统计分析、可视化生成和报告输出，根据领域自动匹配可视化规范（气象、生信、流体、材料等）。
type: executor
---

# onescience-data-analyzer

数据分析执行技能，负责数据分析、可视化与报告输出。

## 职责

本技能为执行器（executor），专注于执行数据分析任务，不涉及任务规划。规划由其他技能完成后传递给本技能执行。

## 核心能力

1. **数据分析**：统计分析、趋势分析、相关性分析
2. **数据可视化**：图表生成、多维展示、交互式可视化
3. **报告生成**：结构化报告、图文结合、结果导出

## 工作流调用

根据任务类型调用对应工作流：

- **统计分析**：`{{workflow:references/statistical_analysis.md}}`
- **可视化生成**：`{{workflow:references/visualization.md}}`
- **报告输出**：`{{workflow:references/report_generation.md}}`

## 领域知识

工作流执行时会根据数据领域自动匹配 `assets/` 目录中的领域知识：

- 气象数据可视化：`assets/meteorology_viz.md`
- 生物信息学可视化：`assets/bioinformatics_viz.md`
- 流体力学可视化：`assets/fluid_dynamics_viz.md`
- 材料科学可视化：`assets/materials_science_viz.md`

## 结构可视化原语

先将 `bio`、`biology`、`bioinformatics` 归一化为生信领域。当输入为 `.pdb`、`.cif`、`.mmcif`，或 `requirements.viz_type=complex_structure` 时：

1. 若 `step_handoff.resource_bindings` 已包含 `visualization_primitive` 的完整 `content` 和 `content.execution_assets`，先校验资产 SHA-256，再原样物化和执行白名单生成器；不得让模型重写模板。
2. 只有资源标识、规范不完整或缺少执行资产时，才向 `onescience-primitives` 请求 `content_request: 完整内容` 和 `include_execution_assets: true`。
3. 重新请求时使用 `filters.domain: bio`、`filters.keyword: complex structure visualization`；不得沿返回的裸 `path` 直接读取原语资产。
4. 必须绑定 `visualization_primitive` 类型的 `complex_structure_visualization` 并请求 `include_execution_assets: true`；执行资产缺失或 SHA-256 不匹配时停止并报告，不得按文本规范临时重写模板。
5. orchestrator 交接的 `step_handoff.inputs.visualization` 与下方直接调用 JSON 的 `data_path`、`requirements` 字段映射为同一内部请求。
6. PyMOL 不可用时可以回退交互式 Web renderer，但不得把 Web 输出声明为 `.pse` 或真实 PyMOL session。
7. `samples_manifest_path` 非空时进入多样本模式；manifest 中每个样本必须原子绑定同一 seed/sample 的 `structure`、`confidence` 与 `summary` 三个文件，任一缺失或校验失败则整条样本失败。
8. 完整 PAE 只能读取同一样本 `confidences.json.pae`；`summary_confidences.json.chain_pair_pae_min` 不能扩展、插值或复制为 PAE matrix。缺失时返回 unavailable，不得伪造热图。
9. `single_file_compatibility: true` 保留位置参数结构输入；没有完整 confidence JSON 时只生成三维结构视图并禁用 PAE。
10. 生成前校验 atom pLDDT 数量、PAE 方阵、token 映射、样本 ID 和文件来源；生成后使用 public manifest 验证 sample count、pLDDT provenance 与 PAE availability。

## 使用方式

接收来自规划技能的任务描述，按照以下流程执行：

1. 识别任务类型（分析/可视化/报告）
2. 加载对应工作流
3. 匹配领域知识和已绑定的 visualization primitive（如果需要）
4. 为结构可视化建立 renderer-neutral scene specification
5. 执行分析与生成
6. 执行输出非空、实体可见性和视觉 smoke test
7. 输出结果

## 输入格式

```json
{
  "task_type": "visualization|analysis|report",
  "data_path": "数据文件路径",
  "samples_manifest_path": "path/to/af3_samples_manifest.json|null",
  "single_file_compatibility": true,
  "confidence_path": "path/to/*_confidences.json|null",
  "summary_confidences_path": "path/to/*_summary_confidences.json|null",
  "domain": "meteorology|bio|bioinformatics|fluid_dynamics|materials_science|general",
  "requirements": {
    "viz_type": "line|scatter|heatmap|contour|3d|complex_structure|...",
    "primitive": "complex_structure_visualization",
    "scene_mode": "auto|single_polymer|protein_multimer|protein_nucleic_acid|protein_ligand|mixed_complex",
    "renderer": "auto|pymol|3dmol|molstar|ngl",
    "confidence_semantic": "none|plddt|b_factor|external",
    "confidence_source": "none|cif_ma_qa_metric_local|cif_b_factor|pdb_b_factor|af3_confidences_json|external_per_residue",
    "requested_views": ["default", "plddt", "custom"],
    "pae_source": "none|af3_confidences_json",
    "analysis_methods": ["correlation", "trend", "distribution"],
    "output_format": "png|svg|pdf|html|pml|pse"
  }
}
```

## 输出格式

```json
{
  "status": "success|partial|failed",
  "outputs": {
    "figures": ["path/to/fig1.png", "path/to/fig2.svg"],
    "interactive": ["path/to/structure.html"],
    "pymol": ["path/to/structure.pml", "path/to/structure.pse"],
    "report": "path/to/report.html",
    "data": "path/to/processed_data.csv"
  },
  "visualization_result": {
    "primitive": "complex_structure_visualization",
    "scene_mode": "single_polymer|protein_multimer|protein_nucleic_acid|protein_ligand|mixed_complex",
    "renderer": "pymol|3dmol|molstar|ngl|other",
    "sample_count": 1,
    "provenance": {
      "samples_manifest_path": null,
      "sample_files": []
    },
    "pae": {
      "available": false,
      "source": "none|confidences.json:pae",
      "sample_ids": [],
      "matrices_validated": 0
    },
    "validation_flags": {
      "expected_sample_count": true,
      "sample_ids_unique": true,
      "default_sample_exists": true,
      "atomic_sample_pairing": true,
      "plddt_provenance_all_samples": true,
      "pae_available_all_samples": true,
      "pae_matrix_shape_valid": true,
      "pae_token_mapping_valid": true
    },
    "warnings": [],
    "quality_checks": {}
  },
  "summary": "分析与可视化完成概要"
}
```
