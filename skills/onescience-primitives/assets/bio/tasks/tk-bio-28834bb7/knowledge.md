# 骨架任务：分子设计目标定义

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 解析Best-of-K对齐的靶标特异性三维分子生成的靶点、种子分子和生成任务。
- 解析SMILES基础模型驱动的ADMET性质预测的靶点、种子分子和生成任务。
- 解析一维语言与三维扩散融合的分子生成的靶点、种子分子和生成任务。
- 解析亲和力梯度引导的口袋条件分子生成的靶点、种子分子和生成任务。
- 解析全原子流匹配的三维小分子从头生成的靶点、种子分子和生成任务。
- 解析分子潜空间扩散进化与多位点抑制剂设计的靶点、种子分子和生成任务。
- 解析合成路线约束的GFlowNet分子生成的靶点、种子分子和生成任务。
- 解析多任务靶点感知的三维分子生成的靶点、种子分子和生成任务。
- 解析形状静电药效团联合的生物电子等排体设计的靶点、种子分子和生成任务。
- 解析正负活性联合引导的靶向小分子生成的靶点、种子分子和生成任务。

## 执行 prompt（跨场景聚合去重）
- 读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的Best-of-K对齐的靶标特异性三维分子生成任务。
- 读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的SMILES基础模型驱动的ADMET性质预测任务。
- 读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的一维语言与三维扩散融合的分子生成任务。
- 读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的亲和力梯度引导的口袋条件分子生成任务。
- 读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的全原子流匹配的三维小分子从头生成任务。
- 读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的分子潜空间扩散进化与多位点抑制剂设计任务。
- 读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的合成路线约束的GFlowNet分子生成任务。
- 读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的多任务靶点感知的三维分子生成任务。
- 读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的形状静电药效团联合的生物电子等排体设计任务。
- 读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的正负活性联合引导的靶向小分子生成任务。

## 输入槽（var/hint/default）
- {MOLECULE_INPUT} | required=True | type=doc | var_name=分子设计输入 | hint=输入靶点或分子文件 | default=target_activity.csv
- {MODEL_NAME} | required=True | type=enum | var_name=分子模型 | hint=选择场景使用的模型 | default=TargetDiff
- {GENERATION_MODE} | required=False | type=enum | var_name=生成模式 | hint=选择分子生成任务 | default=de_novo

## 产出
- 标准化分子输入
- 生成任务配置
- 靶点条件

## 质量门禁 quality_gate
- 分子化学价合法
- 生成模式与输入兼容
- 靶点条件可解析

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-0216b211
- it-4dc3c67c
- it-5058c460
- it-5fb9187e
- it-6995d86d
- it-6cc32e7f
- it-94358d4e
- it-b9814324
- it-ba0b7db3
- it-ef25defa

## 复用场景
- B53
- B56
- B57
- B54
- B59
- B52
- B58
- B60
- B55
- B51
