
## content_principle
AlphaFold 2.3.0 参考数据库集合 面向 biology 任务中的数据接入、检索、预处理和模型消费，核心目标是把 `/public/share/sugonhpcapp01/onestore/onedatasets/alphafold2.3.0` 中的真实目录组织成可复用的原语知识。

## data_schema
输入通常是蛋白序列，输出依赖参数文件、序列数据库和模板数据库。

## directory_layout
```text
/alphafold2.3.0
├── params/
│   ├── params_model_1.npz
│   ├── ...
│   └── params_model_5_multimer_v3.npz
├── bfd/
├── mgnify/
├── pdb70/
├── pdb_mmcif/
├── pdb_seqres/
├── small_bfd/
├── uniprot/
├── uniref30/
└── uniref90/
```

## storage_format
这是 AlphaFold 2 参数和公共数据库包；params 为模型权重，其他目录为序列、模板或 MSA 搜索数据库。

## scale_spec
规模特征以具体数据源为准：结构库通常按样本 ID 或链 ID 组织；蛋白-配体数据通常按复合物目录或 LMDB 组织；基因组数据通常按染色体、物种或 benchmark split 组织。

## coverage_spec
适用于 AlphaFold 2 推理、数据库复现和同源搜索准备。

## label_spec
若为训练集，标签可能是序列、坐标、亲和力、分类标签、问答对或结构目标；若为数据库集合，则通常不提供显式监督标签。

## split_strategy
优先作为数据库和参数目录挂载，训练或推理脚本应通过外部配置指定具体数据库路径。

## constraints
先确认 params 与公共数据库版本是否配套，再检查索引和压缩包是否完整。
