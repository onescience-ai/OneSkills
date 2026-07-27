
## content_principle
ESMFold 运行数据集合 面向 biology 任务中的数据接入、检索、预处理和模型消费，核心目标是把 `/public/share/sugonhpcapp01/onestore/onedatasets/esmfold` 中的真实目录组织成可复用的原语知识。

## data_schema
通常输入是蛋白序列或 FASTA，输出是结构预测或中间特征。

## directory_layout
```text
/esmfold
├── data/
└── weight/
```

## storage_format
这是 ESMFold 推理/复现支撑目录，通常由序列输入配合 weight 目录消费；data 目录是否包含样本需在任务前抽查。

## scale_spec
规模特征以具体数据源为准：结构库通常按样本 ID 或链 ID 组织；蛋白-配体数据通常按复合物目录或 LMDB 组织；基因组数据通常按染色体、物种或 benchmark split 组织。

## coverage_spec
适用于 ESMFold 推理、结构预测和模型复现。

## label_spec
若为训练集，标签可能是序列、坐标、亲和力、分类标签、问答对或结构目标；若为数据库集合，则通常不提供显式监督标签。

## split_strategy
应按推理资源包处理，先确认权重版本，再决定是否需要额外序列数据。

## constraints
先检查 weight 是否完整，再确认 data 目录中是否包含所需的缓存或参考输入。
