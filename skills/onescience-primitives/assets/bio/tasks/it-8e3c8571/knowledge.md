# 实例任务：输入与任务定义 @ B02

- domain: bio
- 骨架: tk-bio-05591214
- 场景: sc-36dea452 (B02)
- step_id: s01
- depend: []

## 场景研究主体
- B02
- 关联论文: Quantifying the Role of OpenFold Components in Protein Structure Prediction | doi:; Highly accurate protein structure prediction with AlphaFold | doi:; OpenFold: Retraining AlphaFold2 yields new insights into its learning mechanisms and capacity for generalization | doi:

## 本实例步骤描述
校验OpenFold组件消融与结构泛化评测所需的序列、链组成和任务设置。

## 本实例执行 prompt
读取{INPUT_DATA}，检查实体、序列和链标识，使用{MODEL_NAME}并按{CHAIN_MODE}建立OpenFold组件消融与结构泛化评测任务。

## 本实例输入槽
- {INPUT_DATA} | required=True | type=doc | var_name=序列或结构输入 | hint=输入FASTA或结构文件 | default=CAMEO_targets.fasta
- {MODEL_NAME} | required=True | type=enum | var_name=结构模型 | hint=选择场景使用的模型 | default=OpenFold
- {CHAIN_MODE} | required=False | type=enum | var_name=链处理模式 | hint=指定单链或多链处理 | default=auto

## 本实例产出
- 标准化输入
- 实体清单
- 任务配置

## 本实例质量门禁
- 输入可被解析
- 链标识唯一
- 模型支持输入实体

## 可调资源（edge:resource，仅真实存在）
- models/openfold

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
