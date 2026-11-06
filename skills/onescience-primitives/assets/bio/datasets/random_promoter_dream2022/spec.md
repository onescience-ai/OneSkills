## content_principle

Random Promoter DREAM 2022 合成启动子回归数据。Carbon 本地 Random Promoter DREAM 2022 酵母合成启动子数据，区分带活性的 supervised、无标签 challenge 序列和子集/leaderboard ID 元数据，保留原始划分与样本标识。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/finetune/random-promoter-dream-2022`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取 README 与全部七个 Parquet footer，核实四种 config 的字段、行数及标签差异。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

supervised：`sequence:string,activity:float,sequence_length:int32,source_file:string,row_id:int64`。challenge_test_sequences 相同但没有 activity。两个 ID 配置为 `subset,item_id,row_id,source_member,line_number,raw_line`，不是序列样本；item_id 非数字时 row_id 可为 -1，不能当作有效连接键。

## directory_layout

```text
random-promoter-dream-2022/
├── README.md
├── supervised/{train-<shard>-of-00002,validation-00000-of-00001,test-00000-of-00001}.parquet
├── challenge_test_sequences/train-00000-of-00001.parquet
├── test_subset_membership/train-00000-of-00001.parquet
└── public_leaderboard_ids/train-00000-of-00001.parquet
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

Parquet 的四个独立 config。challenge/ID 目录中的 train 文件名只是其存储 split，不表示可用于监督训练。

## scale_spec

footer 核实 supervised train 6,065,325 行、validation 673,925 行、test 71,103 行；challenge 序列 71,103 行；subset membership 63,683 行；public leaderboard ID 10 行。ID 行数不等于独立序列总数。

## coverage_spec

来源 README 说明为 Zenodo 10633252（DOI 10.5281/zenodo.10633252）加工版本，任务为合成酵母启动子序列到测量表达活性的回归。

## label_spec

activity 是连续表达活性。challenge 序列无标签，不应填零补成训练数据。ID 表必须按照原始 source_file/source_member、item_id 和行号约定连接，不能跨 config 直接按行数或 row_id 拼接。

## split_strategy

supervised 保留 train/validation/test。challenge 是提交式预测输入；test_subset_membership/public_leaderboard_ids 描述评测子集，不是新的训练样本。

## constraints

多个 config 的行号命名空间不同。不得用 labeled test 调参或把 challenge 的存储 train 文件混入 supervised train。README 声明 CC BY 4.0，引用源挑战数据。
