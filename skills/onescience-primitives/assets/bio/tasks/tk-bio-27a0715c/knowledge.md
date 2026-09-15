# 骨架任务：细胞状态推理与生成

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 执行表征、注释、扰动预测或空间恢复任务。

## 执行 prompt（跨场景聚合去重）
- 运行Geneformer与scGPT单细胞知识可解释性比较，以种子{SEED}为{TARGET_GENES}相关条件产生{NUM_SAMPLES}个预测或表征样本。
- 运行MCMC引导的多组学单细胞扰动预测，以种子{SEED}为{TARGET_GENES}相关条件产生{NUM_SAMPLES}个预测或表征样本。
- 运行scGPT造血细胞表征与谱系结构解析，以种子{SEED}为{TARGET_GENES}相关条件产生{NUM_SAMPLES}个预测或表征样本。
- 运行单细胞到空间转录组的缺失表达恢复，以种子{SEED}为{TARGET_GENES}相关条件产生{NUM_SAMPLES}个预测或表征样本。
- 运行单细胞染色质可及性基础表征与注释，以种子{SEED}为{TARGET_GENES}相关条件产生{NUM_SAMPLES}个预测或表征样本。
- 运行因果潜扩散的未见扰动响应预测，以种子{SEED}为{TARGET_GENES}相关条件产生{NUM_SAMPLES}个预测或表征样本。
- 运行多模态推理增强的遗传扰动虚拟细胞预测，以种子{SEED}为{TARGET_GENES}相关条件产生{NUM_SAMPLES}个预测或表征样本。
- 运行空间转录组与蛋白组图基础表征，以种子{SEED}为{TARGET_GENES}相关条件产生{NUM_SAMPLES}个预测或表征样本。
- 运行空间转录组区域识别与组织架构解析，以种子{SEED}为{TARGET_GENES}相关条件产生{NUM_SAMPLES}个预测或表征样本。
- 运行跨细胞类型与剂量的扰动响应预测，以种子{SEED}为{TARGET_GENES}相关条件产生{NUM_SAMPLES}个预测或表征样本。

## 输入槽（var/hint/default）
- {TARGET_GENES} | required=False | type=list[str] | var_name=目标基因 | hint=列出重点分析基因 | default=['TP53', 'MYC', 'CD3D']
- {NUM_SAMPLES} | required=True | type=int | var_name=采样数量 | hint=设置每条件采样细胞数 | default=128
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定采样与评测结果 | default=19

## 产出
- 基因级结果
- 推理日志
- 细胞级结果

## 质量门禁 quality_gate
- 所有细胞有唯一结果
- 输出基因顺序一致
- 采样数量符合配置

## 可调资源（edge:resource，仅真实存在）
- tools/scanpy

## 实例任务（本骨架在各场景的实例化）
- it-13ba035a
- it-17ef0dad
- it-263c5120
- it-3f9d841d
- it-4e1afdf3
- it-58547f92
- it-dda434be
- it-e032ad6f
- it-e03bffb7
- it-e6e77ce5

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
