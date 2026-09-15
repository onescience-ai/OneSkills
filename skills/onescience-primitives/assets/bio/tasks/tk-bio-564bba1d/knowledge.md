# 骨架任务：特征与模型准备

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 准备模型权重、序列比对和结构模板特征。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}，按{MSA_MODE}准备序列特征并最多保留{MAX_TEMPLATES}个模板。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=model_v0.5.0.pt
- {MSA_MODE} | required=False | type=enum | var_name=MSA模式 | hint=选择MSA准备方式 | default=precomputed
- {MAX_TEMPLATES} | required=False | type=int | var_name=模板上限 | hint=限制结构模板数量 | default=4

## 产出
- 序列特征
- 模型加载记录
- 模板特征

## 质量门禁 quality_gate
- 权重版本可追溯
- 模板数量不超限
- 特征长度一致

## 可调资源（edge:resource，仅真实存在）
- tools/biopython

## 实例任务（本骨架在各场景的实例化）
- it-17f441bd
- it-24f52d30
- it-309b6c25
- it-4ade8d78
- it-5eb2effa
- it-88da0b4a
- it-9e8b62b4
- it-a572dad5
- it-b6d8102c
- it-ffe52a32

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
