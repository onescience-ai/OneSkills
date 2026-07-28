# description

用一个统一 primitive 规划蛋白单体与复合物结构显示。当前契约版本为 `1.4.0`，固定使用受控脚本和内置 3Dmol.js 2.5.4，覆盖 RCSB-like 聚合物样式、序列联动、局部 bonds 聚焦、AF3 真实 pLDDT、完整 PAE 与多样本联动。

# preferred_implementation

默认选择：

```text
primitive spec
  + whitelisted scripts/render_complex_structure.py
  + whitelisted scripts/interactive_template.html
  + whitelisted scripts/validate_visualization.py
```

原因：

- 省去 executor 每次重新生成约数万字节 HTML/JS/CSS 的过程。
- 表示规则、RCSB-like 内置几何、序列/局部聚焦、AlphaFold 固定色板、PAE 轴语义、交互、错误处理和安全转义保持一致。
- Python 生成开销远小于页面中 WebGL 解析和几何绘制。
- 模板升级可以版本化、校验 SHA-256，并用相同 flags 回归 pLDDT provenance、PAE 和样本数量。

纯文本规范重建仅作为 execution assets 不可用或目标后端完全不同的 fallback。

# when_to_use

- PDB/mmCIF/CIF 三维显示。
- AlphaFold/AlphaFold3 等结构推理输出。
- 蛋白单体、蛋白多聚体、蛋白-核酸、蛋白-配体和混合复合物。
- PyMOL 风格交互 HTML、真实 PyMOL 输出或大型结构 Web viewer。

# decision_rules

## scene_mode

1. protein、nucleic acid、ligand/ion 至少三类：`mixed_complex`
2. protein + DNA/RNA：`protein_nucleic_acid`
3. protein + ligand：`protein_ligand`
4. 多条 protein：`protein_multimer`
5. 单条主要 protein：`single_polymer`

## renderer

1. `.pse/.pml` 或 ray image：真实 PyMOL。
2. 会话内旋转、点击和自定义视图：bundled 3Dmol viewer。
3. 超大 mmCIF、复杂 assembly 或流式加载：Mol*。
4. 后端切换不得改变默认实体语义。

## confidence

1. AF3 `confidences.json.atom_plddts` 与结构原子一一对应，或 ModelCIF `_ma_qa_metric` 明确声明 local pLDDT：启用 pLDDT。
2. ribbon/cartoon 使用 `_ma_qa_metric_local` 的 residue/token 分数；点击原子使用 `atom_plddts`。两者并存时必须校验 AF3 atom 分数与 mmCIF B 值的逐原子一致性。
3. 普通实验 B-factor 或未知来源：禁用 pLDDT；不得根据 `0..100` 数值范围猜测。
4. 外部 confidence 仅在 chain/residue/atom 映射通过后启用。

## pae

1. 二维 PAE 只能来自与当前结构同一 sample 的完整 `*_confidences.json.pae`。
2. `*_summary_confidences.json.chain_pair_pae_min` 只能作为链对摘要，不能还原或替代完整 PAE。
3. 必须同时验证方阵、有限非负值、`token_chain_ids` 和 `token_res_ids` 的长度。
4. 横轴固定为 scored token/residue，纵轴固定为 aligned token/residue；低误差深绿、高误差浅绿。

## multi_sample

1. 单样本沿用 `input output` 位置参数；多样本使用显式 `--samples-manifest ... --output ...`。
2. 每个 sample 的 CIF、完整 confidence JSON、summary confidence JSON 是不可拆分的原子三元组，不跨目录猜测配对。
3. `default_sample_id` 必须存在，sample ID 必须唯一；manifest 顺序就是页面选择器顺序。
4. 样本切换必须同步替换三维模型、pLDDT provenance、PAE、ranking/ipTM/pTM 摘要和实体显隐集合。

# procedure

1. 发现输入：单样本读取结构路径及可选 confidence/summary；AF3 作业目录读取显式 samples manifest。
2. 对每个 sample 验证文件存在、结构格式、原子坐标和三元组归属，不自动拼配名称相近的文件。
3. 解析第一个 model、polymer type、链、ligand、ion、water。
4. 选择并映射 local pLDDT metric；验证 atom pLDDT 数量、顺序和来源。证据不足时 fail closed。
5. 若请求 PAE，解析完整矩阵和 token 轴；summary-only 输入在 PAE 门禁处失败，不伪造热图。
6. 选择 scene mode 与 renderer。
7. 通过 resource binding 获取白名单 execution assets 并校验路径/SHA-256。
8. 必须校验并运行 `render_complex_structure.py`；任何必需 execution asset 缺失或哈希不匹配时停止并报告，不得临时重写模板或静默 fallback。
9. 默认使用一次连续的 RCSB-like 蛋白 cartoon（`oval`、`thickness 0.26`、`arrows true`、`tubes false`，不启用恒宽 `ribbon`）与核酸骨架带（`oval`、`width 0.8`、`thickness 0.18`，不启用恒宽 `ribbon`）+独立环片，并保持 sticks、spheres 和 water hidden；surface、全部水、全原子、interface 等仅由自定义视图触发。
10. 用 `validate_visualization.py --manifest ... --expect-samples N --require-pae --require-plddt-provenance` 执行静态门禁。
11. 在浏览器定点检查默认/pLDDT 几何一致、Sequence hover、Dynamic bonds/Off、自定义预览→生成→删除、PAE 和至少一次样本切换；确认无 console error。
12. 输出 `visualization_result`，回传 sample_count、default_sample_id、每样本 provenance/PAE 摘要和实际通过的校验 flags。

