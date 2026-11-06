## description

为Carbon hg38 参考序列与预计算 VEP 结果包选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

Carbon/GENERator 本地 variant-effect-prediction 资源原语，分别登记 hg38 参考序列与 ClinVar 预计算模型结果，说明与 coding 子集、ref/alt 序列重建和新模型评测的关系。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/variant-effect-prediction`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：参考消费接口为 ID→Sequence/窗口查询；结果消费接口为 variant key、label 与指定模型 score，不提供已生成 ref/alt 序列。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 先确认消费的是参考序列还是历史结果，分别核对 schema 和样本单位。
4. 跨表/跨版本连接按坐标与参考一致性检查，不按行号或同名 label 推断等价。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

README 将 hg38 与 ClinVar_VEP_results 均列为 test 存储配置，但参考表的 test 标记不是监督测试样本划分。结果表用于历史结果复核；新划分或校准必须另定并防止位点泄漏。

Sequence 为可能很长的字符串，流式/选择性读取，不一次复制整个参考到内存。基因组 ID、pos 坐标、assembly、ref 匹配未确认前不能据此为任意 ClinVar 表生成窗口。

## next_phase_recommendation

参考 ID/版本核查 → 位点坐标/ref 校验 → 独立窗口生成 adapter；预计算模型结果保持只读并单独比较。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

参考过大时先只读 footer/ID，交给分块窗口步骤；没有可靠坐标映射时只交付已确认的结果表，不生成猜测窗口。
