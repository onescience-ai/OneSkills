# 实例任务：受体配体输入预检 @ B45

- domain: bio
- 骨架: tk-bio-28410bf5
- 场景: sc-d043311e (B45)
- step_id: s01
- depend: []

## 场景研究主体
- B45
- 关联论文: FABind+: Enhancing Molecular Docking through Improved Pocket Prediction and Pose Generation | doi:; RAPID-Net: Accurate Pocket Identification for Binding-Site-Agnostic Docking | doi:

## 本实例步骤描述
标准化口袋预测增强的蛋白配体快速对接的受体、配体或候选姿态输入。

## 本实例执行 prompt
读取{DOCKING_INPUT}，按{ADD_HYDROGENS}处理质子化状态，并用{MODEL_NAME}建立口袋预测增强的蛋白配体快速对接任务。

## 本实例输入槽
- {DOCKING_INPUT} | required=True | type=doc | var_name=对接输入 | hint=输入复合物或配体数据 | default=benchmark_complexes.csv
- {MODEL_NAME} | required=True | type=enum | var_name=对接模型 | hint=选择场景使用的模型 | default=FABind+
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

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
