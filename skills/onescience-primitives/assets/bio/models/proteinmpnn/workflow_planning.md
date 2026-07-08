# description

ProteinMPNN 的规划知识用于判断何时把“给定骨架生成或评估氨基酸序列”的任务交给逆折叠模型，并把骨架 PDB、链约束、固定位置、采样参数和下游结构验证组织成可执行计划。

# when_to_use

- 用户给出蛋白 PDB/backbone，希望设计与该骨架兼容的氨基酸序列。
- RFdiffusion 已生成 backbone，需要补全序列并筛选候选。
- 用户要求固定某些链、固定残基、限制氨基酸、绑定对称位置或按 PSSM 约束采样。
- 用户要求对已有序列在给定结构上打分或输出条件概率。
- 当 `workflow_type=protein_design_to_structure_validation` 且 `starting_point=backbone_pdb`，或上游 RFdiffusion 已产出 backbone PDB/TRB 时，ProteinMPNN 是端到端链路的 `sequence_design` 阶段。
- 若端到端任务已有设计序列 FASTA 且不需要重新设计序列，应跳过 ProteinMPNN 并进入 SimpleFold/OpenFold/AlphaFold3/Protenix 验证阶段。
- 不在用户需要从序列预测结构时使用；该类任务召回 OpenFold、SimpleFold、ESMFold 或 Protenix。

# inputs

- 用户目标：序列设计、约束设计、链级设计、score-only、概率输出。
- 结构输入：PDB/backbone、链 ID、残基编号、缺失残基情况、是否来自 RFdiffusion。
- 约束输入：设计链、固定链、固定位置、tied positions、omit AA、PSSM、bias。
- 采样输入：`num_seq_per_target`、`sampling_temp`、`seed`、`batch_size`、`model_name`。
- 下游需求：是否需要结构折叠验证、复合物评估、序列多样性筛选或实验候选排序。
- 端到端上游产物：RFdiffusion backbone PDB、`.trb`、设计 ID、contig 映射，或用户提供的 backbone PDB/mmCIF。

# outputs

- 召回决策：是否使用 ProteinMPNN，以及 `sequence_design`、`constrained_design` 或 `score_only` 模式。
- 执行计划：输入 PDB/JSONL、约束文件、模型权重、采样参数、输出目录。
- 结果产物：FASTA、score、概率文件、日志和失败诊断。
- 下游交接：将设计 FASTA、score/global_score、probability/score 文件、backbone ID、sequence ID 和约束记录送入 SimpleFold/OpenFold/ESMFold 单体验证，或送入 Protenix/AlphaFold3 做复合物验证。

# procedure

1. 判断用户是否已有 backbone；若没有，先规划 RFdiffusion 或结构来源。
2. 若是端到端 workflow，解析 `starting_point` 和 `upstream_artifacts`：`no_backbone` 需要 RFdiffusion 产物，`backbone_pdb` 可直接进入本阶段，`designed_sequence` 跳过本阶段。
3. 解析设计范围：哪些链要设计，哪些链/残基必须固定，是否需要 tied positions 或氨基酸限制。
4. 选择输入方式：单个 PDB 直接运行；批量或复杂约束先生成 JSONL。
5. 检查 PDB 链 ID、残基编号、缺失坐标、权重目录和输出目录。
6. 生成 `protein_mpnn_run.py` 命令，显式写出采样数量、温度、seed 和约束文件。
7. 解析 observation：FASTA 数量、score 分布、约束是否生效、PDB/JSONL 是否报错。
8. 把高分或多样化候选送入结构预测模型验证可折叠性和功能相关结构指标。

# constraints

- ProteinMPNN 的输入核心是结构骨架，不是纯 FASTA。
- `chain_M` 是设计位置 mask；不要把它当作 padding 或普通 attention mask。
- 固定位置和设计链必须与 PDB 残基编号一致。
- ProteinMPNN 只给序列候选和分数，不保证最终折叠、结合或表达成功。
- 本卡只声明 `sequence_design` stage contract；端到端 workflow 可以复用同一上游/下游产物字段接入其它设计或验证工具。

# next_phase_recommendation

- 对每个设计序列，使用 SimpleFold 或 ESMFold 快速筛选，再用 OpenFold 做高置信度复核。
- 对 binder 或复合物候选，使用 Protenix/AlphaFold3 或其他复合物结构工具验证界面；用户显式指定 AlphaFold3 时不要改走 Protenix。
- 若序列多样性不足，调整 `sampling_temp`、固定位置和 omit/bias 约束。
- 若来自 RFdiffusion，应把骨架 ID、序列 ID 和后续结构验证结果保持可追踪。
- 端到端候选排序应同时保留 backbone PDB、ProteinMPNN FASTA、score/global_score、预测结构路径和失败阶段。

# fallback

- PDB 解析失败：清理 PDB、修正链 ID、去除异常原子并补齐 backbone 坐标。
- 约束不生效：检查 JSONL 字段、链名和残基编号映射。
- 生成序列质量差：调整温度、固定位置、设计链，或回到 RFdiffusion 重新生成骨架。
- 显存或时间不足：减少 `num_seq_per_target`、降低 batch，先做小规模候选。
