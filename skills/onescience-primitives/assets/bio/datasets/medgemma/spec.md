
## content_principle
MedGemma 医学多模态数据集合 面向 biology 任务中的数据接入、检索、预处理和模型消费，核心目标是把 `/public/share/sugonhpcapp01/onestore/onedatasets/medgemma` 中的真实目录组织成可复用的原语知识。

## data_schema
不同子目录对应图像、EHR、文本问答或多模态对照样本，字段由具体任务定义。

## directory_layout
```text
/medgemma
├── Chest_Xray/
├── camelyonpatch/
├── ehr/
├── medqa/
├── nct/
├── CTLM/
├── LLM-Research/
├── navigator/
├── test_images/
└── test_compare/
```

## storage_format
这是医学多任务数据集合，混合图像、病理、EHR、医学问答和测试对照素材；每个子任务的格式和标签需要分开解析。

## scale_spec
规模特征以具体数据源为准：结构库通常按样本 ID 或链 ID 组织；蛋白-配体数据通常按复合物目录或 LMDB 组织；基因组数据通常按染色体、物种或 benchmark split 组织。

## coverage_spec
适用于医学问答、图像分类、病理识别、EHR 结构化分析和多模态对齐。

## label_spec
若为训练集，标签可能是序列、坐标、亲和力、分类标签、问答对或结构目标；若为数据库集合，则通常不提供显式监督标签。

## split_strategy
应先按子任务选择目录，不要把所有目录混成一个统一数据集。

## constraints
先确认任务类型是图像、文本还是 EHR，再构建对应 split 和标签协议。
