## content_principle

DeepSTARR 增强子活性回归数据。Carbon 本地 DeepSTARR 增强子双目标活性回归数据原语，绑定 train/valid/test Parquet，区分原始、scaled、quantile-normalized 活性及 label 向量。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Carbon/finetune/DeepSTARR-enhancer-activity`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。读取 README、三个 Parquet footer，并对首条训练样本核对 label 与 scaled 目标对应。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

`id:string,sequence:string`；活性列 `Dev_log2_enrichment,Hk_log2_enrichment` 及对应 `_scaled`、`_quantile_normalized` 列（double）；`label:list<double>`。首条训练样本中 label 顺序与 `[Dev_log2_enrichment_scaled,Hk_log2_enrichment_scaled]` 一致，正式消费前还须核查整个目标映射。

## directory_layout

```text
DeepSTARR-enhancer-activity/
├── README.md
├── train.parquet
├── valid.parquet
└── test.parquet
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

Parquet，一条序列对应两个连续活性目标。id 是来源样本标识，不必解析成统一坐标格式后才能读取。

## scale_spec

footer 核实 train 402,296 行、valid 40,570 行、test 41,186 行。第一条训练序列为 249 bp，仅为样本观察，不据此断言全部等长。

## coverage_spec

本地 README 声明来源 DeepSTARR Zenodo 5502060，并作格式调整。用于增强子 developmental/housekeeping 活性回归，不是二分类标签集合。

## label_spec

Dev 与 Hk 为两个连续目标；原始、scaled、quantile-normalized 三种空间需显式选择，不能把输出空间或 label 向量顺序混用。变换参数及其拟合来源若不可追溯，应先补齐再声称严格复现实验。

## split_strategy

保留 train/valid/test 文件角色，内部可将 valid 显式别名为 validation，但不得与 test 互换。重新拟合目标变换仅使用 train。

## constraints

不要将 label 列转为类别 ID，也不要只凭向量长度猜测两个目标顺序。预处理、截断和 reverse complement augmentation 应记录，不能跨 split 重采样。
