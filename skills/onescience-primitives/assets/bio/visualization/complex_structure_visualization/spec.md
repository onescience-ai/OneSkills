# primitive_version

`1.4.0`

# architecture_overview

`complex_structure_visualization` 同时覆盖蛋白质单体与复合物。单体是只有一个主要聚合实体的复合结构特例，不再维护独立的 monomer visualization primitive。

推荐执行路径是“规范 + 确定性执行资产”：

```text
single sample:
  PDB/mmCIF/CIF
  + optional AF3 *_confidences.json
  + optional AF3 *_summary_confidences.json

multiple samples:
  samples manifest
  -> repeated structure/confidence/summary triplets

both routes:
  -> structure, pLDDT provenance and PAE schema validation
  -> entity/chain classification and residue/atom confidence mapping
  -> deterministic embedded sample payload
  -> scripts/render_complex_structure.py
  -> RCSB-aligned polymer cartoon + sequence linkage + local bond focus
  -> AlphaFold-style confidence panel + 2D PAE
  -> scripts/validate_visualization.py + browser smoke test
```

执行资产不可用时，executor 才根据本文重新实现相同场景。真实 PyMOL `.pml/.pse` 仍由可用的 PyMOL 后端生成；本原语随附的 HTML 是 PyMOL 风格交互视图，不得声明为 PyMOL session。

# scene_modes

- `single_polymer`
- `protein_multimer`
- `protein_nucleic_acid`
- `protein_ligand`
- `mixed_complex`

自动选择优先级：

```text
mixed_complex
  > protein_nucleic_acid
  > protein_ligand
  > protein_multimer
  > single_polymer
```

# default_scene

首次打开必须直接显示结构，并采用以下规则：

| 实体 | 默认表示 | 默认颜色 |
|---|---|---|
| protein | RCSB-like `ribbon/cartoon`：宽 α 螺旋、箭头 β 折叠、细管 loop/coil | 按链；有显式结构域配置时可按结构域 |
| DNA/RNA | 平滑双螺旋骨架带 + 扁平核苷酸环片 | 每条核酸链使用不同且稳定的离散颜色 |
| ligand | `sticks` | 与蛋白、核酸清晰区分 |
| metal/inorganic ion | `spheres` | 独立离子颜色 |
| water | `hidden` | 不适用 |
| other | 轻量 `stick + sphere` | 中性色 |

默认不计算 surface、不启用全原子 sticks、不显示全部水。相机以全部可见非水实体居中并 fit-to-view。

3Dmol 内置 RCSB-like 几何固定为：

- protein 对全部可见蛋白使用一次连续 cartoon 设置：`style: oval`、`thickness: 0.26`、`arrows: true`、`tubes: false`，不得设置 `ribbon: true` 或固定 `width`。由二级结构驱动带宽，使 α/β 段保持宽带、loop/coil 保持窄连接，并允许 β 箭头生成；不得按 `atom.ss` 把同一条链拆成多次 `setStyle`。
- DNA/RNA 骨架使用 `style: oval`、`width: 0.8`、`thickness: 0.18`，不得设置 `ribbon: true`；核苷酸环片继续由独立 slab 几何绘制和拾取。
- mmCIF 没有 `_struct_conf`/`_struct_sheet_range` 时，固定使用内置 3Dmol.js 2.5.4 从坐标计算二级结构；不得伪造 helix/sheet 标注。运行时必须记录 `h/s/c` 残基计数和来源。默认视图与 pLDDT 视图必须复用上述几何，仅改变颜色。
- AF3 CIF 可能只提供 `_atom_site.label_atom_id`/`label_comp_id`。不得使用缺少 label fallback 的旧 CIF parser；若长度大于 8 的蛋白仍全部为 coil，页面必须给出诊断告警。
- 超短肽没有稳定二级结构、核酸缺少至少 5 个环原子时，不得伪造 ribbon、箭头或 slab。默认视图保留规范表示并提示可在自定义视图选择 sticks。

