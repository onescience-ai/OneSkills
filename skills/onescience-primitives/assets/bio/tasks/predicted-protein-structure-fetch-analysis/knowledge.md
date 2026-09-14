# 预测蛋白结构获取与置信判读 (predicted-protein-structure-fetch-analysis)

## 任务目标
给定 UniProt 登录号，获取 AlphaFold DB 预测结构（mmCIF）与 Predicted Aligned Error（PAE）矩阵，
产出整体折叠置信、内在无序区与刚性结构域边界的综合结论，供下游结构分析决策使用。

## 适用范围 / 不适用场景
适用：已有 UniProt 登录号且需要预测结构置信（pLDDT）、结构域边界或无序评估。
不适用：仅有蛋白名/基因名/序列（先经 tools/uniprot-database-access 解析登录号）；结构同源搜索
（改走 Foldseek）；对自定义序列跑预测；需要实验结构（改走 tools/pdb-structure-data-access）。

## 实体槽（Entity Slots）
- structure_source：alphafold-db（预测）/ rcsb-pdb（实验，改道）。
- analysis_focus：plddt-confidence / domain-boundary / disorder。

## 输入输出契约
输入：UniProt 登录号（如 P00520）。输出：`.cif` 结构文件、`_predicted_aligned_error.json`、
`-metadata.json`；分析脚本 stdout 给出置信与结构域结论；逐残基 pLDDT 存于 mmCIF 的 B-factor 列。

## 方法路线（可替换）
fetch_structure.py（超大蛋白自动 fragment 回退）→ analyze_plddt.py（置信启发式分级）→
analyze_pae.py（滑窗 PAE 启发式检测刚性域边界）。禁止手算结构域边界或自行评估无序。

## 操作序列（Operations）
1. 校验登录号；2. 获取结构三件套（-o 指向项目目录而非技能目录）；3. 读 metadata 跑 pLDDT 分级；
4. 读 PAE 跑域边界检测；5. 综合 pLDDT 结论与 PAE 结论写整体判读；6. 强制 relay 脚本 WARNING。

## 验证契约（Validations）
- pLDDT 分级：structured / disordered / mixed，需给出 Very Low 与 Very High 占比。
- isoform 替代或蛋白 >2700 AA 的 WARNING 必须显著转达，不得省略。
- 高度无序（pLDDT<50 占比高或无刚性域）→ 单独显著警告，劝阻全蛋白下游结构分析（如 Foldseek、对接）；
  若存在小有序域，后续分析严格限定在这些残基边界内。

## 资源引用（Resources）
- tools/uniprot-database-access：登录号解析与序列核验。
- tools/pdb-structure-data-access：实验结构改道。

## 前后置任务（Task Graph）
前置：protein-sequence-homology-analysis（序列层同源与功能线索）。

## 缺口与降级（Fallback / Gap）
AlphaFold DB 无 canonical 条目（仅 isoform）→ relay 警告并标注置信局限；需要实验证据 →
改道 tools/pdb-structure-data-access；高度无序 → 限定有序域边界或放弃结构路线改序列/功能路线。