# performance_and_degradation

- 固定复用 3 个白名单执行资产；不要在每次任务中重新编写模板。
- 结构、紧凑原子元数据和 PAE 作为确定性 payload 嵌入，不在页面运行时 fetch。
- PAE 以 little-endian `uint16`、`0.1 Å` 分辨率编码；编码前大小为 `2 × N²` bytes，完整矩阵不抽样。
- 页面只向 WebGL 实例化当前 sample；样本切换时才解码并重绘 PAE。
- 不在首屏创建 surface 或全部水。
- interface 和相关水使用空间网格，且仅在用户选择时计算。
- surface 是异步高成本层；大型结构应显示进度或切换后端。
- 当浏览器出现明显交互延迟时，依次关闭：surface → 全部水 → 全原子 sticks → slab 自定义网格。
- fragment 默认上限 2 MB，standalone 默认上限 20 MB；超限时优先减少同页样本数或拆分页面。
- 若简化后仍不满足交互要求，切换 Mol* 或生成 PyMOL 静态/会话输出。

# constraints

- executor 不得沿 `matched_resources[].path` 直读资产。
- execution assets 必须由召回层显式返回并校验。
- 不得在没有证据时把 B-factor 标为 pLDDT。
- 不得从 summary confidence JSON 生成像素级 PAE。
- 多样本不得把一个 sample 的 CIF 与另一个 sample 的 confidence/summary 混用。
- Web 的 PyMOL 风格不能写成 PyMOL session。
- 几何 ladder/interface 必须标注近似性质。

# fallback

- 解析失败：报告首个解析错误，不生成空页面。
- execution assets 缺失：依据 spec 重建，记录 `capability_downgrade`。
- vendored 3Dmol.js 缺失或哈希不匹配：停止生成并重新物化完整 execution assets；不得切换 CDN 或浮动版本。
- PDB 为超短肽或不完整核苷酸：保留规范默认表示并给出可渲染性诊断；需要全原子效果时由用户在自定义视图选择 sticks。
- confidence 未确认：保留默认按链视图并禁用 pLDDT。
- 完整 PAE 缺失：保留三维视图并明确显示 unavailable；若任务要求 PAE，则返回失败或 partial，而不是用链对摘要填充。
- 某个 sample 三元组校验失败：不静默跳过；指出 sample ID 和首个失败字段。
- standalone 超过 20 MB：减少同页样本、拆页或经显式审查提高门槛。
- 大结构：简化高成本层或切换 Mol*。

# acceptance

- 召回类型为 `visualization_primitive`、domain 为 `bio`。
- execution assets 只能从 metadata 白名单返回。
- 首屏只有默认视图、pLDDT、已保存自定义视图和添加视图。
- 页面左上角固定标题，视图上方提供 polymer sequence 筛选和 hover 联动。
- 默认规则与 `default_scene` 一致。
- 自定义组合、背景与逐实体显隐可用，且必须先预览后生成、生成后可删除。
- Dynamic bonds 以 4.5 Å 局部 ball-and-stick 聚焦并可 Off 恢复；双键以解析键级优先、无歧义标准蛋白模板回退绘制平行键杆；可能氢键须通过标准供受体白名单、2.4–3.5 Å 距离、双方前驱角 ≥100°、共价路径排除和每 donor 最优候选门禁后才绘制虚线，且不得声称为已验证氢键或完整 Interaction Provider。
- pLDDT 语义错误时 fail closed。
- 标准 AF3 ribbon 使用 `_ma_qa_metric_local`，atom click 使用 `atom_plddts`，来源与映射率写入 manifest。
- pLDDT 色板固定为 `#0053D6/#65CBF3/#FFDB13/#FF7D45`，面板标题为 `#B9D4F1`。
- PAE 使用完整矩阵、正确 scored/aligned 轴和链边界，并位于每个活动三维视图下方。
- 多样本选择器同步切换结构、置信度、PAE 和摘要。
- 输出 HTML、manifest 和校验结果可复现。