# top_level_views

多样本输出在视图按钮上方增加一个 `推理样本` 下拉框；单样本时该控件隐藏。顶部视图区只允许：

1. `默认视图`
2. `pLDDT`
3. 用户已保存的自定义视图按钮
4. `＋ 添加视图`

不得再建立 Cartoon、Sticks、Ball-and-stick、DNA slab、Surface 等独立固定标签页。上述表示均归入“添加视图”的组合配置。

自定义视图必须执行 `编辑 → 预览 → 生成`：预览只更新当前场景，不创建顶部按钮；表单内容变化后必须重新预览才能生成。每个已生成的自定义视图提供独立删除入口；删除活动视图时回退到默认视图。

`pLDDT` 只有在 `confidence_semantic: plddt` 得到上游或结构格式语义确认时才启用。实验结构普通 B-factor 或来源未知时禁用按钮，并记录原因。

默认视图与 pLDDT 视图共用同一套 RCSB-like 蛋白/核酸几何；pLDDT 只替换语义颜色，不得改变蛋白二级结构或核酸环片的表示方式。自定义视图继续按用户选择的 representation 渲染，不强制套用该内置预设。

每个活动三维视图下方固定显示同一活动样本的二维 PAE 面板。PAE 不复制到每个标签页，也不因默认、pLDDT 或自定义视图切换而重新生成；切换推理样本时，三维结构、置信度来源、PAE、实体显隐控件和样本摘要必须一起切换。

# custom_view_schema

```yaml
custom_view:
  name: <1..40 characters>
  protein:
    representation: ribbon | cartoon | tube | sticks | ribbon_surface | hidden
    color: chain | domain | secondary_structure | mono
    domain_ranges:
      - chain: A
        start: 1
        end: 120
  nucleic_acid:
    representations:
      - tube
      - slab
      - ladder
      - all_atom_sticks
    color: chain | base
  ligand:
    representation: sticks | ball_and_stick | spheres | hidden
  metal:
    representation: spheres | sticks | hidden
  water:
    representation: hidden | relevant_3_5A | all_spheres
  analysis_layer: none | interface_4A | protein_surface
  background: <CSS color>
  entity_visibility:
    <entity id>: true | false
```

约束：

- 核酸表示可组合；例如 `tube + slab`、`tube + ladder` 或 `slab + all_atom_sticks`。
- 每条 protein、DNA、RNA、每个 ligand/ion 以及 water group 必须有独立显隐控制。
- `domain` 颜色只有在提供有效 `chain:start-end` 范围时启用，否则回退按链。
- ladder 若无 DSSR/碱基配对注释，只能标记为几何近似。
- `interface_4A` 是几何接触残基提示，不是结合能或稳定性分析。
- `relevant_3_5A` 只显示距可见非水实体 3.5 Å 内的水。
- surface、全原子和全部水都按需生成，不属于首屏。

# structure_and_entity_rules

1. 优先使用 mmCIF `_entity_poly.type`、`label_entity_id` 和 asym 映射分类。
2. protein/DNA/RNA 的独立显示单元为链；ligand/ion 为残基实例；water 可聚合。
3. 保留 auth/label chain 与 residue ID 的可追踪映射。
4. 多模型结构默认只显示第一个模型。
5. 不得只根据 `ATOM/HETATM` 判断 polymer；DNA 也可能使用 `ATOM`。
6. 水、离子和配体分类优先于通用 hetero fallback。

# confidence_semantics

`--confidence-semantic auto` 是 1.4.0 的默认值，并且必须 fail closed：

