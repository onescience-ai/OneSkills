# description

SimpleFold 的规划知识用于判断何时使用快速单序列折叠模型，并把 FASTA、checkpoint、采样参数、输出置信度和后续复核模型组织成可执行计划。

# when_to_use

- 用户有蛋白 FASTA，希望快速得到结构 PDB 和 pLDDT。
- 用户从 ProteinMPNN 得到大量设计序列，需要先做低成本结构初筛。
- 用户不具备完整 MSA/template 数据库，或当前任务只需要快速近似结构。
- 用户明确提到 SimpleFold、快速折叠、单序列结构预测。
- 当 `workflow_type=protein_design_to_structure_validation` 且当前阶段是 `fast_monomer_validation` 或 `design_screening` 时，SimpleFold 是设计序列的快速单体结构验证器。
- 若端到端任务的验证对象是 binder-target、蛋白-核酸、蛋白-配体或多实体复合物，应跳过 SimpleFold 并转 Protenix/AlphaFold3。
- 不在用户需要复合物、配体或核酸结构时使用；此类任务召回 Protenix/AlphaFold3，并按用户指定入口、资产和输入协议选择具体模型。

# inputs

- 用户目标：快速结构预测、设计候选初筛、单序列折叠、批量 FASTA 评估。
- 序列输入：FASTA 文件或目录、候选 ID、序列长度、是否来自 ProteinMPNN。
- 运行输入：checkpoint 目录、`simplefold_model`、`num_steps`、`tau`、`nsample_per_protein`、`backend`、`output_format`。
- 资源输入：GPU/CPU、输出目录、批量规模、时间限制。
- 下游需求：是否需要 OpenFold 高精度复核、Protenix/AlphaFold3 复合物验证或实验候选排序。
- 端到端上游产物：ProteinMPNN 设计 FASTA、backbone ID、sequence ID、score/global_score；运行前应把多序列 FASTA 拆成单条 FASTA 集合。

# outputs

- 召回决策：是否使用 SimpleFold，以及 `fast_structure_prediction` 或 `design_screening` 模式。
- 执行计划：FASTA 输入、checkpoint、采样参数、输出目录、是否输出 pLDDT。
- 结果产物：PDB、pLDDT/置信度、日志、失败诊断。
- 下游交接：将 PDB/CIF、pLDDT/置信度、结构数量、stdout/stderr 日志、候选 ID 和失败原因交给 ranking/report；高价值候选可再送入 OpenFold 或 Protenix/AlphaFold3 复核。

# procedure

1. 判断用户是否需要快速蛋白序列折叠，而不是完整 AF2-style 或复合物推理。
2. 若是端到端 workflow，确认 `current_stage=fast_monomer_validation`，并检查上游 FASTA 是否来自 ProteinMPNN 或用户设计序列。
3. 规范 FASTA：检查氨基酸字符、候选 ID、批量目录和序列长度；ProteinMPNN 多序列 FASTA 先拆成单条 FASTA。
4. 选择运行参数：模型规模、步数、温度、每序列采样数、后端和输出格式。
5. 检查 checkpoint、输出目录、GPU/CPU 资源和是否需要 `--plddt`。
6. 生成 CLI 或 `inference.py` 命令，记录输入、参数和预期输出。
7. 解析 observation：PDB 数量、pLDDT、跳过序列、格式错误、checkpoint 或显存错误。
8. 按 pLDDT、结构完整性和候选来源决定是否进入 OpenFold 或 Protenix/AlphaFold3 精筛。

# constraints

- SimpleFold 输入是蛋白序列 FASTA，不直接处理 RFdiffusion backbone。
- SimpleFold 是快速折叠/初筛工具，不保证复合物、配体或界面构象准确。
- 大规模候选应分批运行，并保留序列 ID 与输出 PDB 的映射。
- 对最终实验候选，建议用 OpenFold、Protenix 或其他高置信度方法复核。
- 端到端管线中 SimpleFold 结构数为 0 不能标记为成功；含离线 ESM/CCD/Boltz 资产准备时，setup/preflight 仍由 workflow/runtime 层统一负责。

# next_phase_recommendation

- 高 pLDDT 且结构合理的单链候选可进入 OpenFold 复核或实验候选排序。
- 来自 RFdiffusion/ProteinMPNN 的候选应把骨架 ID、序列 ID、SimpleFold 分数串联记录。
- binder/复合物候选应进入 Protenix/AlphaFold3 或复合物验证工具；用户显式要求 AlphaFold3 时不要改走 Protenix。
- 低 pLDDT 候选可回到 ProteinMPNN 调整序列或回到 RFdiffusion 调整骨架。
- ranking/report 阶段应汇总 ProteinMPNN score、SimpleFold pLDDT、结构路径、失败原因和可复现输入 FASTA。

# fallback

- FASTA 格式错误：清理非法字符、空序列和重复 header。
- 输出为空：检查 `output_format`、输出目录权限、checkpoint 目录和后端。
- 显存不足：减少批量、降低 `num_steps`、减少 `nsample_per_protein` 或切换设备。
- 结构置信度低：改用 OpenFold/ESMFold 对照，或回到设计阶段重新采样。
