# description

ProToken 规划知识用于判断何时需要把蛋白结构离散化为结构 token、从 token 重建 PDB，或为 PT-DiT 提供结构词表与解码后端。

# when_to_use

- 用户有 PDB，需要结构 token、vq code indexes 或结构重建。
- 用户正在运行 PT-DiT，需要 ProToken embedding、decoder 或 checkpoint 对齐。
- 用户研究蛋白结构离散表示、VQ tokenizer 或 token-based generation。
- 不用于单独完成序列到结构预测或 backbone-to-sequence 设计。
- 若目标是 ProToken + AA embedding 的 de novo co-design、RePaint 或 latent evolution，优先转 PT-DiT；若目标是 FASTA folding，优先转 AlphaFold/OpenFold/AlphaFold3/Protenix。
- 当端到端 workflow 包含 `tokenization`、`structure_reconstruction` 或 PT-DiT 后处理阶段时，ProToken 是 tokenizer/decoder 支撑节点，而不是主结构验证器。

# inputs

- 任务模式: encode、decode、PT-DiT support。
- 生物输入: PDB 或 vq_code_indexes。
- 模型输入: ProToken checkpoint、embedding 文件、padding_len。
- 输出需求: code indexes、重建 PDB、aux 文件。
- 端到端上游产物: PDB/backbone 结构、PT-DiT protoken indexes 或 latent generation 结果；下游通常是 PT-DiT、结构重建 QC 或结构验证模型。

# outputs

- 调用决策: 是否使用 ProToken。
- 执行计划: infer/decode script、checkpoint、padding_len、输出目录。
- 结果产物: `vq_code_indexes.pkl`、reconstructed PDB、input features、aux。
- 下游交接: 将 `vq_code_indexes.pkl`、reconstructed PDB、aux、padding_len、codebook/checkpoint 版本交给 PT-DiT、几何 QC、SimpleFold/OpenFold 或 AlphaFold3/Protenix 复核。

# procedure

1. 确认输入是蛋白结构或结构 token。
2. 若是端到端 workflow，确认本阶段是 `tokenization`、`structure_reconstruction` 还是 `pt_dit_support`，并记录上游/下游候选 ID。
3. 判断需要 encode、decode 还是与 PT-DiT 联动。
4. 检查 `padding_len` 是否覆盖真实残基数。
5. 检查 checkpoint、codebook 和 embedding 是否配套。
6. 运行对应脚本。
7. 检查 token 长度、PDB 输出和 aux 信息。

# constraints

- `padding_len` 必须大于等于有效残基数。
- PDB 质量会影响 tokenization。
- ProToken checkpoint 与 token indexes 必须来自同一词表。
- 与 PT-DiT 联动时 `nres` 和 ProToken padding 要一致。
- ProToken 是结构 tokenizer / reconstruction 组件，不应把它识别成独立结构预测模型或 ProteinMPNN inverse folding 模型。
- 本卡只声明 tokenizer/decoder stage contract；端到端 workflow 的设计起点、结构验证和 ranking/report 由对应模型卡或 workflow 层承担。

# next_phase_recommendation

- token indexes 可进入 PT-DiT 生成、插值或 RePaint。
- 重建 PDB 应做几何检查和结构可视化。
- 批量结构 tokenization 可先小规模抽样验证。
- 若重建 PDB 要作为候选进入端到端验证，应保留 token ID、structure ID、checkpoint/codebook 版本和下游验证结果映射。

# fallback

- 残基过长时提高 padding 或切分结构。
- checkpoint 缺失时仅生成任务计划，不执行推理。
- 重建异常时先检查 PDB 链、缺失原子和 codebook 一致性。
