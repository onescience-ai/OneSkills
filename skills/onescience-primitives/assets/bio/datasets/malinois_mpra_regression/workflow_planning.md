## description

为Malinois/Gosai 三细胞类型 MPRA 回归数据选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

Carbon 本地 Malinois/Gosai MPRA 三目标回归数据，绑定染色体划分、K562/HepG2/SKNSH 活性与标准误，保留 train z-score、反向互补输入和 SE 评测过滤。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/finetune/malinois-mpra-regression`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：指定序列输入、顺序固定的三维 targets、标准误/筛选标记、chromosome、id 和 split；模型训练不将目标相关筛选标记偷渡为输入特征。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 固定目标空间、三目标顺序与单链/双链包装。
4. 验证 chromosome split 与 SE 过滤分母，确认所有拟合仅来自 train。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

沿用染色体划分：validation 为 19/21/X，test 为 7/13，其余进入 train。两个 train shard 属于同一 split。保留 README 中的训练标准化统计，不用 validation/test 重新拟合。

SE 过滤改变评测分母，必须显式报告。forward_rc_concat 已包含正反两段 <dna> 包装，不能再次无意追加反向互补。不要执行来源 create_dataset.py 中的上传操作。

## next_phase_recommendation

保留 chromosome split → 选择 sequence 或 forward_rc_concat → 三目标回归 adapter；训练 z-score 与目标顺序随模型一起记录。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

预包装文本与 tokenizer 不兼容时改用原始 sequence 并显式定义包装；SE 或目标异常单独报告，不静默替换。
