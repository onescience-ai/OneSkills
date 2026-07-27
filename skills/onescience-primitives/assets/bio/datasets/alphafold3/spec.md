
## content_principle
AlphaFold 3 参考库集合 面向 biology 任务中的数据接入、检索、预处理和模型消费，核心目标是把 `/public/share/sugonhpcapp01/onestore/onedatasets/alphafold3` 中的真实目录组织成可复用的原语知识。

## data_schema
典型输入是多链蛋白、核酸或配体相关序列，输出依赖数据库检索和对齐输入。

## directory_layout
```text
/alphafold3
├── public_databases/
├── alignDB/
├── infer_input_data/
├── jackhmmer_split/
├── mmseqsDB/
└── jackhmmer_split.tar.gz
```

## storage_format
这是 AF3 推理和检索数据库集合；public_databases/mmseqsDB/alignDB 属于数据库，infer_input_data 属于输入样例或推理素材。

## scale_spec
规模特征以具体数据源为准：结构库通常按样本 ID 或链 ID 组织；蛋白-配体数据通常按复合物目录或 LMDB 组织；基因组数据通常按染色体、物种或 benchmark split 组织。

## coverage_spec
适用于 AlphaFold 3 推理、数据库挂载和检索前处理。

## label_spec
若为训练集，标签可能是序列、坐标、亲和力、分类标签、问答对或结构目标；若为数据库集合，则通常不提供显式监督标签。

## split_strategy
先确认是搜索库还是输入样本，再按 alphaFold3 的工作流分开处理。

## constraints
先检查数据库目录和输入目录是否分离，再核对 split 和索引是否完整。
