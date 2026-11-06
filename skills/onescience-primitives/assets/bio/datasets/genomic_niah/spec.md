## content_principle

Genomic-NIAH 长上下文 DNA 检索基准。Carbon 本地 Genomic-NIAH 长序列检索基准，覆盖 plain/near-duplicate 四类任务与 4k–128k 上下文，保留 key/value、生成 prompt、深度和正负续写，区分生成准确率与似然偏好。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/eval/genomic-niah`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取 README 任务/字段/指标说明和全部 24 个 Parquet footer，核实两类 schema。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

共有 `uid,haystack_mode,source,context_length_tokens,context_length_bp,depth,condition,num_distractors,key_len_bp,value_len_bp,key,value,negative_value,prompt,positive_sequence,negative_sequence`。plain 另有 `target_insert_start_bp,target_insert_end_bp`；near-duplicate 另有 `task,mutation_distance,distractor_keys,distractor_values`，没有 plain 的两个插入位置列。样本单位是一项检索问题，而非带类别标签的基因。

## directory_layout

```text
genomic-niah/
├── README.md
├── assets/
└── data/
    ├── niah_<4k|8k|16k|32k|64k|128k>/test-00000-of-00001.parquet
    └── niah_neardup_d<1|2|4>_<4k|8k|16k|32k|64k|128k>/test-00000-of-00001.parquet
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

Parquet，DNA prompt/续写与检索条件元数据。context_length_tokens 的来源约定是 6-mer token 数，不能直接等同于任意模型 tokenizer 的长度。

## scale_spec

核实 24 个配置文件 footer，每个 500 行，共 12,000 个检索样本。来源 README 说明 5 个插入深度（10/25/50/75/90%）及四个真核 kingdom 分层；不是 12,000 个独立生物样本的物种分类集。

## coverage_spec

任务前缀 niah、niah_neardup_d4、d2、d1，与六档上下文构成 4×6 网格。README 描述 haystack_mode=real 或 real_stitched；后者拼接同一 record 的 ACGT runs，不应当成完整连续染色体。

## label_spec

生成目标为 value（README 定义 24 bp），模型输入为 prompt。positive_sequence=prompt+value、negative_sequence=prompt+negative_value 供似然比较；生成时不得把 positive_sequence 当输入泄漏答案。

## split_strategy

各配置均为 test；不同上下文/干扰难度分别评测。聚合时保留 source、depth 与 config，不把配置间可能共享来源当独立训练/测试划分。

## constraints

截断 prompt 会改变检索任务及 needle 位置，不能静默裁剪后继续沿用同一上下文结果。DNA 生成 exact match 与 ll_correct 是不同指标，不能互相代替。
