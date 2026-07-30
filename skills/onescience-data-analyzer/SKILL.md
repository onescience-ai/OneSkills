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

### 阶段一：执行资产获取

1. 若 `step_handoff.resource_bindings` 已包含 `visualization_primitive` 的完整 `content` 和 `content.execution_assets`：
   - 先检查 `execution_assets_summary`：若 `unavailable + failed == total`，跳过校验直接进入阶段二降级决策。
   - 否则遍历每个资产，校验 `status` 为 `available` 或 `materialized` 的资产 SHA-256，再物化到工作区。
2. 若资源绑定不完整或缺少执行资产，向 `onescience-primitives` 发起以下资源召回请求：
   - `user_request`：必须包含可视化信号词（如"交互式 3D 蛋白质结构可视化、pLDDT 置信度着色、PAE 热图渲染"），确保 primitives 技能能正确路由到 `visualization` category
   - `content_request: "完整内容"`
   - `include_execution_assets: true`
   - `filters.domain: bio`
   - `filters.keyword: complex_structure_visualization`（**必须使用下划线分隔的精确目录名**，以触发 primitives 的命名直查模式，绕过语义排序和截断）
   - 不得沿返回的裸 `path` 直接读取原语资产
3. **【强制】召回结果校验**：收到 `resource_retrieval_result` 后，执行以下校验：
   a. 检查 `matched_resources` 是否包含 `name=complex_structure_visualization` 且 `type=visualization_primitive` 的资源。
   b. 若**未召回**该原语（即返回空列表或不包含 visualization_primitive），**不得直接放弃**。必须执行以下回退步骤：
      ① 检查 `resource_retrieval_result.detected_domain` 是否为 `bio`，`task_intent` 是否包含 `visualization`。
      ② 若 `task_intent` 不包含 `visualization`，说明 primitives 可能未正确识别可视化意图。此时**重新发起请求**，将 `user_request` 修改为以可视化为主意图的描述（如"需要蛋白质复杂结构三维可视化、pLDDT/PAE 置信度着色、交互式 3D 视图的原语规范"），并显式设置 `filters.keyword: complex_structure_visualization pLDDT PAE 3D interactive render`（保留精确目录名 `complex_structure_visualization` 作为第一个 keyword 以触发命名直查）。
      ③ 二次请求后仍未召回，在 `visualization_result.quality_checks` 中记录 `primitive_not_recalled: true`，`recall_retry_count: 2`，`last_error: unable to match complex_structure_visualization after retry`，进入阶段二降级决策（仅生成非交互式图表，明确说明结构三维渲染不可用）。
   c. 若**已召回**，检查 `execution_assets_summary`，进入阶段二降级决策。

### 阶段二：降级决策

按资产角色分级处理，不允许全有或全无阻断。核心资产定义：

| 资产 | 角色 | 不可用时的行为 |
|---|---|---|
| `scripts/render_complex_structure.py` | **渲染器入口（必需）** | 阻塞，无法降级。返回 `status: blocked`，`blocked_details` 记录缺失原因。 |
| `scripts/vendor/3Dmol-2.5.4.min.js` | **离线运行时（必需）** | 阻塞，无法降级。离线 HTML 无法在没有 3Dmol.js 时渲染三维结构。 |
| `scripts/interactive_template.html` | **HTML 模板（可降级）** | 模板不可用但渲染器和运行时可用时，基于 `complex_structure_visualization` 的 `spec.md` 中 `# renderer_profiles` 和 `# top_level_views` 章节构建最小功能模板。必须支持默认视图、pLDDT 视图、序列联动和 PAE 面板，但可省略自定义视图和 Dynamic bonds 的完整交互。在 `visualization_result.quality_checks` 中标记 `template_rebuilt_from_spec: true`。 |
| `scripts/validate_visualization.py` | **验证器（可跳过）** | 不可用时跳过静态验证步骤，在 `visualization_result.quality_checks` 中标记 `validation_skipped: true`，`interaction_smoke_test` 设为 `not_run`。 |
| `scripts/vendor/3DMOL-LICENSE.txt` | **许可证文本（可跳过）** | 不可用时跳过内联，记录 warning。 |

降级禁止事项（不可跨越的红线）：
- 渲染器入口不可用时，**不得**根据 spec.md 或 usage.md 手写替代 `render_complex_structure.py`——这等同于重写核心渲染逻辑。
- 3Dmol.js 运行时不可用时，**不得**将离线 HTML 改为 CDN 外链——违反离线确定性交付约束。
- 模板降级仅允许在渲染器和运行时均可用时触发；降级产出的 HTML 必须仍在 `# output_schema` 约束内，且 `capability_downgrades` 必须逐项记录缺失功能。

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
    "quality_checks": {"template_rebuilt_from_spec": false,
      "validation_skipped": false,
      "interaction_smoke_test": "passed",
      "primitive_not_recalled": false,
      "recall_retry_count": 0
    }
  },
  "summary": "分析与可视化完成概要"
}
```
