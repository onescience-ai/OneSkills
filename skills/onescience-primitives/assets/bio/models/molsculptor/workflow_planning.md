# description

MolSculptor 规划知识用于把小分子生成、分子优化、相似性约束和 docking reward 筛选任务组织成可执行的 MolSculptor inference/training/case 流程。

# when_to_use

- 用户目标是 SMILES 生成、小分子优化、药物设计辅助或多目标筛选。
- 输入包含初始小分子、SMILES、PDBQT receptor、docking case 或分子性质 reward。
- 用户明确需要 latent diffusion、graph encoder/decoder 或 NSGA-II 分子选择。
- 不用于蛋白结构预测、蛋白序列设计或基因组序列任务。
- 若目标是蛋白结构预测或蛋白生成，应转 AlphaFold/OpenFold/AlphaFold3/Protenix/RFdiffusion/ProteinMPNN/PT-DiT；若目标是 DNA token 语言模型，应转 Evo2。

# inputs

- 任务模式: de novo generation、dual optimization、autoencoder pretrain、diffusion training。
- 分子输入: SMILES、init molecule pickle、case 配置。
- reward 输入: LogP/QED/SA/Tanimoto/docking 脚本和 receptor。
- 运行输入: checkpoint、config、输出目录、采样策略。

# outputs

- 调用决策: 是否使用 MolSculptor。
- 执行计划: inference 脚本、case 目录、checkpoint、reward 和采样参数。
- 结果产物: generated SMILES、性质分数、docking reward、候选分子集合。
- 下游建议: 化学有效性过滤、ADMET/docking 复核或合成可行性评估。

# procedure

1. 确认任务是小分子而不是蛋白或 DNA。
2. 判断是 de novo、优化、预训练还是 diffusion 训练。
3. 准备 SMILES/图特征、case 配置和 checkpoint。
4. 选择采样策略与 reward。
5. 运行生成或优化脚本。
6. 检查 SMILES 有效性、reward 分布、重复分子和约束。
7. 输出候选并进入下游筛选。

# constraints

- 分子图大小不能超过 padding/config 支持范围。
- RDKit、OpenBabel、DSDP 等外部依赖必须可用。
- docking reward 依赖 case-local 路径，不应跨 case 混用。
- checkpoint、vocab 和 config 必须一致。
- MolSculptor 的输入是 SMILES/分子图/药物设计 case，不应复用蛋白 datapipe、OpenFold batch、Protenix feature dict 或 Evo2 tokenizer。

# next_phase_recommendation

- 对候选分子做去重、有效性、QED/SA/LogP 和 docking 复核。
- 高分候选可进入 ADMET、合成路线或分子动力学验证。
- 多目标任务建议保留 Pareto front 供人工筛选。

# fallback

- docking 不可用时先用 RDKit property reward 和 similarity 筛选。
- 无 checkpoint 时只做数据准备或训练配置生成。
- 无效 SMILES 过多时收紧 standardize/filter 或调整采样温度与 top-k/top-p。
