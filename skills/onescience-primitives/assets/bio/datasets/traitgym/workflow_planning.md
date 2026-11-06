## description

为TraitGym hg38 非编码变异效应评测选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

Carbon 本地 TraitGym Mendelian/complex traits 非编码变异评测数据，绑定 hg38 8192 bp ref/alt 窗口、因果标签与 match_group，保留匹配对照和全测试集评测协议。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/traitgym`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：ref_seq/var_seq 成对输入，附 chrom/pos/ref/alt、label 和 match_group；score 为来源 PIP 元数据而非待比较模型输出。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 按 matched_9 及 hg38 定义核对配对窗口，保留 match_group。
4. 固定 LL 差值和反向互补平均设置，防止把 PIP 或来源 class 当模型输入。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

两个配置均为 test 评测入口，smoke 是独立接口样例。保留 match_group；若另做拟合/校准，按组和位点隔离并另命名协议，不拆散一组的因果变异与匹配对照。

完整性检查须确认 ref/alt 与窗口中心、长度和参考一致。不要把 score/PIP 当作输入特征泄漏标签。跨染色体指标汇总与匹配分组均须遵循选定协议。

## next_phase_recommendation

选择 trait 配置 → 验证窗口与组 → 固定似然打分方向和正反链策略 → 按 match_group/染色体汇总；模型分数单独保存。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

窗口/坐标异常时列出具体变异并排除或修复为新版本；无完整匹配组时报告受限评测范围，不能补造对照。
