
## content_principle
GenScore 打分与虚筛数据集合 面向 biology 任务中的数据接入、检索、预处理和模型消费，核心目标是把 `/public/share/sugonhpcapp01/onestore/onedatasets/GenScore/genscore_data` 中的真实目录组织成可复用的原语知识。

## data_schema
训练侧样本通常是 protein_graph、ligand_graph、label；推理侧会从 pocket 和 ligand 文件实时构图。

## directory_layout
```text
/GenScore
├── genscore_data/
│   ├── CASF-2016/
│   ├── PDBbind_flat/
│   ├── PDBbind_v2020/
│   ├── inferdata/
│   └── rtmscore_s/
├── test_data/
└── trained_models/
```

## storage_format
数据包括 PDBBind/CASF 结构、图缓存或在线构图输入；权重和 smoke test 文件与训练数据分开保存。

## scale_spec
规模特征以具体数据源为准：结构库通常按样本 ID 或链 ID 组织；蛋白-配体数据通常按复合物目录或 LMDB 组织；基因组数据通常按染色体、物种或 benchmark split 组织。

## coverage_spec
适用于结合亲和力预测、虚筛排序和口袋-配体图打分。

## label_spec
若为训练集，标签可能是序列、坐标、亲和力、分类标签、问答对或结构目标；若为数据库集合，则通常不提供显式监督标签。

## split_strategy
训练时先区分 PDBbind 与 CASF 评测集，再按需要加载图缓存或在线构图；推理时应优先使用 pocket 生成路径。

## constraints
先确认图缓存版本和标签来源，再核对测试集是否与训练集分离。