1. 若 AF3 `*_confidences.json` 包含与结构原子数完全相等的 `atom_plddts`，语义确认为 `plddt`。
2. 否则，若 ModelCIF/mmCIF 的 `_ma_qa_metric` 明确声明 local pLDDT，且 `_ma_qa_metric_local` 可按 `(label_asym_id, label_seq_id)` 映射，语义确认为 `plddt`。
3. 两类证据都不存在时回退为 `none`；不得仅凭数值范围猜测普通 B-factor 是 pLDDT。
4. `--confidence-semantic plddt` 是调用方的显式语义声明，主要用于已知 AlphaFold PDB/B-factor 载荷；实验结构不得为方便显示而使用该声明。

三维表示使用两层真实置信度：

- ribbon/cartoon/tube 着色优先使用 `_ma_qa_metric_local` 的逐残基/逐核苷酸 pLDDT。映射键必须使用 ModelCIF label ID，而显示仍可使用 auth ID。
- 若没有 local metric，但已有经确认的 atom pLDDT，则对同一 `(label_chain, label_residue)` 的原子取均值，作为明确标注的 residue-mean fallback。
- 点击原子时同时显示 residue pLDDT 与 atom pLDDT；atom pLDDT 优先来自 AF3 `atom_plddts`，否则仅在语义已确认为 pLDDT 时使用结构的 `B_iso_or_equiv`。
- 同时提供 AF3 `atom_plddts` 与 mmCIF B 值时，长度必须等于结构原子数，并逐原子比对；最大绝对差大于 `0.02` 时生成失败，避免错误样本配对。
- 缺失值使用中性色，不得归入 `<50`。

输出 manifest 的 `confidence_provenance` 至少记录：

```yaml
semantic: plddt | b_factor | external | none
ribbon_source: mmcif:_ma_qa_metric_local | af3_confidences_json:atom_plddts(residue_mean) | structure:B_iso_or_equiv(residue_mean) | unavailable
atom_source: af3_confidences_json:atom_plddts | structure:B_iso_or_equiv | unconfirmed
residue_score_count: <integer>
atom_score_count: <integer>
atom_validation:
  compared_atom_count: <integer>
  max_abs_delta: <number|null>
  mean_abs_delta: <number|null>
  matches_mmcif_b_factor: <boolean|null>
```

pLDDT 阈值与颜色固定，不随浅色/深色主题改变：

| 置信度 | 半开区间 | 颜色 |
|---|---:|---|
| Very high | `pLDDT >= 90` | `#0053D6` |
| High | `70 <= pLDDT < 90` | `#65CBF3` |
| Low | `50 <= pLDDT < 70` | `#FFDB13` |
| Very low | `pLDDT < 50` | `#FF7D45` |

AlphaFold 风格面板标题背景固定为 `#B9D4F1`，标题文字为深色。主题变量只影响页面背景、边框和普通文字，不得改变上述语义色。

# pae_contract

完整二维 PAE 来自同一 AF3 样本的 `*_confidences.json`，必需字段为：

- `pae`：非空、有限、非负的 `N × N` 方阵。
- `token_chain_ids`：长度为 `N`。
- `token_res_ids`：长度为 `N`。

只要 `pae` 存在，任一维度或数值校验失败都必须停止生成，不能静默截断或拼接其他样本的数据。没有 `pae` 时仍可显示三维结构，但二维面板必须明确显示 unavailable。

PAE 轴语义固定为：

- 横轴：`Scored token / residue`。
- 纵轴：`Aligned token / residue`。
- 存储定义：`pae[i][j]` 表示以 token `i` 对齐时 token `j` 的预期位置误差；因此 canvas 的 row `i` 为 aligned token，column `j` 为 scored token。
- hover 必须显示两侧 chain/residue 标识和 PAE Å。
- 根据连续的 `token_chain_ids` 生成横纵链边界线与 `Chain <id>` 标签；不得由像素图案猜测链边界。

色图使用固定的反向绿色序列（`Greens_r` 语义）：低 PAE 为深绿，高 PAE 为浅绿。所有矩阵元素均保留，不做抽样；生成器按 row-major 顺序量化为 little-endian `uint16`，`scale: 10`，即显示分辨率 `0.1 Å`，再 Base64 嵌入。默认显示上限至少为 `31.75 Å`；若观测最大值更高，则向上取整到 `0.25 Å` 后扩展显示上限。

