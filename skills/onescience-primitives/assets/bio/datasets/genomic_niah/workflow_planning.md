## description

为Genomic-NIAH 长上下文 DNA 检索基准选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

Carbon 本地 Genomic-NIAH 长序列检索基准，覆盖 plain/near-duplicate 四类任务与 4k–128k 上下文，保留 key/value、生成 prompt、深度和正负续写，区分生成准确率与似然偏好。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/genomic-niah`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：生成消费 prompt 并回查 value；似然评测消费 positive_sequence/negative_sequence，保留 uid、config、source、depth 和长度。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 明确选择生成 exact match 还是似然判别，分开保留两套结果。
4. 确保完整 prompt 适配所选模型上下文，按长度/难度/深度保留分组。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

各配置均为 test；不同上下文/干扰难度分别评测。聚合时保留 source、depth 与 config，不把配置间可能共享来源当独立训练/测试划分。

截断 prompt 会改变检索任务及 needle 位置，不能静默裁剪后继续沿用同一上下文结果。DNA 生成 exact match 与 ll_correct 是不同指标，不能互相代替。

## next_phase_recommendation

选择配置 → tokenizer 实际长度检查 → 完整 prompt 生成或正负续写打分 → 按配置/深度聚合。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

模型上下文不足时明确报告该配置不支持，或选择更短的已有配置；不通过任意截断或随机补齐伪造长上下文评测。
