# 实例任务：基因组输入与坐标规范化 @ B67

- domain: bio
- 骨架: bio-genome-input-coordinate-normalization-task
- 场景: bio-cell-type-specific-regulatory-dna-conditional-generation-scenario (B67)
- step_id: s01
- depend: []

## 场景研究主体
- B67
- 关联论文: Conditional Monte Carlo Tree Diffusion for Designing Cell-Type-Specific and Biologically Faithful Regulatory DNA | doi:

## 本实例步骤描述
读取细胞类型特异调控DNA条件生成的DNA、区间、变异或表观信号。

## 本实例执行 prompt
读取{GENOMICS_INPUT}，相对{REFERENCE_GENOME}校验序列和坐标，使用{MODEL_NAME}建立细胞类型特异调控DNA条件生成任务。

## 本实例输入槽
- {GENOMICS_INPUT} | required=True | type=doc | var_name=基因组输入 | hint=输入序列区间或变异 | default=celltype_tracks.bed
- {MODEL_NAME} | required=True | type=enum | var_name=基因组模型 | hint=选择场景使用的模型 | default=Monte Carlo Tree Diffusion
- {REFERENCE_GENOME} | required=False | type=enum | var_name=参考基因组 | hint=选择坐标参考版本 | default=hg38

## 本实例产出
- 标准化基因组输入
- 坐标检查报告
- 任务配置

## 本实例质量门禁
- 坐标位于参考范围
- 等位基因方向一致
- 样本标识唯一

## 可调资源（edge:resource，仅真实存在）
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