PAE manifest 至少记录：

```yaml
available: true
encoding: uint16-le
scale: 10
size: <N>
min: <angstrom>
max: <angstrom>
mean: <angstrom>
display_max: <angstrom>
chain_boundaries: []
axis_semantics:
  x: scored_token
  y: aligned_token
```

# multi_sample_contract

多样本模式由显式 JSON manifest 驱动，不自动猜测文件配对。每个 sample 是同一推理候选的结构/完整置信度/汇总置信度三元组：

```json
{
  "schema_version": "1.0",
  "title": "AF3 multi-sample result",
  "confidence_semantic": "auto",
  "default_sample_id": "seed-1-sample-0",
  "samples": [
    {
      "id": "seed-1-sample-0",
      "label": "sample 0 · best",
      "structure": "sample-0/model.cif",
      "confidence": "sample-0/confidences.json",
      "summary": "sample-0/summary_confidences.json",
      "ranking_score": 0.95,
      "format": "auto",
      "confidence_semantic": "auto"
    }
  ]
}
```

约束：

- `structure` 必需；`confidence`、`summary`、`ranking_score`、`label`、`title`、`format` 和 sample 级 `confidence_semantic` 可选。
- 相对路径以 samples manifest 所在目录为基准。
- sample ID 必须匹配 `[A-Za-z0-9][A-Za-z0-9_.-]{0,63}`，且全局唯一。
- `default_sample_id` 必须引用已声明 sample；未提供时使用数组第一项。
- manifest 数组顺序就是下拉框顺序；生成器不擅自按 ranking score 重排。
- 输出 public manifest 的 schema 版本为 `1.4.0`，并记录 primitive/profile、3Dmol 版本及 SHA-256、HTML/模板/生成器 SHA-256；每个 sample 记录输入路径及 SHA-256、实体数、pLDDT provenance、PAE 摘要和 summary confidences。

浏览器只向 3Dmol 加载当前 sample。切换时移除旧 model、surface、shape 和 label，重置界面缓存，重建实体显隐控件并重新绘制 PAE。原子元数据优先按 `(chain, residue id, residue name, atom name)` 队列映射，必要时才使用原子 index fallback；页面必须报告映射百分比。自定义视图的表示配置在样本间复用，实体可见性按当前 sample 的实体集合归一化。

# interaction_contract

最低能力：

- 旋转、缩放、平移和重置视角。
- 默认视图与 pLDDT 视图切换时保持相机。
- 页面左上角固定显示 `OneScience Visualization`。
- 三维视图上方提供 `Sequence of` 选择器，至少支持全部、蛋白质和 DNA/RNA；结构 hover 时对应氨基酸或核苷酸在序列中标红。
- 点击原子或核苷酸环片进入 `Dynamic bonds` 局部视图：以点击残基及其 4.5 Å 邻域显示按元素离散着色的 ball-and-stick；双键显示为两根平行键杆，可能氢键显示为独立颜色的虚线圆柱；局部居中且保持旋转/缩放，右侧 `Off` 恢复进入前的活动场景与相机。
- 双键键级优先使用解析器提供的 `bondOrder`；当 mmCIF/PDB 未携带键级时，仅允许对无歧义的标准蛋白键使用模板回退：主链 `C=O`、ASN `CG=OD1`、GLN `CD=OE1`。不得按原子距离猜测芳香环、共振体系、核酸碱基、磷酸或配体的局域化双键。
- 无显式氢坐标时，虚线必须标为 `possible H-bond(s)`：供体/受体来自标准蛋白或核酸白名单，重原子 `D···A` 距离为 2.4–3.5 Å，供体前驱角与受体前驱角均不小于 100°；排除同一残基、直接共价及两键内原子，并且每个 donor 仅保留几何最优候选。不得将普通邻域距离线声明为已验证氢键或完整 Mol* Interaction Provider 结果。外围视觉柔化不声明为真实景深计算。
- 点击标签只有在语义确认时附带 residue pLDDT 和 atom pLDDT。
- 新建自定义视图后，其按钮插在 pLDDT 与“＋ 添加视图”之间。
- 自定义视图至少支持表示组合、背景色和逐实体显隐，并且必须先预览后生成、可删除。
- 没有对应实体的选择器可保持空，不得制造占位实体。
- PAE 面板始终位于活动三维视图下方；hover 显示 scored/aligned token 和真实矩阵值。
- 多样本时显示样本下拉框，并同步切换结构、PAE、pLDDT provenance、ranking/ipTM/pTM 摘要和实体控件；单样本时隐藏下拉框。

