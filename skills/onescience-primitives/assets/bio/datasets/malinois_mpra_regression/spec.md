## content_principle

Malinois/Gosai 三细胞类型 MPRA 回归数据。Carbon 本地 Malinois/Gosai MPRA 三目标回归数据，绑定染色体划分、K562/HepG2/SKNSH 活性与标准误，保留 train z-score、反向互补输入和 SE 评测过滤。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/finetune/malinois-mpra-regression`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取本地详细 README 与全部四个 Parquet footer，记录完整列集合和 split 行数。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

标识与来源：`id,split,chromosome,data_project,oligo,variant_class`；序列：`sequence,sequence_length,reverse_complement,forward_rc_concat`；活性：`K562_log2FC,HepG2_log2FC,SKNSH_log2FC`；标准误：三个 `*_lfcSE`；训练标准化目标：三个 `*_log2FC_train_zscore`；筛选：`all_se_le_1,any_log2fc_gt_0_5`。目标为三维连续回归。

## directory_layout

```text
malinois-mpra-regression/
├── README.md
├── create_dataset.py                 # 来源构建脚本，不作为数据执行
└── data/
    ├── train-00000-of-00002.parquet
    ├── train-00001-of-00002.parquet
    ├── validation-00000-of-00001.parquet
    └── test-00000-of-00001.parquet
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

Parquet；一行对应来源 MPRA oligo/变异实例及三个细胞类型的活性。

## scale_spec

footer 核实 train 两片合计 668,946 行、validation 62,406 行、test 66,712 行。README 说明 all_se_le_1 过滤后的 validation/test 分别 58,811/62,582 行；本轮未重计该布尔筛选。

## coverage_spec

来源 README 指向 Gosai et al., Nature 2024，Machine-guided design of cell-type-targeting cis-regulatory elements 及补充 MPRA 表；适用于细胞类型特异调控活性预测。

## label_spec

输出顺序固定为 K562、HepG2、SKNSH；可选 raw log2FC 或 train_zscore，但需与模型头一致。all_se_le_1 表示三个标准误均 ≤1.0；高活性 any_log2fc_gt_0_5 是筛选/上采样辅助标记，不是回归标签。

## split_strategy

沿用染色体划分：validation 为 19/21/X，test 为 7/13，其余进入 train。两个 train shard 属于同一 split。保留 README 中的训练标准化统计，不用 validation/test 重新拟合。

## constraints

SE 过滤改变评测分母，必须显式报告。forward_rc_concat 已包含正反两段 <dna> 包装，不能再次无意追加反向互补。不要执行来源 create_dataset.py 中的上传操作。
