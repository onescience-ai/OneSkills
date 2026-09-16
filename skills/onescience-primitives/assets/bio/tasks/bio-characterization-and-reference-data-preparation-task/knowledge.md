# 骨架任务：表征与参考数据准备

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 加载权重并构建序列、结构或底物联合表征。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}和{REFERENCE_DATA}，将序列裁剪或分块至{MAX_SEQUENCE_LENGTH}并生成联合表征。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=enzyclip.pt
- {REFERENCE_DATA} | required=False | type=doc | var_name=参考数据 | hint=参考数据集名称 | default=UniProtKB_2025_01
- {MAX_SEQUENCE_LENGTH} | required=False | type=int | var_name=序列长度上限 | hint=限制模型输入长度 | default=1024

## 产出
- 参考标签映射
- 蛋白表征
- 预处理日志

## 质量门禁 quality_gate
- 参考标签无重复冲突
- 序列分块可回溯
- 权重加载成功

## 可调资源（edge:resource，仅真实存在）
- tools/pdb-structure-data-access

## 实例任务（本骨架在各场景的实例化）
- bio-characterization-and-reference-deep-mutational-scanning-inst
- bio-characterization-and-reference-enzyme-classification-and-inst
- bio-characterization-and-reference-enzyme-sequence-and-substrat-inst
- bio-characterization-and-reference-equivariant-structural-inst
- bio-characterization-and-reference-evolutionary-spectrum-inst
- bio-characterization-and-reference-few-shot-multimodal-protein-inst
- bio-characterization-and-reference-multi-scale-representation-inst
- bio-characterization-and-reference-preference-optimization-inst
- bio-characterization-and-reference-protein-mutation-effect-inst
- bio-characterization-and-reference-residual-based-interpretable-inst

## 复用场景
- B39
- B32
- B38
- B37
- B31
- B34
- B35
- B36
- B40
- B33
