# 骨架任务：受体配体输入预检

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 标准化全局盲对接构象生成与置信度排序的受体、配体或候选姿态输入。
- 标准化口袋预测增强的蛋白配体快速对接的受体、配体或候选姿态输入。
- 标准化多口袋条件的物理有效对接的受体、配体或候选姿态输入。
- 标准化对接引导的超大规模虚拟筛选的受体、配体或候选姿态输入。
- 标准化未知结合位点的蛋白口袋识别的受体、配体或候选姿态输入。
- 标准化测地路径引导的柔性分子对接的受体、配体或候选姿态输入。
- 标准化物理规则约束的对接姿态重排序的受体、配体或候选姿态输入。
- 标准化蛋白配体联合生成对接与亲和力预测的受体、配体或候选姿态输入。
- 标准化轻量可解释的蛋白配体构象预测的受体、配体或候选姿态输入。
- 标准化高精度蛋白配体对接与几何修正的受体、配体或候选姿态输入。

## 执行 prompt（跨场景聚合去重）
- 读取{DOCKING_INPUT}，按{ADD_HYDROGENS}处理质子化状态，并用{MODEL_NAME}建立全局盲对接构象生成与置信度排序任务。
- 读取{DOCKING_INPUT}，按{ADD_HYDROGENS}处理质子化状态，并用{MODEL_NAME}建立口袋预测增强的蛋白配体快速对接任务。
- 读取{DOCKING_INPUT}，按{ADD_HYDROGENS}处理质子化状态，并用{MODEL_NAME}建立多口袋条件的物理有效对接任务。
- 读取{DOCKING_INPUT}，按{ADD_HYDROGENS}处理质子化状态，并用{MODEL_NAME}建立对接引导的超大规模虚拟筛选任务。
- 读取{DOCKING_INPUT}，按{ADD_HYDROGENS}处理质子化状态，并用{MODEL_NAME}建立未知结合位点的蛋白口袋识别任务。
- 读取{DOCKING_INPUT}，按{ADD_HYDROGENS}处理质子化状态，并用{MODEL_NAME}建立测地路径引导的柔性分子对接任务。
- 读取{DOCKING_INPUT}，按{ADD_HYDROGENS}处理质子化状态，并用{MODEL_NAME}建立物理规则约束的对接姿态重排序任务。
- 读取{DOCKING_INPUT}，按{ADD_HYDROGENS}处理质子化状态，并用{MODEL_NAME}建立蛋白配体联合生成对接与亲和力预测任务。
- 读取{DOCKING_INPUT}，按{ADD_HYDROGENS}处理质子化状态，并用{MODEL_NAME}建立轻量可解释的蛋白配体构象预测任务。
- 读取{DOCKING_INPUT}，按{ADD_HYDROGENS}处理质子化状态，并用{MODEL_NAME}建立高精度蛋白配体对接与几何修正任务。

## 输入槽（var/hint/default）
- {DOCKING_INPUT} | required=True | type=doc | var_name=对接输入 | hint=输入复合物或配体数据 | default=crossdocked_test.csv
- {MODEL_NAME} | required=True | type=enum | var_name=对接模型 | hint=选择场景使用的模型 | default=DeltaDock
- {ADD_HYDROGENS} | required=False | type=bool | var_name=补充氢原子 | hint=是否标准化质子化状态 | default=True

## 产出
- 标准化受体
- 标准化配体
- 输入异常清单

## 质量门禁 quality_gate
- 受体结构可解析
- 实体标识不重复
- 配体化学价合法

## 可调资源（edge:resource，仅真实存在）
- models/diffdock

## 实例任务（本骨架在各场景的实例化）
- it-01684b6f
- it-12fd2eeb
- it-31d3e61b
- it-3579955a
- it-4beb2f97
- it-62e105b5
- it-93e4f79f
- it-96939b02
- it-c7cfab8a
- it-e2e825ed

## 复用场景
- B41
- B45
- B50
- B47
- B46
- B49
- B42
- B43
- B48
- B44
