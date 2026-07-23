# description

OpenFold 规划知识用于从真实 config 和 OpenFold feature dict 构建 `AlphaFold` 训练或推理代码，并正确处理 monomer/multimer、template、Extra MSA 与 recycling。

# when_to_use

- 已有 OpenFold 专用 feature dict，需要结构预测或训练前向。
- 需要 PyTorch AlphaFold2 风格 Evoformer 与 StructureModule。
- 需要复用 autograd、activation checkpointing 或长序列 chunking。
- 不用于直接接收 FASTA 字符串或通用蛋白 batch。

# inputs

- 含 `globals` 与 `model` 的真实 OpenFold config。
- 与 config 对应的 feature dict，所有 tensor 末维为 recycling 维。
- 匹配的 model state dict。
- 训练时的损失函数/标签；推理时的 device、precision 与 no-grad 设置。

# outputs

- `AlphaFold(config)` 模型与 checkpoint 加载代码。
- forward 结果字典，包括 atom37 结构、表征、recycle 计数和配置启用的辅助 heads。
- 训练 loss 调用或推理结果后处理所需的字段契约。

# procedure

1. 从 config 确认 monomer、multimer 或 seqemb 模式及 template/Extra MSA 开关。
2. 原始序列或结构输入先召回 `openfold_data_pipeline` 构造对应 feature dict，再校验字段和 recycling 末维一致。
3. 实例化 `AlphaFold(config)` 并严格加载匹配 state dict。
4. 训练时保持 autograd，调用 `outputs = model(batch)` 后接项目损失。
5. 推理时设置 eval/no-grad，调用同一 forward。
6. 只读取 outputs 中实际存在的辅助 head 字段。

# constraints

- 直接使用 `onescience.models.openfold.model.AlphaFold`。
- 不把 FASTA、PDB 路径直接传给 `AlphaFold.forward`。
- config 的模式必须与 feature pipeline 和 checkpoint 一致。
- recycling 轮数由 batch 末维决定。

# next_phase_recommendation

- 推理结果进入结构序列化与置信度计算。
- 训练结果进入 loss aggregation、优化器和 checkpoint 流程。
- 长序列任务先做单样本显存预检。

# fallback

- 缺字段时回到 `openfold_data_pipeline` 补齐，不在模型调用代码中伪造字段。
- 显存不足时使用源码已有 chunking/checkpointing 并减小 batch/MSA/template 规模。
- checkpoint 不匹配时恢复原 config，不重命名模型层绕过错误。
