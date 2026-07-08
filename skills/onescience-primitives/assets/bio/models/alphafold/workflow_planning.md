# description

AlphaFold 规划知识用于判断何时调用原版 AF2/Multimer JAX 推理流水线，并把蛋白 FASTA、数据库、模板日期、preset、参数目录和输出目录组织成可执行推理任务。

# when_to_use

- 用户要求复用原版 AlphaFold v2 或 AlphaFold-Multimer 推理。
- 输入是蛋白 FASTA，目标是结构预测、pLDDT、pTM、ipTM、PAE 或 ranked PDB。
- 用户明确需要 AF2/Multimer 数据库检索、template search 或 Amber relaxation。
- 当 `workflow_type=protein_design_to_structure_validation` 且用户显式要求原版 AlphaFold/Multimer JAX 路线作为 AF2-style 复核时，可作为结构验证阶段；若用户未指定原版 JAX，OpenFold 通常是 PyTorch AF2 路线。
- 不用于 AF3 多分子复合物、核酸、配体结构预测；这类需求优先 AlphaFold3 或 Protenix。
- 不用于 OpenFold/PyTorch AF2 batch、训练或微调；这类需求优先 OpenFold。

# inputs

- 任务类型: monomer、monomer_ptm、multimer。
- 生物输入: FASTA 文件、链信息、模板日期限制。
- 资源输入: 参数目录、数据库目录、外部搜索工具路径、输出目录。
- 运行策略: 是否 relax、是否复用 features、是否批量调度。
- 端到端上游产物: ProteinMPNN 设计 FASTA、候选 ID、可选 SimpleFold/OpenFold 初筛结果；需要另行准备 AlphaFold v2 数据库、模板日期和参数目录。

# outputs

- 调用决策: 是否使用 alphafold。
- 执行计划: run script、preset、数据库 preset、模板日期、输出路径。
- 结果产物: feature pickle、result pickle、ranked PDB、confidence JSON、timings。
- 下游交接: 将 ranked PDB、confidence JSON、PAE/pLDDT/pTM/ipTM、候选 ID 和 timings 交给 ranking/report；复合物或含配体候选转 AlphaFold3/Protenix。

# procedure

1. 确认输入是蛋白序列而不是核酸、小分子或 backbone design。
2. 若是端到端 workflow，确认本阶段是用户显式要求的 `af2_jax_validation`，并核对上游 FASTA 是否来自设计序列或候选筛选。
3. 判断单体或多体，选择 `model_preset`。
4. 检查数据库、外部工具、参数和模板日期。
5. 生成 run_alphafold 命令。
6. 运行后检查 ranked PDB、pLDDT、pTM/ipTM 和 PAE。
7. 根据结果决定是否 relax、复核或进入下游筛选。

# constraints

- `model_preset` 必须和 FASTA 链组织一致。
- 数据库检索不可在缺少数据库和工具的环境中假定可运行。
- multimer 不应被简化为 monomer 拼接输入。
- 输出结构置信度不足时，不应直接进入实验结论。
- AlphaFold 是 JAX/Haiku AF2 路线，不应与 OpenFold PyTorch batch 或 Protenix/AlphaFold3 AF3 feature dict 混用。
- 本卡只声明原版 AF2 JAX 验证 stage contract；端到端 workflow 的骨架生成、序列设计、工具预检和候选排序不在本卡内实现。

# next_phase_recommendation

- 高置信 ranked PDB 可进入结构分析、突变设计或 docking。
- 多体任务建议结合 ipTM、PAE 和接口质量筛选。
- 低置信区域可用 AlphaFold3/Protenix 或实验信息复核。

# fallback

- 缺少完整数据库时使用 `reduced_dbs` 或复用已有 features。
- GPU/内存不足时降低 batch/subbatch 或拆分长序列。
- multimer pipeline 失败时先单链验证 FASTA 和 MSA，再恢复多链输入。