# renderer_profiles

## bundled_interactive_web

- 入口：`scripts/render_complex_structure.py`
- 模板：`scripts/interactive_template.html`
- 后端：内置 3Dmol.js 2.5.4 classic build
- 输入：PDB/mmCIF/CIF；可选 AF3 confidence/summary JSON；或显式 samples manifest
- 输出：standalone HTML 或 HTML fragment，固定包含标题、序列联动和局部 bonds 聚焦
- Python 生成阶段仅使用标准库；固定运行库从 `scripts/vendor/3Dmol-2.5.4.min.js` 内联，生成和打开页面均不依赖网络，适用于 Windows/Linux/macOS 的现代 WebGL 浏览器。

## pymol

适用于可编辑场景与高质量 ray image：

- 真实输出：`.pml`、`.pse`、`.png`
- protein 映射为 cartoon/ribbon
- nucleic acid 映射为 tube/slab/ladder 或 PyMOL/DSSR 可支持的等价表示
- ligand 映射为 sticks，metal 映射为 spheres，water 默认隐藏
- 只有 PyMOL 实际运行并保存成功时才能报告 `.pse`

## large_structure_web

当结构规模或交互要求超出轻量模板能力时，可切换 Mol*。切换后仍需保持实体角色、默认表示、pLDDT 语义和输出 schema。

# performance_policy

- 首选随附脚本，不让 executor 每次重新生成 HTML/JS/CSS。
- 1.4.0 把固定 3Dmol 运行库和全部 samples 内嵌；结构、原子元数据和 PAE 都不从页面运行时外部读取。
- `--embed-mode` 为旧单结构 CLI 兼容参数；1.4.0 的统一 sample payload 与 PAE 编码不受该参数改变。
- PAE 是 `O(N²)` 数据。所有元素以 `uint16-le`、`0.1 Å` 分辨率保存，编码前占 `2 × N²` bytes，随后还有 Base64 约 `4/3` 的体积开销。
- 多样本 HTML 的磁盘和初始 JS 内存近似为各结构与各 PAE payload 之和；WebGL 只加载当前 sample，避免同时实例化多个三维 model。
- PAE 在样本切换时解码并绘制一次；三维视图标签切换不得重复解析 PAE。
- surface、全部水、全原子 sticks 和复杂几何层延迟到自定义视图。
- 大型结构应先关闭这些高成本层；必要时切换大型结构后端或简化表示。
- fragment 默认上限为 2 MB，standalone 默认上限为 20 MB。预计超过上限时应减少同页样本数、拆分结果页或显式审查后调整校验上限。
- 生成速度不等同于浏览器 WebGL/Canvas 速度；前者主要由原子数和 `N²` PAE 编码决定，后者主要由当前 sample 原子数、surface、几何数量和 PAE 尺寸决定。

# output_schema

