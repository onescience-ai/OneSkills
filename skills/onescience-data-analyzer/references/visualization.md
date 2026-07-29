# 可视化生成工作流

## 工作流目标

根据数据特征与领域需求生成科学可视化结果；二维图表和三维结构场景使用各自的领域规范与质量门禁。

## 执行步骤

### 1. 数据准备
- 加载待可视化数据
- 数据清洗与格式化
- 识别数据维度与类型

### 2. 领域知识匹配
根据 `domain` 参数加载对应领域可视化规范：
- 气象：`assets/meteorology_viz.md`
- 生信：`assets/bioinformatics_viz.md`
- 流体：`assets/fluid_dynamics_viz.md`
- 材料：`assets/materials_science_viz.md`

当生信输入为 PDB/mmCIF/CIF 或请求包含结构、复合物、PyMOL、ribbon、slab、ladder、pLDDT 时，必须另行通过 `onescience-primitives` 召回 `complex_structure_visualization`；需要 bundled Web renderer 时同时请求受控 execution assets，不得仅依赖通用 `bioinformatics_viz.md`，也不得沿资源 `path` 直读 primitive 文件。

### 3. 图表类型选择
基于数据特征与需求确定：
- 时间序列 → 折线图/面积图
- 分布 → 直方图/箱线图/小提琴图
- 关系 → 散点图/相关性热图
- 空间 → 等高线图/热力图/矢量场
- 多维 → 3D图/平行坐标/降维可视化
- PDB/mmCIF/CIF → `complex_structure_visualization` 三维结构场景

### 3.5. 执行资产预验证（仅结构可视化）

当 `viz_type=complex_structure` 时，在进入完整渲染流程之前，必须先执行轻量级的资产可用性预验证：

1. 向 `onescience-primitives` 发起 `include_execution_assets: true` 请求，绑定 `complex_structure_visualization`。
2. 检查返回的 `execution_assets_summary`：
   - 若 `available + materialized < total`，逐资产检查 `status` 字段，确认哪些资产不可用及其原因。
3. 按降级决策矩阵（见 `onescience-data-analyzer/SKILL.md` 的「阶段二：降级决策」）判断：
   - `scripts/render_complex_structure.py` 和 `scripts/vendor/3Dmol-2.5.4.min.js` 均可用 → 进入步骤 4 完整渲染流程。
   - 任一必需资产不可用 → 立即向 orchestrator 返回 `status: blocked`，附带结构化的 `blocked_details`（包含逐资产状态和 `execution_assets_summary`），不进入后续解析与渲染阶段，避免浪费前序准备时间。
   - 仅非必需资产（模板、验证器、许可证）不可用 → 标记对应降级策略，继续进入步骤 4。
4. 将 `status=available` 的资产内容内联到工作区，将 `status=materialized` 的资产通过 `materialized_path` 引用。

### 4. 图表生成
- 应用领域配色方案
- 设置坐标轴与标签（符合领域规范）
- 添加图例与注释
- 优化布局与分辨率

三维结构场景改为：

1. 解析结构实体、链、配体、离子和置信度来源。
2. 多样本 manifest 中每个样本原子配对 CIF、`confidences.json` 和 `summary_confidences.json`，并校验 atom/token 维度；单文件兼容模式没有 confidence JSON 时必须禁用 PAE。
3. PAE 只读取 `confidences.json.pae`；不得用 summary 的 `chain_pair_pae_min` 伪造二维矩阵。
4. 依据 primitive 生成 renderer-neutral scene specification，默认 protein ribbon、DNA/RNA tube+slab、ligand sticks、metal spheres、water hidden。
5. 对 bundled Web visualization 必须运行已返回且校验通过的确定性脚本；只有用户明确要求其他 renderer 时才选择真实 PyMOL 或其他后端。
6. 保持链/实体颜色、pLDDT 阈值和输出元数据跨后端一致。
7. 检查所有主要实体可见、置信度语义有效、输出非空并运行静态 validator；浏览器可用时执行 visual smoke test，否则结果必须标记为 runtime_not_verified。

### 5. 导出输出
- 保存为指定格式（png/svg/pdf/html；真实 PyMOL 后端可额外输出 pml/pse）
- 生成图表元数据
- 记录可视化参数
- 结构场景额外记录 primitive、scene mode、renderer、链色映射、confidence semantic、warnings 和 quality checks

## 输出内容

```json
{
  "figures": [
    {
      "path": "output/figure_1.png",
      "type": "line_plot",
      "description": "时间序列趋势图"
    }
  ],
  "interactive": [],
  "pymol": [],
  "metadata": {
    "colormap": "viridis",
    "dpi": 300,
    "format": "png"
  },
  "visualization_result": {
    "primitive": null,
    "scene_mode": null,
    "renderer": null,
    "sample_count": 0,
    "provenance": {},
    "pae": {"available": false},
    "validation_flags": {},
    "warnings": [],
    "quality_checks": {}
  }
}
```
