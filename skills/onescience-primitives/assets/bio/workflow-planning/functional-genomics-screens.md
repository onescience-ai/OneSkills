# 功能基因组筛选工作流

- workflow_id: `functional-genomics-screens`

## 适用范围

用于 pooled CRISPR screen、RNAi screen、Perturb-seq、DepMap/gene essentiality、sgRNA count matrix、library QC、MAGeCK/RRA 风格 hit calling 和候选基因优先级交接。

## 输入

- 必需：library annotation；sgRNA/gene mapping；FASTQ 或 sgRNA count matrix；sample metadata；condition/timepoint/replicate 设计；control guides。
- Perturb-seq 分支：single-cell object、guide assignment、MOI 信息。
- 可选：DepMap/context database、positive/negative controls、validation assay 需求。

## 输出

- sgRNA count/QC 表。
- gene hit table、sgRNA table、effect size、FDR。
- library representation、Gini index、control guide behavior。
- Perturb-seq differential response 表。
- candidate prioritization 和验证建议。

## 流程节点

1. 校验 library、control guides、replicate、timepoint 和 contrast。
2. 计算 guide counts、mapping rate、library representation、bottleneck 和 Gini index。
3. 选择 depletion/enrichment、time-course 或 paired-condition hit calling 分支。
4. Perturb-seq 分支先进行细胞 QC、guide assignment 和 perturbation-level DE。
5. 按 effect size、FDR、replicate support、control guide 行为和先验证据排序候选。
6. 输出 screen 统计、候选表和验证交接。

## 边界与分流

- Perturb-seq 的纯 scRNA 预处理先走 `single-cell-rna-analysis`。
- screen hit 是候选优先级，不等于基因机制证明。
- 不用单条 sgRNA 变化直接代表 gene-level hit。

## 模型与工具选择边界

- pooled CRISPR/RNAi 使用 count-based screen 工具和 RRA/MAGeCK 类思路。
- Perturb-seq 使用单细胞工作流 + perturbation-aware DE。
- DepMap 只作为背景证据，不直接替代本实验 hit calling。

## 质量检查

- library representation 足够。
- control guides 表现正常。
- replicate concordance 和 batch/timepoint 结构可解释。
- bottleneck、Gini index、mapping rate 达标。
- multiple testing correction 有记录。

## 回退策略

- 缺 library annotation：停止 gene-level hit calling，只做 guide-level QC。
- representation 失败：不解释 dropout hit，只输出失败原因。
- replicate 不足：输出探索性候选，标记验证需求。

## 资源召回建议

- screen plan 模板：`bio_workflow_template_app`。
- Perturb-seq 分支：`bio_single_cell_analysis_app`。
- feature matrix 和候选表：`bio_table_qc_biomarker_app`。
