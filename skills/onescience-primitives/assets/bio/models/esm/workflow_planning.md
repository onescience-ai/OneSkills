# description

ESM 的规划知识用于判断何时调用蛋白语言模型能力，并把蛋白 FASTA、模型权重、表征层、结构预测、突变打分或 inverse folding 需求组织成可执行计划。

# when_to_use

- 用户要求蛋白序列表征、embedding、per-token/mean 表示、contact map 或下游机器学习特征。
- 用户要求 ESMFold 快速预测蛋白结构，且输入是蛋白 FASTA。
- 用户要求用 ESM/ESM1v 对蛋白突变做零样本打分或 DMS 表格评分。
- 用户有蛋白 backbone，并且明确要求 ESM/GVP inverse folding、ESM 序列采样，或需要与 ProteinMPNN 做对照。
- 当 `workflow_type=protein_design_to_structure_validation` 中需要 ESMFold 对照、ESM embedding 特征、SimpleFold/ESM 离线资产支持或显式 ESM/GVP inverse folding 时使用；普通 backbone-to-sequence 仍优先 ProteinMPNN。
- 若端到端任务是标准 RFdiffusion -> ProteinMPNN -> validator 链路且未显式要求 ESM，对 ESM 只记录为可选对照或特征支持，不作为默认阶段。
- 不在用户输入为 DNA/RNA 基因组序列时使用；核酸序列推理召回 Evo2。

# inputs

- 用户目标：表征提取、快速结构预测、突变打分、contact 预测、显式 ESM/GVP inverse folding。
- 生物输入：蛋白 FASTA、野生型序列、突变 CSV、backbone PDB/CIF、链 ID。
- 模型输入：ESM2/ESM1v/ESMFold/GVP inverse folding 权重或模型名、repr layer、include 项。
- 运行输入：输出目录、token batch、recycle、chunk size、CPU/GPU/offload、scoring strategy。
- 下游需求：是否作为 SimpleFold 特征、ML 特征、结构初筛、突变候选排序或后续 OpenFold/Protenix 复核。
- 端到端上游产物：ProteinMPNN FASTA、候选 ID、backbone PDB/CIF 或突变候选表；下游可进入 SimpleFold/OpenFold/Protenix 复核或 ranking/report。

# outputs

- 召回决策：是否使用 ESM，以及 `representation`、`esmfold_structure`、`variant_scoring`、`inverse_folding` 或 `simplefold_feature_support` 模式。
- 执行计划：入口脚本、模型权重、输入文件、关键参数、输出目录和资源策略。
- 结果产物：embedding `.pt`、contact、PDB、突变分数 CSV、inverse folding FASTA、日志和失败诊断。
- 下游交接：把 embedding、ESMFold PDB、突变分数 CSV、inverse folding FASTA、候选 ID 和日志交给结构验证、候选筛选或 ranking/report。

# procedure

1. 判断用户是否在处理蛋白序列/结构，而不是核酸基因组序列。
2. 若是端到端 workflow，确认 ESM 是默认验证阶段、可选对照、特征支持还是离线资产依赖；不要替代已选的 RFdiffusion/ProteinMPNN 主链路。
3. 识别 ESM 使用模式：embedding、ESMFold、variant scoring、显式 ESM/GVP inverse folding 或 SimpleFold 特征支持；若只是普通 backbone-to-sequence，转 ProteinMPNN。
4. 单序列或 MSA token 化需要召回 `esm_sequence_batch_converter`；其它模式按模型 API 准备 FASTA、突变表、PDB/CIF、模型路径和参数。
5. 检查蛋白字母表、序列长度、token batch、模型权重、输出目录和 GPU/CPU 资源。
6. 基于 `onescience.models.esm` 的预训练加载、模型 forward、folding 或 inverse-folding Python API 构建入口，并显式写出关键参数。
7. 解析 observation：`.pt`、PDB、CSV、FASTA 是否生成，contacts/层输出是否符合预期，错误来自格式、长度、权重还是显存。
8. 根据结果衔接下游：embedding 进入分析，ESMFold 结构进入初筛，突变分数进入候选排序，inverse folding 结果进入结构复核。

# constraints

- ESM 的输入语义是蛋白氨基酸序列或蛋白 backbone，不处理 DNA/RNA 序列。
- 表征层、`include` 项和模型类型必须匹配；不要把 ESMFold 参数套到 ESM2 extract 上。
- 长序列可能超过 token 限制，需要截断、分段或调整 batch/chunk。
- ESMFold 结果适合快速预测和初筛，高价值候选仍建议用 OpenFold 或 Protenix 复核。
- 普通“根据 backbone 设计序列”默认选择 ProteinMPNN；ESM inverse folding 只作为显式指定或对照路线。
- 本卡只声明 ESM 表征、对照折叠或 inverse folding stage contract；端到端 workflow 的主链路和工具预检由 workflow 层决定。

# next_phase_recommendation

- 表征输出可进入聚类、相似性搜索、功能预测或自定义下游模型。
- ESMFold/结构输出可与 SimpleFold/OpenFold 做一致性检查。
- 蛋白突变高分候选可进入结构预测、稳定性分析或实验排序。
- inverse folding 结果若用于设计，应与 ProteinMPNN 结果对照，并用结构模型验证。
- 若作为 SimpleFold/ESM 离线资产支持，应把 ESM repo/权重准备状态交给 runtime preflight，而不是在模型卡中执行下载。

# fallback

- 模型权重不可用：切换到可用 ESM checkpoint 或让执行环境安装/下载权重。
- 序列过长：降低 `max-tokens-per-batch`、设置 `chunk-size`、截断或分段处理。
- FASTA/突变表格式错误：清理非法氨基酸、修正 mutation column 和 offset。
- ESMFold 显存不足：启用 CPU offload、增大 chunk、降低 batch，或改用 SimpleFold 做初筛。
