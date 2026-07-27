
## content_principle
Protenix 结构与索引集合 面向 biology 任务中的数据接入、检索、预处理和模型消费，核心目标是把 `/public/share/sugonhpcapp01/onestore/onedatasets/protenix` 中的真实目录组织成可复用的原语知识。

## data_schema
seq_to_pdb_index.json 提供序列到结构检索索引；mmcif/mmcif_msa/mmcif_bioassembly 目录保存结构与比对文件；indices 目录保存采样或过滤后的列表。

## directory_layout
```text
/protenix
├── mmcif/
├── mmcif_msa/
├── mmcif_bioassembly/
├── posebusters_bioassembly/
├── posebusters_mmcif/
├── recentPDB_bioassembly/
├── indices/
├── seq_to_pdb_index.json
├── components.v20240608.cif
└── components.v20240608.cif.rdkit_mol.pkl
```

## storage_format
主结构文件为 mmCIF；MSA、bioassembly 和 recentPDB/posebusters 分支按结构 ID 或任务索引组织；索引为 JSON、CSV、TXT 和 CSV.GZ；化学组件字典为 CIF 与 RDKit pickle。

## scale_spec
规模特征以具体数据源为准：结构库通常按样本 ID 或链 ID 组织；蛋白-配体数据通常按复合物目录或 LMDB 组织；基因组数据通常按染色体、物种或 benchmark split 组织。

## coverage_spec
适用于蛋白结构预测、复合物建模、结构检索、MSA 组织和 Protenix 风格推理输入准备。

## label_spec
若为训练集，标签可能是序列、坐标、亲和力、分类标签、问答对或结构目标；若为数据库集合，则通常不提供显式监督标签。

## split_strategy
优先先读索引再定位结构文件，再按链级或复合物级组织样本；若下游需要单链/多链输入，应从 bioassembly 和 mmCIF 路径中区分。

## constraints
先确认序列映射、样本命名规则和 bioassembly 版本；若使用 MSA 或模板，需检查每个样本是否同时有 mmcif 与对应比对文件。
