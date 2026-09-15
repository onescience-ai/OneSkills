# 骨架任务：医学数据与任务定义

- domain: bio
- 复用场景数: 3
- 实例任务数: 3

## 步骤描述（跨场景聚合去重）
- 读取临床奖励对齐的胸部X线报告生成所需的去标识影像和临床文本。
- 读取医学文本与影像多模态问答及报告辅助所需的去标识影像和临床文本。
- 读取纵向胸部CT变化检测与报告生成所需的去标识影像和临床文本。

## 执行 prompt（跨场景聚合去重）
- 读取{MEDICAL_INPUT}并核对去标识状态，使用{MODEL_NAME}建立{MODALITY}模态的临床奖励对齐的胸部X线报告生成任务。
- 读取{MEDICAL_INPUT}并核对去标识状态，使用{MODEL_NAME}建立{MODALITY}模态的医学文本与影像多模态问答及报告辅助任务。
- 读取{MEDICAL_INPUT}并核对去标识状态，使用{MODEL_NAME}建立{MODALITY}模态的纵向胸部CT变化检测与报告生成任务。

## 输入槽（var/hint/default）
- {MEDICAL_INPUT} | required=True | type=doc | var_name=医学输入 | hint=输入去标识医学数据 | default=paired_chest_ct.json
- {MODEL_NAME} | required=True | type=enum | var_name=医学模型 | hint=选择场景使用的模型 | default=ALTER
- {MODALITY} | required=False | type=enum | var_name=影像模态 | hint=选择医学影像模态 | default=CT

## 产出
- 任务配置
- 去标识输入
- 影像元数据

## 质量门禁 quality_gate
- 影像序列可解析
- 患者标识已移除
- 模态与模型兼容

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-0886e946
- it-98fdd59c
- it-adb735f5

## 复用场景
- B99
- B98
- B100
