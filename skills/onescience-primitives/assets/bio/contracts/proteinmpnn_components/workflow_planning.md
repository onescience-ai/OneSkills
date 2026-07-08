# description

该卡用于 inverse folding 和 RFdiffusion 后处理中的 ProteinMPNN 组件规划。

# when_to_use

- 已有蛋白骨架，需要设计序列。
- 需要固定链、固定位置、omit AA、PSSM 或 tied positions。
- 需要评估 backbone 对序列的 log probability。

# inputs

- PDB 或 backbone tensor `X`。
- 设计 mask、chain encoding、residue index。
- 采样温度和约束 JSON。

# outputs

- 设计序列。
- 每位点 log_probs/probabilities。
- 约束采样结果和失败原因。

# procedure

1. 解析 PDB 并检查主链原子。
2. 构造 ProteinMPNN feature batch。
3. 根据任务选择普通 sample 或 tied_sample。
4. 输出序列，并可进入后续结构评估或 relax。

# constraints

- 不把 ProteinMPNN 当结构预测模型。
- 不硬改 forward 表达约束，优先使用 helper JSON / runner 参数。
- 不混淆训练版和推理版同名实现。

# next_phase_recommendation

RFdiffusion 输出骨架后优先接本卡；若需要验证结构，后续接结构预测或打分流程。

# fallback

PDB 缺主链原子时先修复或过滤；约束 JSON 不合法时降级为无约束采样并报告差异。
