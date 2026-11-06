## description

为Carbon 多来源基因组预训练语料选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

Carbon 本地 DNA/转录本预训练集合，覆盖 GENERator 真核语料及 10B 子集、Evo2 mRNA/splice/原核语料和 smoke 数据，区分 sequence 与 text schema、元数据标签和特殊分隔符。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/pretrain`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：统一适配后的文本或 token 流，附来源、record_id/id、物种/基因元数据及划分；语言建模标签由 collator 构造，不能从目录补造分类 label。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 分别核对真核 sequence 与 Evo2 text 两种入口，确认元数据包装、@ 和 tokenizer。
4. 固定来源混合、记录级 holdout 和 packing；smoke/cache 不参与基准规模统计。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

本地顶层语料目录和 shard 号不代表官方 train/validation/test。按记录、contig 或物种固定 holdout 与随机种子，避免同一来源片段跨 split；10B_subset 是原真核语料的子集，不能与完整真核语料当独立评测集。

不同来源使用不同列与文本包装；保留 `@`、物种/基因标签的语义并核对 tokenizer。来源 README 的混合比例和 6-mer 预算是训练配方，不应当成每个本地 shard 的统计。不同上游许可证分别继承。

## next_phase_recommendation

来源选择 → sequence/text 解析 → 元数据包装与特殊字符协议 → 流式 tokenization/packing；预处理输出与模型 tokenizer 版本一起登记。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

特殊字符或 tokenizer 不兼容时保留原始记录并列出适配差异；可用 JSONL 做 smoke 检查，不用随机 DNA 填补缺失数据。
