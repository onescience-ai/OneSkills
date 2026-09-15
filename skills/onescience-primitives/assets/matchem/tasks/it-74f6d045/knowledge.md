# 实例任务：位点稳定性与选择性排序 @ Cu-NxBy_单原子位点CO2到CH4选择性优化

- domain: matchem
- 骨架: tk-matchem-3f89bcb1
- 场景: sc-9566751c (Cu-NxBy_单原子位点CO2到CH4选择性优化)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- Cu-NxBy_单原子位点CO2到CH4选择性优化
- 关联论文: Manipulating local coordination of copper single atom catalyst enables efficient CO2-to-CH4 conversion | doi:; The nature of active sites for carbon dioxide electroreduction over oxide-derived copper catalysts | doi:; Isolated copper–tin atomic interfaces tuning electrocatalytic CO2 conversion | doi:

## 本实例步骤描述
结合局域配位保持、结构重构/脱附风险、关键中间体结合强度和反应路径，形成 Cu-NxBy 候选的 CH4 选择性—稳定性排序。

## 本实例执行 prompt
依据 {REACTION_ANALYSIS} 对 Cu-NxBy 候选排序；将 CH4 路径、HER 竞争、位点稳定性及验证数据分列，输出推荐、淘汰和待验证候选，不把单一描述符当作充分证据。

## 本实例输入槽
- {REACTION_ANALYSIS} | required=True | type=doc | var_name=反应分析结果 | hint=s03 输出。 | default={REACTION_ANALYSIS}
- {VALIDATION_DATA} | required=False | type=doc | var_name=验证数据 | hint=实验性能和局域配位表征。 | default={VALIDATION_DATA}

## 本实例产出
- Cu-NxBy 候选排序
- CH4 选择性设计规则
- 需实验验证的优先候选

## 本实例质量门禁
- 排序依据可回溯到原始吸附/自由能/能垒数据
- 推荐位点的结构与配位环境明确
- 计算预测和实验观察分开报告

## 可调资源（edge:resource，仅真实存在）
- datapipes/xps-nife-oer-surface-analysis

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
