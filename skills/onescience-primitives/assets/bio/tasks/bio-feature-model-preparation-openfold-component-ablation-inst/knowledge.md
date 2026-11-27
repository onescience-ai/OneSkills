# 实例任务：特征与模型准备 @ B02

- domain: bio
- 骨架: bio-feature-model-preparation-task
- 场景: bio-openfold-component-ablation-structural-generalization-scenario (B02)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B02
- 关联论文: Quantifying the Role of OpenFold Components in Protein Structure Prediction | doi:; Highly accurate protein structure prediction with AlphaFold | doi:; OpenFold: Retraining AlphaFold2 yields new insights into its learning mechanisms and capacity for generalization | doi:

## 本实例步骤描述
准备模型权重、序列比对和结构模板特征。

## 本实例执行 prompt
按实际 OpenFold 配置加载{CHECKPOINT}，按{MSA_MODE}准备序列特征并最多保留{MAX_TEMPLATES}个模板。

- **MSA 与模板**：预计算 MSA 的查询序列须匹配靶标；单序列输入是单独的条件，不能作为有 MSA 的基线。模板须满足预先确定的时间截止条件，并排除独立评测靶标的参考结构；区分模板上限和实际采用数。
- **模板消融**：使用同一权重，只改变实际输入的模板特征；不用不同训练分支的权重代替。
- **损失消融**：使用训练条件可比、确有不同训练损失的成对权重。推理时切换配置不能改变训练损失；没有可比权重时不报告该组效应。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=finetuning_ptm_2.pt
- {MSA_MODE} | required=False | type=enum | var_name=MSA模式 | hint=选择MSA准备方式 | default=precomputed
- {MAX_TEMPLATES} | required=False | type=int | var_name=模板上限 | hint=限制结构模板数量 | default=4

## 本实例产出
- 模型加载记录
- 序列特征
- 模板特征

## 本实例质量门禁
- 权重版本可追溯
- 特征长度一致
- 模板数量不超限

## 可调资源（edge:resource，仅真实存在）
- tools/biopython

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
