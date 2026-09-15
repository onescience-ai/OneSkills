# 骨架任务：位点稳定性与选择性排序

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 结合局域配位保持、结构重构/脱附风险、关键中间体结合强度和反应路径，形成 Cu-NxBy 候选的 CH4 选择性—稳定性排序。

## 执行 prompt（跨场景聚合去重）
- 依据 {REACTION_ANALYSIS} 对 Cu-NxBy 候选排序；将 CH4 路径、HER 竞争、位点稳定性及验证数据分列，输出推荐、淘汰和待验证候选，不把单一描述符当作充分证据。

## 输入槽（var/hint/default）
- {REACTION_ANALYSIS} | required=True | type=doc | var_name=反应分析结果 | hint=s03 输出。 | default={REACTION_ANALYSIS}
- {VALIDATION_DATA} | required=False | type=doc | var_name=验证数据 | hint=实验性能和局域配位表征。 | default={VALIDATION_DATA}

## 产出
- CH4 选择性设计规则
- Cu-NxBy 候选排序
- 需实验验证的优先候选

## 质量门禁 quality_gate
- 排序依据可回溯到原始吸附/自由能/能垒数据
- 推荐位点的结构与配位环境明确
- 计算预测和实验观察分开报告

## 可调资源（edge:resource，仅真实存在）
- datapipes/xps-nife-oer-surface-analysis

## 实例任务（本骨架在各场景的实例化）
- it-74f6d045

## 复用场景
- Cu-NxBy_单原子位点CO2到CH4选择性优化
