---
name: bio-biomarker-machine-learning
description: 组学生物标志物机器学习 skill。用于高维 omics classifier、feature selection、nested CV、batch-aware split、survival analysis、SHAP/LIME 解释、模型卡和验证报告交接。
---

# 生物标志物机器学习

## 使用边界

用于从表达、甲基化、突变、蛋白质组、代谢组、微生物组或多组学特征中训练/评估诊断、预后或疗效预测模型。若涉及 OneScience 模型内部训练，必须回到 `../../onescience-models/SKILL.md`。

## 可复用资源

- `onescience-coder/assets/bio_table_templates/biomarker_model_card.yaml`：数据、endpoint、split、模型、指标、解释和验证模板。
- `references/biomarker_ml_validation.md`：数据泄漏、嵌套交叉验证、特征选择、生存模型和解释边界。
- `onescience-coder/assets/bio_table_qc_tools/feature_table_leakage_check.py`：检查 feature table 的重复 ID、split 泄漏和 endpoint 缺失。

## 推荐流程

1. 明确 endpoint：diagnosis、response、survival、recurrence、toxicity 或 subtype。
2. 数据设计：样本层级、batch、patient/case split、外部验证、缺失值机制。
3. 预处理：normalization、feature filtering、batch correction、train-only feature selection。
4. 模型：regularized logistic/Cox、RF/XGBoost、SVM、survival forest；避免超小样本深度模型。
5. 验证：nested CV、calibration、confidence interval、external validation、subgroup performance。
6. 解释：SHAP/LIME/coefficients、稳定性、biological plausibility 和实验 follow-up。

## 交接物

```yaml
bio_task_family: translational-biomarker
translational_task: biomarker-machine-learning
endpoint:
feature_table:
cohort_split:
preprocessing:
feature_selection:
model_family:
validation_plan:
interpretability:
expected_outputs:
execution_entry:
```

## 禁止事项

- 不要在全数据上做特征选择后再交叉验证。
- 不要按样本随机划分会泄漏 patient/case/repeated measure 的数据。
- 不要只报告 accuracy；需要 AUC/PR、calibration、CI 和外部验证风险。
