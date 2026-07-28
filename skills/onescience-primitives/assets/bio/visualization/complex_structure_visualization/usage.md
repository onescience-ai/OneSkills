# launch

优先通过 `onescience-primitives` 召回规范和受控 execution assets，再交给 `onescience-data-analyzer`。标准交接字段使用 `step_handoff`：

```yaml
step_handoff:
  step_id: visualize_complex_structure
  execution_skill: onescience-data-analyzer
  step_goal: 生成可交互的蛋白-DNA 复合物结构视图
  task_context:
    domain: bio
    task_intent: visualization
  resource_bindings:
    - type: visualization_primitive
      name: complex_structure_visualization
      version: 1.4.0
      include_execution_assets: true
  inputs:
    visualization:
      structure_path: outputs/structure.cif
      confidence_path: outputs/confidences.json
      summary_confidences_path: outputs/summary_confidences.json
      structure_format: auto
      scene_mode: auto
      renderer: 3dmol
      confidence_semantic: auto
      requested_views:
        - default
        - plddt
        - custom
        - pae
      output_formats:
        - html
  required_outputs:
    - visualization_result
    - interactive_html
  completion_criteria:
    - structure_parsed
    - default_scene_visible
    - plddt_provenance_valid
    - pae_matrix_valid
    - interaction_smoke_test
```

# direct_cli

## AF3 单样本：完整 pLDDT + PAE

在 primitive 目录执行：

```powershell
python scripts/render_complex_structure.py `
  path/to/model.cif `
  path/to/structure_interactive.html `
  --confidence-json path/to/confidences.json `
  --summary-confidence-json path/to/summary_confidences.json `
  --confidence-semantic auto `
  --manifest-output path/to/visualization_manifest.json
```

在此模式中，ribbon 优先按 ModelCIF `_ma_qa_metric_local` 的 residue pLDDT 着色；点击原子时显示 AF3 `atom_plddts`。完整 PAE、token 轴和链边界来自同一个 `confidences.json`。`atom_plddts` 数量必须等于结构原子数；若 mmCIF B 值存在，两者最大绝对差必须不超过 `0.02`。

## 旧单 CIF/PDB 兼容

原来的两个位置参数继续有效：

```powershell
python scripts/render_complex_structure.py `
  path/to/structure.cif `
  path/to/structure_interactive.html `
  --confidence-semantic auto `
  --manifest-output path/to/structure_manifest.json
```

若 CIF 自身含明确的 ModelCIF local pLDDT，`auto` 会启用真实 residue-level pLDDT；没有 `confidences.json` 时 PAE 面板显示 unavailable。普通实验 PDB/CIF 在 `auto` 下不会把 B-factor 当成 pLDDT。

## AF3 多样本 manifest

输入 manifest 示例：

```json
{
  "schema_version": "1.0",
  "title": "AF3 five-sample inference",
  "confidence_semantic": "auto",
  "default_sample_id": "seed-101-sample-1",
  "samples": [
    {
      "id": "seed-101-sample-0",
      "label": "sample 0 · ranking 0.9725",
      "ranking_score": 0.9725,
      "structure": "seed-101_sample-0/model.cif",
      "confidence": "seed-101_sample-0/confidences.json",
      "summary": "seed-101_sample-0/summary_confidences.json"
    },
    {
      "id": "seed-101-sample-1",
      "label": "sample 1 · ranking 0.9751 · best",
      "ranking_score": 0.9751,
      "structure": "seed-101_sample-1/model.cif",
      "confidence": "seed-101_sample-1/confidences.json",
      "summary": "seed-101_sample-1/summary_confidences.json"
    }
  ]
}
```

相对路径以 manifest 所在目录为基准。数组顺序即页面下拉框顺序，`default_sample_id` 决定首屏样本；渲染器不会自动重新排名。

```powershell
python scripts/render_complex_structure.py `
  --samples-manifest path/to/af3_samples_manifest.json `
  --output path/to/af3_multisample.html `
  --confidence-semantic auto `
  --manifest-output path/to/af3_multisample_output_manifest.json
```

多样本模式不能与位置参数 `input output` 混用。每个 sample 只要求 `structure`；缺少 `confidence` 时该 sample 的 PAE 不可用，但结构仍可显示。页面只把当前 sample 加载到 3Dmol；切换时结构、PAE、confidence provenance、summary 和实体控件同步更新。

