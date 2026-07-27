
## content_principle
La-Proteina 数据与权重集合 面向 biology 任务中的数据接入、检索、预处理和模型消费，核心目标是把 `/public/share/sugonhpcapp01/onestore/onedatasets/la-proteina/dataset` 中的真实目录组织成可复用的原语知识。

## data_schema
样本通常由蛋白序列、结构、训练划分和模型权重路径组成。

## directory_layout
```text
/la-proteina
├── dataset/
│   ├── pdb/
│   └── pdb_train/
├── AFDB/
├── ca_model_weights/
├── vanilla_model_weights/
└── checkpoints_laproteina/
```

## storage_format
结构样本以 PDB 目录和训练 PDB 子集组织；AFDB 与权重目录是参考和模型依赖，不应混作监督标签。

## scale_spec
规模特征以具体数据源为准：结构库通常按样本 ID 或链 ID 组织；蛋白-配体数据通常按复合物目录或 LMDB 组织；基因组数据通常按染色体、物种或 benchmark split 组织。

## coverage_spec
适用于蛋白结构生成、设计模型预训练和结构验证。

## label_spec
若为训练集，标签可能是序列、坐标、亲和力、分类标签、问答对或结构目标；若为数据库集合，则通常不提供显式监督标签。

## split_strategy
先确认是训练集还是结构库，再将 PDB 或 AFDB 样本映射到模型输入。

## constraints
先检查 pdb_train 的训练划分和 AFDB 结构是否一致，再核对权重版本。
