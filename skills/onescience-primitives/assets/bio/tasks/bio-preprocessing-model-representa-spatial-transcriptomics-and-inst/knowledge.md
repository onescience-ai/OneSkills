# 实例任务：预处理与模型表征 @ B80

- domain: bio
- 骨架: bio-preprocessing-model-representation-task
- 场景: bio-spatial-transcriptomics-and-proteomics-basic-representation-scenario (B80)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B80
- 关联论文: HEIST: A Graph Foundation Model for Spatial Transcriptomics and Proteomics Data | doi:

## 本实例步骤描述
加载权重并执行归一化、基因对齐和批次编码。

## 本实例执行 prompt
加载{CHECKPOINT}，按{BATCH_KEY}编码批次，并依据{NORMALIZE_COUNTS}处理计数后生成模型表征。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=heist.pt
- {BATCH_KEY} | required=False | type=str | var_name=批次字段 | hint=填写批次元数据列名 | default=batch
- {NORMALIZE_COUNTS} | required=False | type=bool | var_name=归一化计数 | hint=是否执行总量归一化 | default=True

## 本实例产出
- 模型输入矩阵
- 细胞表征
- 预处理日志

## 本实例质量门禁
- 基因词表已对齐
- 批次标签无缺失
- 输入数值均为有限值

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