## Codex fragment

生成 Codex 会话内片段：

```powershell
python scripts/render_complex_structure.py `
  path/to/model.cif `
  path/to/complex-structure.html `
  --confidence-json path/to/confidences.json `
  --fragment `
  --root-id complex-structure `
  --confidence-semantic auto `
  --manifest-output path/to/complex-structure-manifest.json
```

fragment 默认大小门槛为 2 MB；多样本通常应交付 standalone HTML，或只在 fragment 中放置一个样本。

## 静态校验

单样本/多样本完整置信度校验：

```powershell
python scripts/validate_visualization.py `
  path/to/af3_multisample.html `
  --manifest path/to/af3_multisample_output_manifest.json `
  --expect-samples 5 `
  --require-pae `
  --require-plddt-provenance

python scripts/validate_visualization.py `
  path/to/complex-structure.html `
  --manifest path/to/complex-structure-manifest.json `
  --expect-fragment `
  --expect-samples 1 `
  --require-pae `
  --require-plddt-provenance
```

未传 `--max-bytes` 时，fragment 上限为 2,000,000 bytes，standalone 上限为 20,000,000 bytes。验证器还检查固定标题、RCSB-like 内置预设、序列筛选/hover、Dynamic bonds/Off、自定义预览/删除、AlphaFold pLDDT 色板、`#B9D4F1` 标题色、PAE canvas/轴、样本选择器、无占位符以及无 fetch/XHR/WebSocket。

脚本仅依赖 Python 标准库。3Dmol.js 2.5.4 已固定在 `scripts/vendor/` 并由生成器内联到 HTML；生成后可直接离线打开，不访问 CDN。必须同时物化并校验 renderer、template、validator、vendored runtime 与许可证，不能只复制 Python 文件。
标准 profile 禁止任意 `--template` 覆盖；只有显式调试时才能同时传入 `--allow-custom-template`，此类输出不应作为标准交付。

普通 PDB 若只含短肽或不完整核苷酸，默认 cartoon/tube 可能只形成短 coil/圆柱；这不等于角色解析失败。页面会报告短肽全 coil 或核苷酸环原子不足，用户可在自定义视图选择 sticks。不得把普通实验 PDB 的 B-factor 自动声明为 pLDDT。

# confidence_examples

AF3 标准输出优先使用自动 provenance：

```text
--confidence-semantic auto
--confidence-json <sample>_confidences.json
```

来源优先级为：

1. ribbon：ModelCIF `_ma_qa_metric_local` residue pLDDT。
2. atom click：`confidences.json.atom_plddts`。
3. local metric 缺失时：经确认的 atom pLDDT 按 label chain/residue 求均值。

只有调用方已经独立确认 AlphaFold PDB/B-factor 载荷时才显式声明：

```text
--confidence-semantic plddt
```

实验结构或语义未知：

```text
--confidence-semantic none
```

后者会保留按链默认视图并禁用 pLDDT 按钮。不能为方便显示而把普通 B-factor 标为 pLDDT。

固定置信度色阶：

```text
>=90       #0053D6
70..<90    #65CBF3
50..<70    #FFDB13
<50        #FF7D45
```

PAE 使用 `Greens_r` 语义：低误差深绿、高误差浅绿；横轴为 scored token/residue，纵轴为 aligned token/residue，链边界来自 `token_chain_ids`。

# custom_view_example

“＋ 添加视图”中的等价配置：

```json
{
  "name": "DNA ladder + interface",
  "protein": {
    "representation": "ribbon",
    "color": "chain"
  },
  "nucleic_acid": {
    "representations": ["tube", "slab", "ladder"],
    "color": "chain"
  },
  "ligand": {
    "representation": "sticks"
  },
  "metal": {
    "representation": "spheres"
  },
  "water": {
    "representation": "hidden"
  },
  "analysis_layer": "interface_4A",
  "background": "#181818",
  "entity_visibility": {
    "protein:A": true,
    "dna:B": true,
    "dna:C": true
  }
}
```

当前 bundled viewer 要求先点击“预览”，再点击“生成视图”；表单变化会使上一次预览失效。生成后的按钮带独立删除入口，删除活动视图时回到默认视图。自定义视图只在页面会话内保存；跨页面持久化可由 executor 把相同 schema 写入 `visualization_result.views.custom`，但不能假装页面已经持久化。

