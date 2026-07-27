
## content_principle
AlphaGenome 训练与参考集合 面向 biology 任务中的数据接入、检索、预处理和模型消费，核心目标是把 `/public/share/sugonhpcapp01/onestore/onedatasets/AlphaGenome` 中的真实目录组织成可复用的原语知识。

## data_schema
典型样本包括参考序列、fold 划分、训练片段和物种标签。

## directory_layout
```text
/AlphaGenome
├── reference/
│   ├── HOMO_SAPIENS/
│   └── MUS_MUSCULUS/
├── v1/
│   └── train/
└── fasttrans/
```

## storage_format
格式包括物种参考序列、版本化训练目录和 fasttrans 支撑包；具体样本字段应按 v1/train 内部 fold 或任务目录确认。

## scale_spec
规模特征以具体数据源为准：结构库通常按样本 ID 或链 ID 组织；蛋白-配体数据通常按复合物目录或 LMDB 组织；基因组数据通常按染色体、物种或 benchmark split 组织。

## coverage_spec
适用于基因组基础模型、跨物种建模、参考序列对齐和训练/验证切分。

## label_spec
若为训练集，标签可能是序列、坐标、亲和力、分类标签、问答对或结构目标；若为数据库集合，则通常不提供显式监督标签。

## split_strategy
先根据 v1 或 reference 目录确定任务版本，再按物种或 fold 划分数据。

## constraints
先检查 reference 物种是否满足任务要求，再核对 train 与 ALL_FOLDS 的版本对应关系。
