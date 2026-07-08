# description

Protenix 的规划知识用于判断何时需要 OneScience/Protenix PyTorch 路线的 AF3-style 复合物结构预测，并把蛋白、核酸、配体、MSA/template、checkpoint、采样参数和结果筛选组织成可执行计划。

# when_to_use

- 用户要求预测蛋白-蛋白、蛋白-核酸、蛋白-配体或多实体复合物结构，并且需要 Protenix/OneScience PyTorch 入口。
- 用户明确提到 Protenix、`inference_unified.py`、Protenix checkpoint、Protenix JSON、CIF/PDB 复合物输出、扩散采样或 ligand/CCD。
- 用户未指定 AlphaFold3，且当前可用资产是 Protenix checkpoint/Protenix JSON 时，可优先选择 Protenix。
- 用户明确提到 AlphaFold3、AF3 JAX、`run_alphafold.py`、`model_dir` 或官方 AF3 data pipeline 时，不选择 Protenix，转 AlphaFold3。
- 用户已有 ProteinMPNN 设计序列或候选结构，需要验证复合物结合构象。
- 用户输入包含 RNA、DNA、配体、修饰残基或多实体约束。
- 当 `workflow_type=protein_design_to_structure_validation` 且当前阶段是 `complex_validation`，并且用户未显式指定 AlphaFold3 或当前资产是 Protenix checkpoint/JSON 时，Protenix 是默认复合物验证器。
- 若端到端任务只是单体设计序列快速筛选，优先 SimpleFold；若需要 AF2/MSA/template 复核，转 OpenFold/AlphaFold。
- 不在单条蛋白 FASTA 快速折叠时优先使用；可先召回 SimpleFold/ESMFold/OpenFold。

# inputs

- 用户目标：复合物预测、配体结合、蛋白-核酸结构、binder 验证、多 seed 候选采样。
- 生物输入：蛋白序列、RNA/DNA 序列、配体/CCD 信息、链 ID、实体关系、MSA/template。
- 运行输入：Protenix JSON、Protenix checkpoint、`use_msa`、`dtype`、cycle、diffusion sample/step、seed。
- 模型选择输入：用户是否显式指定 Protenix 或 AlphaFold3、资产是 Protenix checkpoint 还是 AF3 `model_dir`、入口是 `inference_unified.py` 还是 `run_alphafold.py`。
- 资源输入：GPU/显存、化学组件资源、输出目录、attention 后端。
- 上下游输入：上游可来自 ProteinMPNN/RFdiffusion 设计候选；下游可进入界面筛选、接触分析或实验排序。
- 端到端上游产物：ProteinMPNN FASTA、RFdiffusion backbone/target PDB、binder-target 链映射、配体/核酸/CCD 信息、候选 ID；需要整理为 Protenix JSON。

# outputs

- 召回决策：是否使用 Protenix，以及 `complex_structure_prediction`、`ligand_complex`、`nucleic_acid_complex` 或 `design_validation` 模式。
- 执行计划：输入 JSON 生成/校验、checkpoint、采样参数、MSA/化学组件资源和输出目录。
- 结果产物：CIF/PDB、置信度、接触/排名结果、日志和失败诊断。
- 下游交接：将 CIF/PDB、ranking/confidence、接触/界面信息、实体/链映射、候选 ID 和失败诊断交给界面筛选、候选排序，或回退到序列/骨架再设计。

# procedure

1. 判断用户目标是否包含多实体复合物、核酸、配体或 AF3-style 结构预测需求。
2. 若是端到端 workflow，确认 `current_stage=complex_validation`，并把上游 RFdiffusion/ProteinMPNN 产物转换为 Protenix JSON，而不是混用 SimpleFold/OpenFold batch。
3. 先做模型选择：Protenix/OneScience PyTorch 入口、Protenix checkpoint 或 Protenix JSON 走 Protenix；AlphaFold3/JAX/`model_dir`/`run_alphafold.py` 走 AlphaFold3。
4. 将用户输入整理为 Protenix JSON：实体类型、链 ID、序列、配体/CCD、MSA/template 字段。
5. 选择运行模式：带 MSA 精细推理、无 MSA 快速连通性检查、多 seed 采样或设计候选验证。
6. 检查 JSON schema、checkpoint、化学组件资源、MSA 可用性、输出目录和 GPU 显存。
7. 生成 `inference_unified.py` 命令，显式写出 dtype、cycle、sample、step、seed 和 `use_msa`。
8. 解析 observation：结构文件、采样数量、置信度、接触结果、JSON/化学组件/显存错误。
9. 根据复合物质量决定下一步：保留高置信度候选、调整 MSA/采样，或回到 RFdiffusion/ProteinMPNN 重新设计。

# constraints

- Protenix 输入必须是支持的 JSON/feature 语义，不接受裸 FASTA 直接推理。
- AF3 JSON、Protenix JSON 和模型 feature dict 不可假定完全互换。
- 配体、修饰残基、离子和核酸必须有明确实体字段和化学组件支持。
- Protenix 是结构预测/验证模型，不负责 backbone 生成或序列采样。
- Protenix 不覆盖 AlphaFold3 JAX 执行；显式 AlphaFold3 请求必须保留为 AlphaFold3 模型选择。
- 本卡只声明 PyTorch/OneScience AF3-style 复合物验证 stage contract；后续其它端到端 workflow 可复用 JSON/structure/confidence/ranking 交接字段。

# next_phase_recommendation

- 高置信度复合物进入界面接触、冲突、结合构象和实验候选排序。
- 低置信度 binder 候选可回到 ProteinMPNN 调整序列，或回到 RFdiffusion 重新生成骨架。
- 只有单蛋白序列且无需复合物时，先判断是否需要 AF2/MSA/template；否则改用 OpenFold、SimpleFold 或 ESMFold。
- 多 seed 输出应按置信度、界面合理性和结构多样性筛选。
- ranking/report 阶段应汇总 RFdiffusion backbone ID、ProteinMPNN sequence ID、Protenix JSON、结构路径、置信度和失败原因。

# fallback

- JSON 字段错误：按实体类型重建输入 JSON，明确链 ID、序列、配体和 MSA 字段。
- 化学组件失败：检查 CCD/RDKit 资源、配体命名和修饰残基定义。
- 显存不足：降低 `sample_diffusion.N_sample`、`N_step`、`model.N_cycle`，使用 `bf16` 或拆分候选。
- 复合物置信度低：增加 MSA/template、尝试多 seed，或把设计退回 ProteinMPNN/RFdiffusion。
