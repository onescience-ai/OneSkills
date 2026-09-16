# 实例任务：表征与参考数据准备 @ B38

- domain: bio
- 骨架: bio-characterization-and-reference-data-preparation-task
- 场景: bio-multi-scale-representation-protein-fitness-prediction-scenario (B38)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B38
- 关联论文: Multi-Scale Representation Learning for Protein Fitness Prediction | doi:

## 本实例步骤描述
加载权重并构建序列、结构或底物联合表征。

## 本实例执行 prompt
加载{CHECKPOINT}和{REFERENCE_DATA}，将序列裁剪或分块至{MAX_SEQUENCE_LENGTH}并生成联合表征。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=ms_fitness.pt
- {REFERENCE_DATA} | required=False | type=doc | var_name=参考数据 | hint=参考数据集名称 | default=UniProtKB_2025_01
- {MAX_SEQUENCE_LENGTH} | required=False | type=int | var_name=序列长度上限 | hint=限制模型输入长度 | default=1024

## 本实例产出
- 蛋白表征
- 参考标签映射
- 预处理日志

## 本实例质量门禁
- 权重加载成功
- 序列分块可回溯
- 参考标签无重复冲突

## 可调资源（edge:resource，仅真实存在）
- tools/pdb-structure-data-access

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