```yaml
visualization_result:
  status: success | partial | failed
  primitive: complex_structure_visualization
  primitive_version: 1.4.0
  scene_mode: single_polymer | protein_multimer | protein_nucleic_acid | protein_ligand | mixed_complex
  renderer: 3dmol | pymol | molstar | ngl | other
  default_sample_id: <sample id>
  sample_count: <integer>
  samples:
    - id: <sample id>
      label: <display label>
      structure:
        path: <input path>
        format: pdb | cif | mmcif
        model_index: 1
        sha256: <hex>
      entity_summary:
        proteins: <count>
        dna: <count>
        rna: <count>
        ligands: <count>
        metals: <count>
        waters: <count>
      confidence_provenance:
        semantic: plddt | b_factor | external | none
        ribbon_source: <source>
        atom_source: <source>
        residue_score_count: <integer>
        atom_score_count: <integer>
      pae:
        available: <boolean>
        encoding: uint16-le | null
        size: <integer|null>
        axis_x: scored_token
        axis_y: aligned_token
  views:
    default: <resolved default_scene>
    plddt_enabled: <boolean>
    custom: []
    pae_below_every_view: true
  outputs:
    - kind: interactive | static_image | pymol_script | pymol_session
      format: html | png | pml | pse
      path: <output path>
  quality_checks:
    structure_parsed: pass | fail
    intended_entities_visible: pass | fail
    confidence_semantics_valid: pass | fail | not_applicable
    plddt_provenance_valid: pass | fail | not_applicable
    pae_matrix_valid: pass | fail | not_applicable
    sample_switch_smoke_test: pass | fail | not_applicable
    output_nonempty: pass | fail
    interaction_smoke_test: pass | fail | not_run
  capability_downgrades: []
  warnings: []
```

# execution_assets

执行器只能使用 `metadata.json.execution_assets` 白名单中声明的文件。召回层必须对相对路径做目录内规范化校验并校验 SHA-256；调用方不得沿 primitive 的裸 `path` 自行读取资产。

# quality_gates

1. 输入可解析且原子数非零。
2. 默认首屏显示所有主要非水实体。
3. protein ribbon、nucleic tube+slab、ligand sticks、metal spheres 规则成立。
4. 两条 DNA/RNA 链颜色可区分。
5. pLDDT 语义有效或按钮明确禁用；标准 AF3 样本要求 residue/atom score count 均大于零、ribbon source 非 unavailable，浏览器原子映射显示 `100.0%`。
6. pLDDT 四色与标题色分别精确为 `#0053D6`、`#65CBF3`、`#FFDB13`、`#FF7D45` 和 `#B9D4F1`。
7. 要求 PAE 时，每个 sample 的矩阵必须可用、size 大于零、编码为 `uint16-le`，且轴为 x=`scored_token`、y=`aligned_token`。
8. 多样本 ID 唯一，default sample 存在；样本切换后结构、PAE、置信度标题和摘要必须同步变化。
9. 顶部没有旧的独立表示标签页；自定义视图预览、生成、删除、组合选项、背景与实体显隐至少各完成一次交互测试。
10. 标题、序列类型筛选、结构 hover→序列标红、Dynamic bonds 的虚线可能氢键/平行双键→Off 恢复均存在且完成一次定点交互测试。
11. HTML 无残余模板占位符、无 fetch/XHR/WebSocket、输出非空；fragment 默认不超过 2 MB，standalone 默认不超过 20 MB。

# references

- PyMOL cartoon command: https://pymol.org/dokuwiki/doku.php?id=command%3Acartoon
- 3Dmol.js GLViewer: https://3dmol.csb.pitt.edu/doc/GLViewer.html
- RCSB 7R6R Mol* view: https://www.rcsb.org/3d-view/7R6R/1
- RCSB Mol* interaction guide: https://www.rcsb.org/docs/3d-viewers/mol*/getting-started
- DSSR-PyMOL nucleic-acid schematics: https://academic.oup.com/nar/article/48/13/e74/5842193
- Mol* viewer: https://academic.oup.com/nar/article/49/W1/W431/6270780
- AlphaFold 3 output semantics: https://github.com/google-deepmind/alphafold3/blob/main/docs/output.md
