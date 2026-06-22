---
name: bio-population-genetics-gwas
description: 群体遗传与 GWAS skill。用于 PLINK/VCF QC、PCA、admixture、LD pruning、association testing、GWAS summary stats、selection statistics、Manhattan/QQ、Fst、Tajima D、iHS 和 XP-EHH 交接。
---

# 群体遗传与 GWAS

## 使用边界

用于个体级 genotype/VCF/PLINK 或 summary stats 的群体结构、关联分析和选择扫描。若任务是变异文件格式处理，先读 `../../data-foundation/variant-interval-files/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_population_templates/gwas_qc_manifest.csv`：样本、群体、表型、协变量、批次和文件路径模板。
- `references/popgen_gwas_qc.md`：PLINK QC、PCA/admixture、LD、GWAS 和选择扫描边界。
- `onescience-coder/assets/bio_population_tools/gwas_summary_qc.py`：对 GWAS summary stats 表做列检查、P 值范围和缺失汇总。

## 推荐流程

1. 明确输入层级：VCF、BED/BIM/FAM、summary stats、phenotype/covariate table。
2. 样本 QC：missingness、sex check、relatedness、heterozygosity、ancestry outlier。
3. 变异 QC：MAF、missingness、HWE、INFO/R2、LD pruning、build/liftover。
4. 群体结构：PCA、admixture、local ancestry 或 kinship。
5. 分析：linear/logistic/mixed model、selection statistics、LD block、fine-mapping handoff。
6. 输出：QC tables、PCA/Manhattan/QQ、association results、population caveats。

## 交接物

```yaml
bio_task_family: population-phylo-evolution
evolution_task: population-genetics-gwas
genotype_input:
phenotype_and_covariates:
reference_build:
sample_qc:
variant_qc:
population_structure:
analysis_model:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要在没有 ancestry/covariate 控制时解释 GWAS hit。
- 不要混用不同 genome build 或 allele coding。
- 不要把 summary stats 当作可恢复个体级信息。
