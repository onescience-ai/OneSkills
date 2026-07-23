# description

ProteinMPNN 规划知识用于从蛋白骨架与设计约束构建序列训练、打分、普通采样或 tied-position 采样代码。

# when_to_use

- 给定 N/CA/C/O 骨架或 CA-only 骨架，需要设计氨基酸序列。
- 需要评估已知序列在给定骨架上的 log probability。
- 需要固定链/位点、omit AA、PSSM 或 tied positions。
- 不用于从序列预测结构。

# inputs

- 骨架坐标或由 `parse_PDB` 得到的结构字典。
- `tied_featurize` 所需 chain、fixed position、omit-AA、PSSM、tied-position 与 bias 设置。
- 与 full-backbone/CA-only 模式匹配的模型配置和 checkpoint。
- 训练的 `S`、mask 和 loss 选择，或采样 temperature/bias 参数。

# outputs

- `forward` 的 `(B,L,num_letters)` log probability。
- `sample`/`tied_sample` 的序列与采样诊断字典。
- 设计位点、固定位置、decoding order 和约束的显式记录。

# procedure

1. 解析骨架并确认 full-backbone 或 CA-only 模式。
2. 用 `tied_featurize` 构造 `X`、`S`、`mask`、`chain_M`、`residue_idx`、`chain_encoding_all` 和约束张量。
3. 按源码签名构造 `ProteinMPNN`，加载匹配 checkpoint。
4. 训练/打分调用 `forward`，并用 `loss_nll` 或 `loss_smoothed`。
5. 普通设计调用 `sample`；存在 tied positions 时调用 `tied_sample`。
6. 将 token 转为序列，并核验固定位置和链约束未被破坏。

# constraints

- 直接使用 `protein_mpnn_utils.py` 的类、函数和张量约定。
- full-backbone 的原子顺序必须为 N、CA、C、O。
- `chain_M` 是设计 mask，不等同于 padding mask。
- CA-only 配置与 checkpoint 必须配套。

# next_phase_recommendation

- 将生成序列交给结构预测模型验证可折叠性。
- 按 log probability、约束满足率和结构结果排序。
- 训练任务补充数据增强、optimizer 和 checkpoint runtime。

# fallback

- 序列违反固定约束时检查 `chain_M` 与 tied feature 张量。
- checkpoint 加载失败时核对 `protein_mpnn_utils.py` 实现及构造参数。
- 几何结果异常时检查原子顺序、缺失残基和 chain encoding。
