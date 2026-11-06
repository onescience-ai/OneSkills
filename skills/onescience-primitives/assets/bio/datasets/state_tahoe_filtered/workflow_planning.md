## description

为State Tahoe 过滤后 smoke 数据选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

State Tahoe 本地 c36/c39/c44 单细胞药物扰动 smoke 数据，描述药物及剂量组合、细胞系、plate 和 HVG/State 表示，用于受控接口检查与局部泛化评测。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/State_dataset/State-Tahoe-Filtered-smoke`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：所选表达/embedding、药物及剂量、细胞系、plate、control 与 split；保留文件分支和原始细胞索引。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 确认 smoke 使用范围，检查 drug 与 drugname_drugconc 语义及 control。
4. 核对基因轴、表示维度和外部 holdout 配置，建立不泄漏条件的分割。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

不将 c36/c39/c44 名称自行解释为 train/validation/test。正式划分须绑定 Tahoe 实验配置或显式固定细胞系、药物/剂量和 plate holdout；smoke 结论只覆盖本地子集。

同一药物不同剂量不可静默合并；相同基因维度不证明三文件基因顺序一致。X_hvg/X_state 与 X 采用不同坐标语义，使用前核对。

## next_phase_recommendation

c36/c39/c44 选择 → 基因轴和条件解析 → 显式 holdout → State adapter；不能用 Parse 的 cytokine 列协议替代 Tahoe 药物协议。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

没有可靠 holdout 时只做 smoke 接口检查并声明未进行完整 Tahoe 评测；剂量无法解析时保留原始组合字符串，不自行 eval 执行。
