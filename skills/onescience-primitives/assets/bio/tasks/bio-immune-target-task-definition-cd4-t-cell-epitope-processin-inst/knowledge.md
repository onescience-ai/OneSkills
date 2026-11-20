# 实例任务：免疫对象与任务定义 @ B26

- domain: bio
- 骨架: bio-immune-target-task-definition-task
- 场景: bio-cd4-t-cell-epitope-processing-presentation-prediction-scenario (B26)
- step_id: s01
- depend: []

## 场景研究主体
- B26
- 关联论文: APLSuite: An Integrated Suite for CD4+ T Cell Epitope Prediction via Antigen Processing Likelihood | doi:; CAME-AB: Cross-Modality Attention with Mixture-of-Experts for Antibody Binding Site Prediction | doi:

## 本实例步骤描述
读取CD4 T细胞表位加工与呈递预测所需的抗原、抗体或受体数据。

## 本实例执行 prompt
校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的CD4 T细胞表位加工与呈递预测任务。

## 本实例输入槽
- {IMMUNE_INPUT} | required=True | type=doc | var_name=免疫输入数据 | hint=输入序列结构或配对表 | default=viral_proteome.fasta
- 既有非致病模型抗原的结构输入可使用鸡溶菌酶 PDB 1LYZ（Gallus gallus，税号 9031；UniProt P00698；实体 1、链 A，实体标称 129 残基）。结构模型版本为 revision 1.4（2024-10-16）；资源包 `rcsb-1lyz-r1p4-chicken-lysozyme` 的必要文件为 `1LYZ.pdb`、`entry.json`、`polymer_entity_1.json`，用途为结构输入质控。该版本的共享目录尚未核实可访问，共享位置与同一资源、版本的对应关系仍缺少证据，暂无已核实的可用共享绝对路径。P00698 前体与成熟结构残基需建立映射，实体长度不保证每个残基均有完整坐标；原结构、链/插入码、缺失与失败记录随标准化结果保留。默认文件名仅为示例，不能用于推断来源或文件存在性。
- {MODEL_NAME} | required=True | type=enum | var_name=免疫模型 | hint=选择场景使用的模型 | default=APLSuite
- APLSuite 的可核验实现为 APL 应用及 EasyAPI-APLSuite/gpuCOREX 组件，具体版本与依赖见下列工具资源。`aplsuite.pt` 不是已核验的必要权重，不由模型名称推定权重可用。
- {TASK_MODE} | required=False | type=enum | var_name=任务模式 | hint=选择预测或设计任务 | default=design
- 使用上述既有结构的预测/质控属于 prediction 分支；槽中的 design 为模板示例，资源关联不提供序列设计输入，也不自动启用设计。

## 本实例产出
- 标准化免疫数据
- 链与表位映射
- 任务配置

## 本实例质量门禁
- 链类型可识别
- 样本标识唯一
- 任务标签定义明确

## 可调资源（edge:resource，仅真实存在）
- tools/simplefold-protein-structure-prediction-model-and-pipeline
- datasets/rcsb-1lyz-chicken-lysozyme：1LYZ 既有实验结构及来源元数据，用于核对实体、链、残基坐标与结构输入；不包含完整预测特征或独立表位标签。
- tools/aplsuite-antigen-processing-likelihood：APL@182c0faaf4f104f1621089f9b4a7899ed62deaa0、EasyAPI-APLSuite 2.0.11@a76754506c7515bc58b967ff16537ee0440619d4、gpuCOREX 0.0.2@0e55fd9f9ca6c279e3ceebd3f2e71f402e16ad1d 的实现与依赖说明。完整应用说明使用 Python 3.12；EasyAPI 1.0.1、biopandas 0.4.1、biopython 1.83、freesasa 2.2.1 等为来源版本要求，不是安装或加载成功的证明。APL 需要与真实残基对齐的四特征；联合 MHC 分支另需精确匹配的 MHC 方法、版本、等位基因及必要文件。方法与评价定义沿用 [场景知识](../../workflow-planning/cd4-t-cell-epitope-processing-presentation/knowledge.md)，资源卡不替代数值方法说明。

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
- 单个 1LYZ 结构可支持结构解析、映射及质控产物的保存/重开，但不提供完整的四特征、经核验的非致病同源输入、精确离线 MHC 实现或独立受测标签；结构质控通过不能作为完整预测、AP/AUPRC 或科研完成的证据。
- 标签评价需保留原测定条件、物种/等位基因、真实受测全集及实体映射；未测或未知不补为阴性，不把同实体的不同测定拼成独立双类真值。必需特征、软件或标签不足时保留相应未验证项与已有健康产物，不补造分数。
