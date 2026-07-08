# description

AlphaFold3 规划知识用于判断何时调用 AF3 JAX 复合物结构预测路线，并把 JSON 输入、data pipeline、模型参数、attention 实现、recycle 和 diffusion sample 组织成可执行计划。

# when_to_use

- 用户输入包含蛋白、RNA、DNA、配体、离子或共价连接的复合物。
- 用户需要 AF3-style diffusion 结构预测、PAE/PDE/pLDDT、contact probability 或 ranking。
- 用户明确希望复用 JAX/Haiku AlphaFold3 示例脚本。
- 当 `workflow_type=protein_design_to_structure_validation` 且当前阶段是 `complex_validation`，并且用户显式要求 AlphaFold3/AF3 JAX/官方 data pipeline 时，AlphaFold3 是 binder-target、蛋白-核酸、蛋白-配体或多实体复合物验证器。
- 若端到端任务只是单体快速筛选，优先 SimpleFold；若是 PyTorch/OneScience AF3-style 组件路线，优先 Protenix。
- 若目标是 PyTorch/OneScience 组件级改造，优先转 Protenix。
- 若目标是 AlphaFold v2/AF2 FASTA + MSA/template 推理，优先转 AlphaFold；若目标是 OpenFold/PyTorch AF2 训练或微调，优先转 OpenFold。

# inputs

- 分子输入: AF3 JSON、MSA/template/CCD/bonds 信息。
- 运行输入: `model_dir`、`output_dir`、data pipeline 开关、inference 开关。
- 性能输入: attention 实现、recycle 数、diffusion sample 数、bucket/token 规模。
- 输出需求: 是否保存 embeddings、distogram、PAE/PDE。
- 端到端上游产物: ProteinMPNN 设计序列、可选 RFdiffusion backbone/target PDB、binder-target 实体信息、配体/核酸/CCD 信息；需要整理为 AF3 JSON。

# outputs

- 调用决策: 是否使用 AlphaFold3。
- 执行计划: JSON 路径、pipeline/inference 开关、attention 策略、输出目录。
- 结果产物: 结构文件、ranking、confidence JSON、PAE/PDE、可选 embeddings/distogram。
- 下游交接: 将结构文件、ranking、confidence JSON、PAE/PDE/pLDDT、contact probability、实体/链映射和失败诊断交给界面筛选、候选排序或 Protenix 交叉验证。

# procedure

1. 确认输入是 AF3 支持的分子组合。
2. 若是端到端 workflow，确认 `current_stage=complex_validation`，并把上游设计序列、target、配体或核酸信息整理为 AF3 JSON，而不是直接接收 ProteinMPNN FASTA。
3. 检查 JSON 是否已有 MSA/template/CCD 信息。
4. 根据资源选择 `run_data_pipeline` 与 `run_inference`。
5. 选择 `flash_attention_implementation`，兼容优先用 `xla`。
6. 设置 recycle 和 diffusion sample。
7. 运行后检查 ranking、pLDDT、PAE/PDE、配体和共价键几何。

# constraints

- JSON schema 和化学组件数据必须一致。
- data pipeline 需要数据库和外部搜索工具。
- 长复合物会触发 bucket、pair embedding 和显存压力。
- AlphaFold3 与 Protenix 不共享 batch adapter。
- AlphaFold3 是 JAX/Haiku AF3 JSON 推理路线，不应把 Protenix 的 PyTorch/OneScience `One*` 组件注册需求路由到这里。
- 本卡只声明 AF3 JAX 复合物验证 stage contract；端到端 workflow 的设计、工具预检、Slurm 和候选排序由 workflow 层统一编排。

# next_phase_recommendation

- 高置信结构进入接口、配体结合和复合物稳定性分析。
- 低置信或高 PAE 区域建议调整输入、补充 MSA/template 或用 Protenix 复核。
- 配体任务建议增加化学有效性和手性检查。
- 来自 RFdiffusion/ProteinMPNN 的 binder 候选应保留 backbone ID、sequence ID、target chain、AF3 JSON 和结构验证分数，供 ranking/report 汇总。

# fallback

- attention 后端失败时切到 `xla`。
- 缺数据库时关闭 data pipeline 并提供预计算 MSA/template。
- 显存不足时减少 diffusion samples、避免保存 pair embeddings 或拆分任务。
