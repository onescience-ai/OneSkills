## description

为Random Promoter DREAM 2022 合成启动子回归数据选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

Carbon 本地 Random Promoter DREAM 2022 酵母合成启动子数据，区分带活性的 supervised、无标签 challenge 序列和子集/leaderboard ID 元数据，保留原始划分与样本标识。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/finetune/random-promoter-dream-2022`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：监督任务消费 sequence+activity+来源键；challenge 消费无标签 sequence；ID 配置只供样本分组或提交索引。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 明确 config 的训练/预测/ID 元数据角色，禁止根据文件名 train 直接确定用途。
4. 验证跨配置标识连接及标签可用性，固定原始划分与评测子集。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

supervised 保留 train/validation/test。challenge 是提交式预测输入；test_subset_membership/public_leaderboard_ids 描述评测子集，不是新的训练样本。

多个 config 的行号命名空间不同。不得用 labeled test 调参或把 challenge 的存储 train 文件混入 supervised train。README 声明 CC BY 4.0，引用源挑战数据。

## next_phase_recommendation

选择 config → 验证 schema 和标识 → 回归或无标签预测 adapter → 按已验证 ID 规则分组评测。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

ID 对齐未确认时先输出整体验证结果和未匹配清单，不按位置猜测子集成员；无标签序列只走预测。
