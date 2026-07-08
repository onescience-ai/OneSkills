# description

LaProteina 的规划知识用于把蛋白结构生成目标拆解为无条件长度采样、CATH/长度条件生成、motif scaffolding、binder/multimer 扩展和后续 designability 验证等阶段，并选择相应配置、checkpoint 和评估策略。

# when_to_use

- 用户要求从头生成指定长度的蛋白结构或骨架。
- 用户给出 motif，希望围绕 motif 生成 scaffold。
- 用户需要批量采样结构并评估 designability、codesignability 或 novelty。
- 当前 workflow 阶段是 `protein_backbone_generation` 或 `motif_scaffolding`。
- 不在用户只给 FASTA 要求折叠时使用；此时应转向结构预测模型。
- 不在小分子 docking 或医学问答任务中使用。

# inputs

- 生成目标：无条件、长度条件、CATH 条件、motif scaffolding、binder 或 multimer。
- 结构条件：生成长度、CATH code、motif PDB、contig、atom selection mode。
- 模型资源：主 checkpoint、autoencoder checkpoint、可选 autoguidance checkpoint。
- 采样参数：nsteps、self_cond、guidance_w、ag_ratio、nsamples、job_id。
- 评估需求：是否计算 designability、codesignability、motif RMSD、novelty 或 FID。

# outputs

- 召回决策：使用 LaProteina，以及具体配置名。
- 执行计划：Hydra 配置、checkpoint、生成长度、motif 参数和输出目录。
- 结果产物：生成 PDB、motif 信息 CSV、评估 CSV、日志。
- 下游交接：把结构候选交给 ProteinMPNN、折叠验证、结构聚类或可视化流程。

# procedure

1. 判断用户目标是结构生成还是序列折叠。
2. 选择模式：无条件长度采样、条件采样或 motif scaffolding。
3. 根据模式选择 `inference_ucond_tri`、motif 配置或自定义配置。
4. 检查 checkpoint 与 autoencoder checkpoint 是否存在并匹配。
5. 检查 GPU、数据目录和输出目录。
6. 对 motif 任务检查链 ID、残基编号、contig 和 atom selection mode。
7. 生成命令并显式设置 `--config_name`、`--job_id`、`--data_path`。
8. 运行后检查 PDB 数量、长度、日志和可选评估指标。
9. 将成功结构进入序列设计和结构验证阶段。

# constraints

- 推理环境必须有 GPU。
- checkpoint、autoencoder 与配置中的 latent 维度必须一致。
- motif 约束不能凭空编造，必须来自用户输入或文件。
- 不能把生成 PDB 直接视为最终可表达蛋白，需要后续序列与结构验证。
- 大规模评估要和生成阶段分离规划，避免一次任务内资源爆炸。

# next_phase_recommendation

- 对骨架候选运行 ProteinMPNN 或等价序列设计模型。
- 对设计序列运行 SimpleFold/OpenFold/Protenix 等结构验证模型。
- motif scaffolding 应计算 motif RMSD 或固定原子保真度。
- 批量候选应按长度、设计性、结构冲突和 novelty 汇总排序。

# fallback

- CUDA 不可用：不要继续执行推理，改为环境修复或申请 GPU 节点。
- checkpoint 缺失：切换到可用配置或提示准备对应权重。
- motif 解析失败：输出 motif CSV 检查，重新核对链 ID、残基编号和 atom selection mode。
- 显存不足：降低 `nsamples`、`max_nsamples_per_batch` 或生成长度。
- 生成质量差：增加 `nsteps`、调整 guidance 或换用带 pair update 的配置。
