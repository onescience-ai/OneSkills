# 骨架任务：生物一致性与泛化评估

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 计算区域ARI并检查细胞类型、通路和空间结构保持。
- 计算反事实误差并检查细胞类型、通路和空间结构保持。
- 计算基因相关性并检查细胞类型、通路和空间结构保持。
- 计算宏平均F1并检查细胞类型、通路和空间结构保持。
- 计算差异表达相关并检查细胞类型、通路和空间结构保持。
- 计算扰动方向准确率并检查细胞类型、通路和空间结构保持。
- 计算概念纯度并检查细胞类型、通路和空间结构保持。
- 计算谱系保持率并检查细胞类型、通路和空间结构保持。
- 计算跨模态检索率并检查细胞类型、通路和空间结构保持。

## 执行 prompt（跨场景聚合去重）
- 基于{LABEL_KEY}和{MIN_CORRELATION}评估区域ARI、差异表达及结构保持并汇总失败条件。
- 基于{LABEL_KEY}和{MIN_CORRELATION}评估反事实误差、差异表达及结构保持并汇总失败条件。
- 基于{LABEL_KEY}和{MIN_CORRELATION}评估基因相关性、差异表达及结构保持并汇总失败条件。
- 基于{LABEL_KEY}和{MIN_CORRELATION}评估宏平均F1、差异表达及结构保持并汇总失败条件。
- 基于{LABEL_KEY}和{MIN_CORRELATION}评估差异表达相关、差异表达及结构保持并汇总失败条件。
- 基于{LABEL_KEY}和{MIN_CORRELATION}评估扰动方向准确率、差异表达及结构保持并汇总失败条件。
- 基于{LABEL_KEY}和{MIN_CORRELATION}评估概念纯度、差异表达及结构保持并汇总失败条件。
- 基于{LABEL_KEY}和{MIN_CORRELATION}评估谱系保持率、差异表达及结构保持并汇总失败条件。
- 基于{LABEL_KEY}和{MIN_CORRELATION}评估跨模态检索率、差异表达及结构保持并汇总失败条件。

## 输入槽（var/hint/default）
- {MIN_CORRELATION} | required=False | type=float | var_name=相关性下限 | hint=设置表达相关性下限 | default=0.5
- {LABEL_KEY} | required=False | type=str | var_name=评测标签字段 | hint=填写真实标签列名 | default=cell_type

## 产出
- 区域ARI明细
- 反事实误差明细
- 基因相关性明细
- 宏平均F1明细
- 差异表达相关明细
- 扰动方向准确率明细
- 概念纯度明细
- 生物一致性报告
- 评测结果
- 谱系保持率明细
- 跨模态检索率明细

## 质量门禁 quality_gate
- 低质量细胞已标记
- 结果保留原始细胞索引
- 训练测试样本隔离

## 可调资源（edge:resource，仅真实存在）
- tools/pydeseq2

## 实例任务（本骨架在各场景的实例化）
- it-1d2f8995
- it-20ed080c
- it-3ec888e0
- it-43868957
- it-60f40c7c
- it-8d0db938
- it-8f314933
- it-afc10836
- it-e5afde22
- it-faf6e17d

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
