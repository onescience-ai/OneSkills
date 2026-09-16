# 骨架任务：预处理与模型表征

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 加载权重并执行归一化、基因对齐和批次编码。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}，按{BATCH_KEY}编码批次，并依据{NORMALIZE_COUNTS}处理计数后生成模型表征。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=state.ckpt
- {BATCH_KEY} | required=False | type=str | var_name=批次字段 | hint=填写批次元数据列名 | default=batch
- {NORMALIZE_COUNTS} | required=False | type=bool | var_name=归一化计数 | hint=是否执行总量归一化 | default=True

## 产出
- 模型输入矩阵
- 细胞表征
- 预处理日志

## 质量门禁 quality_gate
- 基因词表已对齐
- 批次标签无缺失
- 输入数值均为有限值

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- bio-preprocessing-model-representa-causal-latent-diffusion-inst
- bio-preprocessing-model-representa-cross-cell-type-and-dose-inst
- bio-preprocessing-model-representa-geneformer-scgpt-single-inst
- bio-preprocessing-model-representa-mcmc-guided-multi-omics-inst
- bio-preprocessing-model-representa-multimodal-reasoning-enhance-inst
- bio-preprocessing-model-representa-scgpt-hematopoietic-cell-inst
- bio-preprocessing-model-representa-single-cell-chromatin-inst
- bio-preprocessing-model-representa-single-cell-to-spatial-inst
- bio-preprocessing-model-representa-spatial-transcriptomics-and-inst
- bio-preprocessing-model-representa-spatial-transcriptomics-inst

## 复用场景
- B72
- B75
- B71
- B77
- B76
- B79
- B74
- B80
- B78
- B73
