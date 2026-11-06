## description

为Boltz 多工具结构预测评测对与结果选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

Boltz 本地 CASP15/test 结构评测包，登记参考 CIF、Boltz/AF3/Chai 输入与预测、聚合指标和物理检查表，保留 target、模型编号、排名及 oracle/top1 的区别。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/Boltz_dataset/boltz_results_final`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：tool、target、reference_path、prediction_path、model_idx/rank，及独立标记的已有/新算指标；参考与预测角色必须显式。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 按 casp15/test 与工具建立配对表，检查缺失候选和排名。
4. 固定结构映射与物理检查协议，分别汇报 top1、average、oracle 与失败目标。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

保留 casp15/test 分支作为既有评测分组；本包不提供已核实的训练划分。比较工具必须对齐 target 交集、候选数和排名规则，并报告缺失预测。

不能将 outputs 或来源结果 CSV 当真值用于训练。gzip、链名、assembly、残基映射和缺失原子处理须一致；历史结果与本地重算结果分开标记。

## next_phase_recommendation

target 清单 → 工具预测/参考配对 → chain/assembly 映射 → 匹配评测工具 → oracle/average/top1 与物理质量分别汇总。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

没有可配对参考或工具格式不支持时记录 target 和原因，不用另一个工具预测补充真值；旧 CSV 只能标为来源结果。
