## content_principle

Geneformer Genecorpus rank-token 单细胞语料。Genecorpus-30M/104M 人类单细胞转录组 rank-value 编码语料，绑定 Geneformer 本地 Arrow 数据及下游示例，区分 2048/4096 版本、词表和特殊 token，用于自监督预训练与模型适配。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Geneformer`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取两版 README、dataset_info/state、首个 Arrow schema 与 batch，并检查全部声明分片是否存在；未全量扫描所有细胞。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

| 版本 | 已核实 Arrow 字段 | 语义 |
| --- | --- | --- |
| 30M / 2048 | `input_ids: list<int64>`、`length: int64` | 每个细胞的基因排序 token 与长度 |
| 104M / 4096 | `input_ids: list<int32>` | 每个细胞的排序 token；本地没有独立 `length` 字段 |

不是表达计数矩阵，也不是 DNA 碱基 token。30M README 的 `lengths` 与本地实际字段 `length` 不同，读取以 Arrow/schema 为准。104M 长度可从列表计算，不应假定每条恰好 4096。

## directory_layout

```text
Geneformer/
├── Genecorpus-30M/
│   ├── README.md
│   ├── genecorpus_30M_2048.dataset/{dataset_info.json,state.json,dataset.arrow}
│   ├── token_dictionary.pkl
│   ├── genecorpus_30M_2048{,_sorted}_lengths.pkl
│   └── example_input_files/{cell_classification,gene_classification,tf_targets}/
└── Genecorpus-104M/
    ├── README.md
    └── genecorpus_104M_4096.dataset/{dataset_info.json,state.json,data-<shard>-of-01202.arrow}
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

Hugging Face Datasets 的磁盘目录与 Arrow IPC stream；通过兼容版本的 `datasets.load_from_disk` 读取，或用 Arrow IPC 流接口检查。长度、词表和示例标签另有 pickle/CSV，不与 Arrow 主样本自动合并。

## scale_spec

30M 的 state 声明 1 个 Arrow 文件，104M 声明 1202 个分片，本次逐一检查这些声明路径均存在。30M README 记载质控后 27,406,217 个细胞；104M README 记载 103,877,737 个细胞，均为来源文档规模，不是本轮全量重计。首个 batch 抽查：30M 第一条 length=2048；104M 第一条 token 列表长度 286。

## coverage_spec

人类单细胞转录组自监督表示学习。配套示例覆盖细胞类型/疾病分类、bivalent promoters、剂量敏感 TF、NOTCH1 网络和 TF 调控范围；示例标签须按各任务单独解析。

## label_spec

主语料 README 明确不含细胞注释，无统一监督 `label`。排序来自细胞内表达经语料基因非零中位数归一化后的基因次序。30M README 描述 25,424 个编码/miRNA 基因，104M 描述 20,271 个蛋白编码基因；这些不是可直接作为分类头维度的细胞类别数。

## split_strategy

两个版本的 README 均说明没有预定义 train/validation/test。预训练划分须另行固定并记录；下游任务使用独立标签与分组协议，不能把语料版本或 Arrow 分片号当 split。

## constraints

30M 与 104M 的词表、特殊 token 和模型长度预算不同，不能拼接后直接共用 ID。30M README 描述 pad/mask，104M 描述 cls/eos/pad/mask；104M 所需 token_dictionary_104M.pkl 未在该本地根目录确认，接入前从匹配版本补齐。不要反向恢复或宣称提供原始表达计数。
