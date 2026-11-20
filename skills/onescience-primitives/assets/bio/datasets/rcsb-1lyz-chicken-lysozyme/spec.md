# RCSB 1LYZ 数据规格

## content_principle

RCSB PDB 1LYZ 鸡卵清溶菌酶既有实验结构及官方条目、实体元数据；结构模型 revision 1.4，修订日期 2024-10-16。数据包版本与知识原语版本分别维护。

- https://data.rcsb.org/rest/v1/core/entry/1LYZ
- https://data.rcsb.org/rest/v1/core/polymer_entity/1LYZ/1
- https://files.wwpdb.org/pub/pdb/README
- https://files.rcsb.org/download/1LYZ.pdb

## data_schema

1LYZ.pdb 为 PDB 文本结构记录，含模型、链、原子、残基编号、插入码、坐标（Å）、占据率、altloc 与 B-factor。entry.json、polymer_entity_1.json 为官方 JSON 对象，分别提供修订记录和物种、链、来源序列及 UniProt 对应信息。实体 1、作者链 A；来源 Gallus gallus（税号 9031），UniProt P00698，实体标称长度 129 残基。实际坐标覆盖须从结构读取，不由标称长度推定。

## directory_layout

资源根目录及逐文件哈希见 [usage/access](usage.md#access)。必要文件为：

```text
rcsb-1lyz-r1p4-chicken-lysozyme/
  1LYZ.pdb
  entry.json
  polymer_entity_1.json
```

三文件分别承担结构、条目/版本及实体/来源说明，不能只取结构文件替代整个包。

## storage_format

PDB 文本与 JSON；保留原始完整文件，不压缩、不截断。解析时保留原始记录，区分聚合物、水和其他异源记录；处理插入码、替代构象、缺失和解析异常。

## scale_spec

三个必要文件共 177396 字节：1LYZ.pdb 为 145962，entry.json 为 12212，polymer_entity_1.json 为 19222。规模不含解析对象、软件依赖或输出。

## coverage_spec

单个 PDB 条目的结构输入及来源元数据，分析选择实体 1、链 A。P00698 前体编号与成熟结构编号须显式映射；该包只覆盖结构身份与坐标质控用途。

## label_spec

无独立实验评价标签，不含表位或其他下游预测标签；晶体 B-factor 不解释为预测结构的 pLDDT。

## split_strategy

本包为单条结构输入，训练/验证/测试拆分不适用；若后续作为模型输入或评测材料，消费者需另行建立隔离与泄漏检查。

## constraints

该包不含 SASA、COREX、序列熵及完整对齐特征，也不含经条件核验的同源输入、离线 MHC 文件或独立实验标签。wwPDB README 支持公开获取；完整法律条款未核实，不推定任意用途或再分发授权。
