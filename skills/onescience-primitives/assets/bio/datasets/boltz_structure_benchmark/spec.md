## content_principle

Boltz 多工具结构预测评测对与结果。Boltz 本地 CASP15/test 结构评测包，登记参考 CIF、Boltz/AF3/Chai 输入与预测、聚合指标和物理检查表，保留 target、模型编号、排名及 oracle/top1 的区别。

本地数据根目录：`/public/share/sugonhpcapp01/onestore/onedatasets/Boltz_dataset/boltz_results_final`。蒸馏依据为 2026-11-05 的本地文件、配套说明及有界元数据核查。核查目录角色、7fct 参考/预测入口及两类 CSV schema；未运行结构评测。卡片版本描述原语修订，不代表上游数据发布版本。

## data_schema

评测单位为 tool × target × model/排名，参考结构与预测分开。results CSV 表头为 `tool,target,metric,oracle,average,top1`；physical_checks 包括 `tool,pdb_id,model_idx`、ligand/bond/angle/clash/chirality 等计数和 `clash_free,valid_ligand,valid`。targets/test 多为 `.cif.gz`，CASP15 为 `.cif`；工具预测目录格式须各自解析。

## directory_layout

```text
boltz_results_final/
├── targets/{casp15,test}/
├── inputs/{casp15,test}/{boltz,af3,chai,msa}/
├── outputs/{casp15,test}/{boltz,af3,chai}/
├── results_{casp,test}.csv
├── physical_checks_test.csv
├── evals/
├── evals_local/
└── aggregate_local/
```

`<...>` 和花括号表示路径模式；实际可用文件以接入时检查为准。

## storage_format

CIF/gzip CIF、工具专属输入/预测和 CSV 结果。aggregate_local/evals_local 属于派生评测产物，不是新的独立参考集。

## scale_spec

本轮确认 CASP15/test 与三工具目录，读取 results_test 和 physical_checks 表头及首行，并确认 test/7fct 参考与预测入口；未全量统计所有 target、模型数或重算指标。

## coverage_spec

多工具结构精度和物理合理性复核。CASP15 与 test 的 target 命名和参考来源分别保留，不能假定都是同一 PDB 发布时间切分。

## label_spec

参考 CIF 是结构真值入口，预测 CIF 是模型输出。oracle 是事后最佳候选统计，top1 是选定第一候选，average 为集合统计，不能将 oracle 当成模型实际排序性能。物理 valid 标记不等同于结构精度。

## split_strategy

保留 casp15/test 分支作为既有评测分组；本包不提供已核实的训练划分。比较工具必须对齐 target 交集、候选数和排名规则，并报告缺失预测。

## constraints

不能将 outputs 或来源结果 CSV 当真值用于训练。gzip、链名、assembly、残基映射和缺失原子处理须一致；历史结果与本地重算结果分开标记。
