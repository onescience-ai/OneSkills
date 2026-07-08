# description

RFdiffusion 的规划知识用于判断何时需要生成或改造蛋白骨架，并把用户的设计目标转换为 contig、输入 PDB、热点残基、采样数量、输出前缀和后续序列设计步骤。

# when_to_use

- 用户要求从头生成蛋白骨架、指定长度范围生成 scaffold，或围绕结构 motif 生成新骨架。
- 用户给出靶标 PDB，希望生成 binder 或界面候选。
- 用户希望保留已有结构的一部分并做 partial diffusion。
- 用户需要的是 backbone 级别候选，而不是已经确定序列的结构预测。
- 当 `workflow_type=protein_design_to_structure_validation` 且 `starting_point=no_backbone`，或当前阶段是 `backbone_generation` 时，RFdiffusion 是端到端链路的默认起点。
- 若端到端任务已有 backbone PDB/mmCIF，应跳过 RFdiffusion 并进入 ProteinMPNN；若已有设计序列 FASTA，应直接进入结构验证模型。
- 不在用户只给 FASTA 并要求折叠时使用；该类任务召回 OpenFold、SimpleFold、ESMFold 或 Protenix。

# inputs

- 用户目标：无条件骨架、motif scaffolding、binder design、partial diffusion、对称设计。
- 结构输入：目标 PDB、motif PDB、链 ID、残基编号、热点残基、要保留或扩散的区域。
- 设计约束：contig 长度范围、固定片段、binder 长度、设计数量、是否保存轨迹。
- 资源输入：checkpoint 目录、输出前缀、GPU/显存、磁盘空间。
- 下游需求：是否需要 ProteinMPNN 设计序列、是否需要 SimpleFold/OpenFold/Protenix 验证结构。
- 端到端上下文：`workflow_type`、`starting_point`、`current_stage`、`upstream_artifacts`、`downstream_artifacts`；本阶段通常无上游模型产物，但可消费 target/motif PDB、contig 和 hotspot。

# outputs

- 召回决策：是否使用 RFdiffusion，以及对应的 `unconditional`、`motif_scaffolding`、`binder_design`、`partial_diffusion` 或 `symmetry_design` 模式。
- 执行计划：Hydra override 参数、contig 表达式、输入 PDB、热点残基、checkpoint 和输出目录。
- 结果产物：骨架 PDB、TRB、轨迹、日志和失败诊断。
- 下游交接：将 backbone PDB、`.trb`、contig 映射、设计 ID 和失败诊断交给 ProteinMPNN；后续再用 SimpleFold/OpenFold/AlphaFold3/Protenix 做结构或复合物验证。

# procedure

1. 判断用户是否需要“生成骨架”而不是“预测给定序列结构”。
2. 若是端到端 workflow，解析 `starting_point`：`no_backbone` 才进入本阶段；`backbone_pdb` 转 ProteinMPNN；`designed_sequence` 或 `complex_validation` 转结构验证。
3. 选择设计模式：无条件、motif、binder、partial diffusion 或对称设计。
4. 把生物约束转换为 contig：确认链 ID、残基编号、固定片段、可变长度和断链语法。
5. 检查输入 PDB、checkpoint、输出前缀、热点残基和 GPU 资源。
6. 生成 `run_inference.py` 命令，显式写出关键 Hydra override。
7. 解析 observation：骨架 PDB 数量、TRB、轨迹、contig 错误、PDB 编号错误、显存错误。
8. 若骨架生成成功，规划 ProteinMPNN 序列设计；若是 binder，再规划结构复合物验证和界面筛选。

# constraints

- RFdiffusion 输出通常是 backbone 候选，不是最终序列设计结果。
- contig 语法必须和输入 PDB 的链 ID、残基编号一致。
- binder 任务必须明确靶标链、binder 长度范围和可选热点；热点不能凭空编造。
- partial diffusion 的输入长度与设计长度必须一致或有明确映射。
- 本卡只声明 `backbone_generation` stage contract；端到端编排、工具预检、Slurm 和候选排序由 workflow 层统一处理，便于后续新增其它端到端 workflow。

# next_phase_recommendation

- 骨架生成成功后，优先召回 ProteinMPNN 设计序列。
- 生成序列后，用 SimpleFold、OpenFold 或 ESMFold 评估可折叠性；复合物或含配体场景用 Protenix。
- binder 任务应增加界面面积、接触残基、冲突和置信度筛选。
- motif scaffold 应检查 motif RMSD 或固定残基保留情况。
- 端到端排序表应保留 RFdiffusion backbone ID、PDB 路径、TRB 路径、contig 映射和后续 ProteinMPNN/验证阶段的候选 ID。

# fallback

- contig 解析失败：重新核对链 ID、残基编号和断链语法。
- 输入 PDB 报错：清理 PDB、保留必要链、统一残基编号并去除不支持的异质原子。
- 生成结构质量差：调整长度范围、热点、设计数量或 checkpoint。
- GPU/时间不足：减少 `num_designs`、缩短 contig、关闭轨迹输出，或先跑小规模试采样。
