# 骨架任务：输入与任务定义

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 校验OpenFold组件消融与结构泛化评测所需的序列、链组成和任务设置。
- 校验原子级蛋白表征驱动的结构预测所需的序列、链组成和任务设置。
- 校验无MSA蛋白质快速折叠预测所需的序列、链组成和任务设置。
- 校验物理反馈约束的蛋白构象集合生成所需的序列、链组成和任务设置。
- 校验蛋白质单体结构预测与置信度评估所需的序列、链组成和任务设置。
- 校验蛋白质复合物结构精修与质量评估所需的序列、链组成和任务设置。
- 校验蛋白质多构象状态空间生成与筛选所需的序列、链组成和任务设置。
- 校验蛋白质核酸配体复合物全原子结构预测所需的序列、链组成和任务设置。
- 校验蛋白质配体复合物结构与结合亲和力联合预测所需的序列、链组成和任务设置。
- 校验轻量化多分子复合物结构预测所需的序列、链组成和任务设置。

## 执行 prompt（跨场景聚合去重）
- 读取{INPUT_DATA}，检查实体、序列和链标识，使用{MODEL_NAME}并按{CHAIN_MODE}建立OpenFold组件消融与结构泛化评测任务。
- 读取{INPUT_DATA}，检查实体、序列和链标识，使用{MODEL_NAME}并按{CHAIN_MODE}建立原子级蛋白表征驱动的结构预测任务。
- 读取{INPUT_DATA}，检查实体、序列和链标识，使用{MODEL_NAME}并按{CHAIN_MODE}建立无MSA蛋白质快速折叠预测任务。
- 读取{INPUT_DATA}，检查实体、序列和链标识，使用{MODEL_NAME}并按{CHAIN_MODE}建立物理反馈约束的蛋白构象集合生成任务。
- 读取{INPUT_DATA}，检查实体、序列和链标识，使用{MODEL_NAME}并按{CHAIN_MODE}建立蛋白质单体结构预测与置信度评估任务。
- 读取{INPUT_DATA}，检查实体、序列和链标识，使用{MODEL_NAME}并按{CHAIN_MODE}建立蛋白质复合物结构精修与质量评估任务。
- 读取{INPUT_DATA}，检查实体、序列和链标识，使用{MODEL_NAME}并按{CHAIN_MODE}建立蛋白质多构象状态空间生成与筛选任务。
- 读取{INPUT_DATA}，检查实体、序列和链标识，使用{MODEL_NAME}并按{CHAIN_MODE}建立蛋白质核酸配体复合物全原子结构预测任务。
- 读取{INPUT_DATA}，检查实体、序列和链标识，使用{MODEL_NAME}并按{CHAIN_MODE}建立蛋白质配体复合物结构与结合亲和力联合预测任务。
- 读取{INPUT_DATA}，检查实体、序列和链标识，使用{MODEL_NAME}并按{CHAIN_MODE}建立轻量化多分子复合物结构预测任务。

## 输入槽（var/hint/default）
- {INPUT_DATA} | required=True | type=doc | var_name=序列或结构输入 | hint=输入FASTA或结构文件 | default=8a1v.json
- {MODEL_NAME} | required=True | type=enum | var_name=结构模型 | hint=选择场景使用的模型 | default=Protenix
- {CHAIN_MODE} | required=False | type=enum | var_name=链处理模式 | hint=指定单链或多链处理 | default=auto

## 产出
- 任务配置
- 实体清单
- 标准化输入

## 质量门禁 quality_gate
- 模型支持输入实体
- 输入可被解析
- 链标识唯一

## 可调资源（edge:resource，仅真实存在）
- models/alphafold
- models/alphafold3
- models/openfold

## 实例任务（本骨架在各场景的实例化）
- it-1192fb8f
- it-3e8c23f0
- it-46e133e4
- it-4a4dd09a
- it-4ee1896a
- it-8d349f0a
- it-8e3c8571
- it-a5364a83
- it-a9f3f382
- it-d30f1880

## 复用场景
- B02
- B08
- B03
- B10
- B01
- B09
- B07
- B04
- B05
- B06
