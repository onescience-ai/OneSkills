
## content_principle
TargetDiff 口袋-配体数据集合 面向 biology 任务中的数据接入、检索、预处理和模型消费，核心目标是把 `/public/share/sugonhpcapp01/onestore/onedatasets/targetdiff/data` 中的真实目录组织成可复用的原语知识。

## data_schema
PocketLigandPairDataset 以 pocket_fn 和 ligand_fn 为索引，输出 ProteinLigandData；PDBBind 路径会额外携带 y 和 kind。

## directory_layout
```text
/targetdiff
├── data/
│   └── <target_or_pocket_id>/
├── examples/
│   ├── *_pocket10.pdb
│   └── *_ligand.sdf
└── fpscores.pkl.gz
```

## storage_format
原始样本多为 pocket PDB、ligand SDF/MOL2 和 index.pkl；运行时通常生成 LMDB 缓存与 PyG 图对象。

## scale_spec
规模特征以具体数据源为准：结构库通常按样本 ID 或链 ID 组织；蛋白-配体数据通常按复合物目录或 LMDB 组织；基因组数据通常按染色体、物种或 benchmark split 组织。

## coverage_spec
适用于靶点条件分子生成、口袋对接、亲和力相关训练和样例验证。

## label_spec
若为训练集，标签可能是序列、坐标、亲和力、分类标签、问答对或结构目标；若为数据库集合，则通常不提供显式监督标签。

## split_strategy
优先确认 index.pkl、口袋 PDB 和配体文件是否同目录成套，再决定是否生成 LMDB 缓存。

## constraints
先检查靶点子目录是否同时有 protein 和 ligand，再验证缓存版本和 split 文件。
