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
- bio-feature-model-preparation-atom-level-protein-represent-inst
- bio-feature-model-preparation-lightweight-multi-molecular-inst
- bio-feature-model-preparation-msa-free-protein-fast-inst
- bio-feature-model-preparation-openfold-component-ablation-inst
- bio-feature-model-preparation-physical-feedback-constraine-inst
- bio-feature-model-preparation-protein-complex-structure-inst
- bio-feature-model-preparation-protein-ligand-complex-inst
- bio-feature-model-preparation-protein-monomer-structure-inst
- bio-feature-model-preparation-protein-multi-conformational-inst
- bio-feature-model-preparation-protein-nucleic-acid-ligand-inst

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
