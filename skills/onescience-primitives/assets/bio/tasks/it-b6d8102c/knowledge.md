# 实例任务：特征与模型准备 @ B07

- domain: bio
- 骨架: tk-bio-564bba1d
- 场景: sc-edd9ba1e (B07)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B07
- 关联论文: Expanding Protein Structure Prediction into Conformational State Space | doi:; Chai-1: Decoding the molecular interactions of life | doi:

## 本实例步骤描述
准备模型权重、序列比对和结构模板特征。

## 本实例执行 prompt
加载{CHECKPOINT}，按{MSA_MODE}准备序列特征并最多保留{MAX_TEMPLATES}个模板。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=chai1_model_v2.pt
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
