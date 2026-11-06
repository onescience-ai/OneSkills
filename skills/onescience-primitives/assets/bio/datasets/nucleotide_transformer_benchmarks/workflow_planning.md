## description

为Nucleotide Transformer 下游序列分类任务集选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

Carbon 本地 Nucleotide Transformer 下游 18 项 DNA 分类数据原语，登记 Parquet/FNA 双格式、sequence/name/label/task 与 train/test 划分，明确与 HyenaDNA 同类分支需核验后复用。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/finetune/nucleotide_transformer_downstream_tasks`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：sequence、任务内 label、name、task 与原始 split；所有批次必须明确当前 task 的类别映射。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 固定一个任务和其类目映射，保留 train/test，不混同 GUE。
4. 如需复用 HyenaDNA 资源，先核对命名、ID、序列与划分再确认等价。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

保留每任务 train/test，没有本地统一 validation 文件。需要验证集时仅从 train 按来源/序列组划分，报告派生协议；不得从 test 调参。

该集合不能因为包含 promoter/组蛋白任务就冒称 GUE 或 BEND。HyenaDNA 中存在 enhancer 等目录命名差异，未经内容比对不能自动认定为同一快照或互换 split。

## next_phase_recommendation

任务选择 → Parquet 标签/ID 解析 → tokenizer 与分类头 → 保留 train/test 的任务级评测；跨资源复用先比对样本身份。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

任务标签说明缺失时可做 schema/序列检查，保留原始 ID；FNA 标签不明时改用已标注 Parquet，不猜测 header 编码。
