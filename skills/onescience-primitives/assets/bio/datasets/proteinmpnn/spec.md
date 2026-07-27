
## content_principle
ProteinMPNN 结构训练样本集 面向 biology 任务中的数据接入、检索、预处理和模型消费，核心目标是把 `/public/share/sugonhpcapp01/onestore/onedatasets/proteinmpnn/pdb_2021aug02_sample` 中的真实目录组织成可复用的原语知识。

## data_schema
PDBID_CHAINID.pt 包含 seq、xyz、mask、bfac、occ；PDBID.pt 包含 method、date、resolution、chains、tm、asmb_ids、asmb_details、asmb_method 和 assembly 变换。

## directory_layout
```text
/pdb_2021aug02_sample
├── README
├── list.csv
├── valid_clusters.txt
├── test_clusters.txt
├── pdb/
└── l3/
```

## storage_format
核心样本为 PyTorch `.pt` 文件；list.csv 保存链级索引、序列和 cluster；valid/test cluster 文件用于防止序列同源泄漏。

## scale_spec
规模特征以具体数据源为准：结构库通常按样本 ID 或链 ID 组织；蛋白-配体数据通常按复合物目录或 LMDB 组织；基因组数据通常按染色体、物种或 benchmark split 组织。

## coverage_spec
适用于 ProteinMPNN 序列设计、链级条件生成、结构约束采样和 cluster split 训练/验证。

## label_spec
若为训练集，标签可能是序列、坐标、亲和力、分类标签、问答对或结构目标；若为数据库集合，则通常不提供显式监督标签。

## split_strategy
先按 list.csv 或 cluster 文件定位链，再按 PDBID 读取单链或 assembly 元信息；训练时应保持 cluster 分割，不要跨 cluster 随机切分。

## constraints
先检查链级 pt 是否齐全，再确认验证/测试 cluster 与训练 cluster 不重叠。
