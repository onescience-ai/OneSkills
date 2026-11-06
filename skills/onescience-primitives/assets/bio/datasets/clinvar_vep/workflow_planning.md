## description

为ClinVar coding/non-coding 变异评测表选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

Carbon 本地 ClinVar VEP coding 与 non-coding 评测数据原语，区分坐标标签表、预计算模型分数和非编码质控注释，说明缺少直接 ref/alt 序列窗口及参考版本核对要求。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/clinvar-vep`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：现有分数复核消费 variant key + label + 指定 score；新模型消费显式生成的 ref/alt 序列，不能从不存在的窗口列直接加载。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 区分 coding 的历史分数表与 non_coding 的 QC 注释表，冻结位点清单。
4. 重跑序列模型前核实 genome assembly 与坐标，再生成并校验窗口。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

本地 README 将两个配置均注册为 test。不是现成的训练/验证划分。比较历史模型分数或重新打分时使用同一位点清单和缺失值政策，smoke 不替代全量测试。

不能把含模型分数的表当成原始序列训练集。重建窗口前必须确认参考基因组版本、pos 的坐标约定及 ref 一致性，不能仅因旁边有 hg38 文件就默认所有位点兼容。clinical 标签不等同于实验功能强度。

## next_phase_recommendation

位点/label 表 → 参考版本核查与 ref 校验 → 生成成对序列 → 新模型 VEP；历史 score 列独立保留用于比较。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

缺参考版本或序列窗口时仅交付位点/分数表解析，不生成猜测序列；位点不兼容时输出差异和过滤后分母。
