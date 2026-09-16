# 实例任务：医学数据与任务定义 @ B100

- domain: bio
- 骨架: bio-medical-data-task-definition-task
- 场景: bio-longitudinal-chest-ct-change-detection-and-report-generation-scenario (B100)
- step_id: s01
- depend: []

## 场景研究主体
- B100
- 关联论文: ALTER: Modeling Longitudinal Changes via Regional Differencing for 3D CT Report Generation | doi:

## 本实例步骤描述
读取纵向胸部CT变化检测与报告生成所需的去标识影像和临床文本。

## 本实例执行 prompt
读取{MEDICAL_INPUT}并核对去标识状态，使用{MODEL_NAME}建立{MODALITY}模态的纵向胸部CT变化检测与报告生成任务。

## 本实例输入槽
- {MEDICAL_INPUT} | required=True | type=doc | var_name=医学输入 | hint=输入去标识医学数据 | default=paired_chest_ct.json
- {MODEL_NAME} | required=True | type=enum | var_name=医学模型 | hint=选择场景使用的模型 | default=ALTER
- {MODALITY} | required=False | type=enum | var_name=影像模态 | hint=选择医学影像模态 | default=CT

## 本实例产出
- 去标识输入
- 影像元数据
- 任务配置

## 本实例质量门禁
- 患者标识已移除
- 影像序列可解析
- 模态与模型兼容

## 可调资源（edge:resource，仅真实存在）
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
