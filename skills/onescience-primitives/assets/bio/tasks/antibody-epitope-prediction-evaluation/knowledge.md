# Antibody Epitope Prediction Evaluation

## 适用范围
Task for evaluating computational models that predict antibody binding sites (epitopes/paratopes) on antigens. Use this task when benchmarking prediction methods, assessing model performance, or comparing different approaches. Covers standard metrics, dataset splitting strategies, baseline comparisons, and statistical validation for computational immunology applications.

## 输入
- **Model predictions**: Per-residue binding probability scores or binary predictions
- **Ground truth labels**: Experimentally validated binding site annotations
- **Dataset splits**: Training/validation/test partitions with抗原 family stratification
- **Baseline methods**: Reference predictions from established tools (Discotope-2, IEVpred, etc.)

## 输出
- **Performance metrics**: AUPRC, AUROC, F1, precision, recall, MCC scores
- **Statistical analysis**: Confidence intervals, significance tests, effect sizes
- **Stratified results**: Performance by antigen family, CDR type, antibody class
- **Comparison report**: Method ranking, strengths/weaknesses analysis

## 流程节点
1. **Dataset preparation** → Split data into independent train/valid/test sets
2. **Prediction generation** → Run model on test set, output per-residue scores
3. **Threshold selection** → Optimize classification threshold on validation set
4. **Metric computation** → Calculate AUPRC, AUROC, F1, precision, recall, MCC
5. **Statistical testing** → Bootstrap confidence intervals, paired t-tests
6. **Stratified analysis** → Evaluate by抗原 family, CDR type, structural class
7. **Baseline comparison** → Compare against Discotope-2, IEVpred, DiscoTope, etc.
8. **Report generation** → Compile results with visualizations and recommendations

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| AUPRC | Primary metric | [1] | Area Under Precision-Recall Curve for imbalanced data |
| AUROC | Secondary metric | [1] | Area Under ROC Curve for overall discrimination |
| F1 score | Harmonic mean | [1] | Balance of precision and recall |
| MCC | Matthews Correlation Coefficient | [1] | Robust metric for imbalanced classes |
| Interface cutoff | 5 Å | [1] | Standard distance for binding site definition |
| Test set size | >100 complexes | [1] | Minimum for reliable performance estimates |

## 边界与分流
- **Class imbalance**: Binding sites are small fraction of residues; use AUPRC not just accuracy
- **Data leakage**: Ensure no sequence/structure redundancy between train and test sets
- **Threshold sensitivity**: F1/AUPRC depend on threshold; report threshold-independent metrics
- **Baseline fairness**: Compare methods on same dataset splits with same evaluation protocol

## 质量检查
- Verify ground truth labels are experimentally validated (not computational predictions)
- Check test set independence from training data (sequence identity <30%)
- Confirm metrics are computed correctly with proper handling of edge cases
- Validate statistical significance with appropriate tests (paired, multiple comparison correction)

## 回退策略
- If no independent test data, use cross-validation with careful data splitting
- For limited experimental data, use structural proximity as binding site proxy
- If baselines unavailable, compare against random and consensus predictions
- Consider semi-supervised evaluation when labeled data is scarce

## 资源召回建议
- When benchmarking antibody binding site prediction methods
- When validating computational models against experimental data
- When comparing multiple prediction approaches for the same task
- Pair with SAbDab for benchmark datasets and ANARCI for CDR annotations

## 证据来源
[1] Guest JD, Vreven T, Zhou J, et al. An expanded benchmark for antibody-antigen docking and affinity prediction reveals insights into antibody recognition determinants. Structure. 2021;29(3):308-319.e4. doi:10.1016/j.str.2021.01.005
[2] Fromm S, Ludaic M, Elofsson A. Evaluating deep learning based structure prediction methods on antibody-antigen complexes. Bioinformatics. 2026;42(3):btag136. doi:10.1093/bioinformatics/btag136