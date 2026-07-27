
## content_principle
DiffDock 对接数据与模型集合 面向 biology 任务中的数据接入、检索、预处理和模型消费，核心目标是把 `/public/share/sugonhpcapp01/onestore/onedatasets/diffdock/datasets` 中的真实目录组织成可复用的原语知识。

## data_schema
训练侧通常是处理好的复合物图、对接姿态与 split；推理侧是输入蛋白和配体描述、缓存图和模型参数。

## directory_layout
```text
/diffdock
├── datasets/
│   ├── PDBBind_processed/
│   ├── BindingMOAD_2020_processed/
│   ├── P-L/
│   ├── inferdata/
│   ├── splits/
│   ├── esm_pdbbind/
│   └── esm_pdbbind_full/
├── score_model/
├── confidence_model/
├── cache/
└── cache_torsion/
```

## storage_format
处理后数据以复合物目录、缓存图、split 文件、ESM embedding 和模型 YAML/PT 权重共同组成；训练前应区分 raw archive、processed 数据和运行缓存。

## scale_spec
规模特征以具体数据源为准：结构库通常按样本 ID 或链 ID 组织；蛋白-配体数据通常按复合物目录或 LMDB 组织；基因组数据通常按染色体、物种或 benchmark split 组织。

## coverage_spec
适用于蛋白-配体对接、结合姿态评分、虚筛和推理构图。

## label_spec
若为训练集，标签可能是序列、坐标、亲和力、分类标签、问答对或结构目标；若为数据库集合，则通常不提供显式监督标签。

## split_strategy
优先按 split 文件和 processed 数据集构建训练集，再用 inferdata 处理在线输入；若使用 ESM 嵌入，应同步检查嵌入字典与样本 ID。

## constraints
先确认 PDBBind 与 MOAD 的 split 一致性，再核对缓存目录和 torsion/noise 参数。