# renderer_mapping

## bundled_interactive_web

- 默认：采用 RCSB-like 几何，protein 为宽 α 螺旋/箭头 β 折叠/细管 loop，DNA/RNA 为平滑骨架带+扁平核苷酸环片；ligand sticks、metal spheres、water hidden。
- pLDDT：与默认视图共用同一几何，仅在 provenance 确认为 `plddt` 时启用固定 AlphaFold 四色；点击局部可同时查看 residue/atom pLDDT。
- 序列：`Sequence of` 可筛选全部、蛋白质或 DNA/RNA；结构 hover 时对应序列位置标红。
- Dynamic bonds：点击原子或核苷酸环片后显示 4.5 Å 局部、按元素着色的 ball-and-stick 并居中；双键以两根平行键杆显示，可能氢键以虚线显示；`Off` 恢复原场景与相机。
- PAE：固定显示在每个活动三维视图下方，使用完整矩阵、`Greens_r` 语义、token 轴、链边界与 hover。
- 多样本：选择器切换当前 sample 的结构/confidence/summary 三元组；单样本时隐藏选择器。
- 自定义：protein representation/color、核酸组合表示、ligand/metal/water、分析层、背景、逐实体显隐；执行预览→生成，可删除。
- ladder 无配对注释时是几何近似。

## pymol

真实 PyMOL 可用时，使用同一 scene schema 映射到 cartoon/ribbon、sticks、spheres、surface、selection 和 distance。只有实际保存成功时才返回 `.pml/.pse`。

# runtime_request

```json
{
  "task_type": "visualization",
  "data_path": "outputs/model.cif",
  "domain": "bio",
  "requirements": {
    "viz_type": "complex_structure",
    "primitive": "complex_structure_visualization",
    "primitive_version": "1.4.0",
    "scene_mode": "auto",
    "renderer": "3dmol",
    "confidence_semantic": "auto",
    "confidence_path": "outputs/confidences.json",
    "summary_confidences_path": "outputs/summary_confidences.json",
    "requested_views": ["default", "plddt", "custom", "pae"],
    "output_format": ["html"]
  }
}
```

多样本请求将 `data_path` 替换为：

```json
{
  "samples_manifest_path": "outputs/af3_samples_manifest.json",
  "default_sample_id": "seed-101-sample-1"
}
```

# validation

必需：

```yaml
required:
  - structure_parsed
  - intended_entities_visible
  - confidence_semantics_valid
  - plddt_provenance_valid
  - pae_matrix_valid_when_requested
  - sample_ids_unique
  - default_sample_exists
  - output_nonempty
  - no_unresolved_placeholders
  - no_runtime_data_fetch
recommended:
  - default_view_smoke_test
  - plddt_view_smoke_test
  - pae_hover_smoke_test
  - sample_switch_smoke_test
  - custom_view_preview_generate_delete_smoke_test
  - sequence_filter_hover_smoke_test
  - dynamic_bonds_off_smoke_test
  - entity_visibility_smoke_test
  - atom_mapping_100_percent_for_standard_af3
  - renderer_version_recorded
```

# operation_limits

- 不执行结构预测、对接、结合能计算或分子动力学。
- 不从图像外观推断稳定性。
- 几何 interface/ladder 是显示辅助，不替代 DSSR、接触分析或实验验证。
- PAE 是预期位置误差可视化，不等同于实验误差，也不能替代结构域或界面验证。
- `uint16-le` PAE 保留完整矩阵维度，但显示值量化到 0.1 Å；原始 JSON 不被修改。
- 多样本页面把所有 payload 嵌入 HTML，样本数和 PAE 尺寸会线性/平方增加文件与内存开销。
- bundled 3Dmol 局部聚焦对解析到的键级绘制多键，并仅对标准蛋白主链 `C=O`、ASN `CG=OD1`、GLN `CD=OE1` 使用无歧义双键模板回退；不按距离猜测芳香、共振、核酸或配体键级。
- 无显式氢坐标时只显示 `possible H-bond(s)`：标准残基供体/受体白名单、2.4–3.5 Å 重原子距离、供体和受体前驱角均 ≥100°、排除同残基及两键内原子、每 donor 仅保留几何最优候选；这不是完整 Mol* Interaction Provider 或经能量验证的氢键分析。外围柔化是视觉提示，不是物理景深。
- Web 输出不是 PyMOL session。
