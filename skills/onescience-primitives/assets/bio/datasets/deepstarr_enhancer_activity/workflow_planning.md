## description

为DeepSTARR 增强子活性回归数据选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

Carbon 本地 DeepSTARR 增强子双目标活性回归数据原语，绑定 train/valid/test Parquet，区分原始、scaled、quantile-normalized 活性及 label 向量。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/finetune/DeepSTARR-enhancer-activity`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：sequence、两个指定顺序的连续 targets、id、split；需要反变换时同时交付匹配的目标变换参数。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 显式选择 raw/scaled/quantile-normalized 目标空间，验证 label 位置。
4. 保留现有划分，固定 tokenizer/增强策略并验证回归头输出维度。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

保留 train/valid/test 文件角色，内部可将 valid 显式别名为 validation，但不得与 test 互换。重新拟合目标变换仅使用 train。

不要将 label 列转为类别 ID，也不要只凭向量长度猜测两个目标顺序。预处理、截断和 reverse complement augmentation 应记录，不能跨 split 重采样。

## next_phase_recommendation

固定目标列/label 顺序 → tokenizer 与长度检查 → 双目标回归 adapter；输出保留 id 和 split。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

label 向量顺序或变换来源不明时优先选择具有明确定义的具名目标列，并报告该协议与来源配方的差异。
