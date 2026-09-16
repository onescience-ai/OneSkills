# 实例任务：受体配体输入预检 @ B48

- domain: bio
- 骨架: bio-receptor-ligand-input-precheck-task
- 场景: bio-lightweight-interpretable-protein-ligand-conformation-prediction-scenario (B48)
- step_id: s01
- depend: []

## 场景研究主体
- B48
- 关联论文: QuickBind: A Light-Weight And Interpretable Molecular Docking Model | doi:

## 本实例步骤描述
标准化轻量可解释的蛋白配体构象预测的受体、配体或候选姿态输入。

## 本实例执行 prompt
读取{DOCKING_INPUT}，按{ADD_HYDROGENS}处理质子化状态，并用{MODEL_NAME}建立轻量可解释的蛋白配体构象预测任务。

## 本实例输入槽
- {DOCKING_INPUT} | required=True | type=doc | var_name=对接输入 | hint=输入复合物或配体数据 | default=quickbind_pairs.csv
- {MODEL_NAME} | required=True | type=enum | var_name=对接模型 | hint=选择场景使用的模型 | default=QuickBind
- {ADD_HYDROGENS} | required=False | type=bool | var_name=补充氢原子 | hint=是否标准化质子化状态 | default=True

## 本实例产出
- 标准化受体
- 标准化配体
- 输入异常清单

## 本实例质量门禁
- 受体结构可解析
- 配体化学价合法
- 实体标识不重复

## 可调资源（edge:resource，仅真实存在）
- models/diffdock
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
