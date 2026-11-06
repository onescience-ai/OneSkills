## description

为Geneformer Genecorpus rank-token 单细胞语料选择数据入口、字段映射和下游接入路线，固化来源、样本单位与划分约束。

## when_to_use

Genecorpus-30M/104M 人类单细胞转录组 rank-value 编码语料，绑定 Geneformer 本地 Arrow 数据及下游示例，区分 2048/4096 版本、词表和特殊 token，用于自监督预训练与模型适配。 当需要使用上述本地数据及其具体 schema 时召回本卡。

## inputs

数据根目录 `/public/share/sugonhpcapp01/onestore/onedatasets/Geneformer`，所选子集、消费目标和输出目录；同时指定模型/解析器版本、标签或目标字段、划分协议。

## outputs

交付可追溯的数据接入信息：所选文件、样本单位、字段映射、标签/目标定义、划分和检查结果；保留未验证事项。

消费边界：主输入为 `input_ids`，30M 可提供 `length`，104M 可派生长度；任务 collator 负责 mask 与训练目标。示例 gene/cell 标签不属于所有主语料样本。

## procedure

1. 解析数据根目录和子集，确认文件可读、非空，记录实际选择与版本线索。
2. 检查实际 schema 和样本单位，保留原始标识与来源；配套资源必须与数据版本匹配。
3. 先选择 30M 或 104M，核对对应词表和特殊 token，不跨版本混用。
4. 读取 state 与 Arrow schema，抽查 token 与长度，按任务另行建立划分和标签映射。
5. 记录字段映射、划分、依赖和验证结果，交接至对应的数据 adapter 或只读索引步骤。

## constraints

两个版本的 README 均说明没有预定义 train/validation/test。预训练划分须另行固定并记录；下游任务使用独立标签与分组协议，不能把语料版本或 Arrow 分片号当 split。

30M 与 104M 的词表、特殊 token 和模型长度预算不同，不能拼接后直接共用 ID。30M README 描述 pad/mask，104M 描述 cls/eos/pad/mask；104M 所需 token_dictionary_104M.pkl 未在该本地根目录确认，接入前从匹配版本补齐。不要反向恢复或宣称提供原始表达计数。

## next_phase_recommendation

版本选择 → 词表与模型配置对齐 → Arrow 数据读取 → 任务所需的 mask/padding/collator；基因 ID 应按相应词表的 Ensembl 映射解释。

先完成当前消费接口的样本级验证，再根据用户目标进入数据准备、推理、训练或评测；本卡自身不执行这些工作。

## fallback

词表缺失时可先做 Arrow schema 和长度检查，补齐匹配版本后再解码基因或输入模型。分片缺失时列出具体文件，不用另一版本代替。
