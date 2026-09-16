# 实例任务：细胞状态推理与生成 @ B73

- domain: bio
- 骨架: bio-cell-state-inference-and-generation-task
- 场景: bio-cross-cell-type-and-dose-perturbation-response-prediction-scenario (B73)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B73
- 关联论文: Benchmarking virtual cell models for in-the-wild perturbation response | doi:; AROMA: Augmented Reasoning Over a Multimodal Architecture for Virtual Cell Genetic Perturbation Modeling | doi:; Predicting cellular responses to perturbation across diverse contexts with State | doi:

## 本实例步骤描述
执行表征、注释、扰动预测或空间恢复任务。

## 本实例执行 prompt
运行跨细胞类型与剂量的扰动响应预测，以种子{SEED}为{TARGET_GENES}相关条件产生{NUM_SAMPLES}个预测或表征样本。

## 本实例输入槽
- {TARGET_GENES} | required=False | type=list[str] | var_name=目标基因 | hint=列出重点分析基因 | default=['TP53', 'MYC', 'CD3D']
- {NUM_SAMPLES} | required=True | type=int | var_name=采样数量 | hint=设置每条件采样细胞数 | default=128
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定采样与评测结果 | default=19

## 本实例产出
- 细胞级结果
- 基因级结果
- 推理日志

## 本实例质量门禁
- 所有细胞有唯一结果
- 输出基因顺序一致
- 采样数量符合配置

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
