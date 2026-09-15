# 实例任务：评测与解释汇总 @ B33

- domain: bio
- 骨架: tk-bio-0dc2d6a7
- 场景: sc-2f2a837d (B33)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B33
- 关联论文: EnzyCLIP: A Cross-Attention Dual Encoder Framework with Contrastive Learning for Predicting Enzyme Kinetic Constants | doi:; HERMES: Holographic Equivariant neuRal network model for Mutational Effect and Stability prediction | doi:

## 本实例步骤描述
计算R方并输出残基、结构域或样本层解释。

## 本实例执行 prompt
计算R方并与{MIN_METRIC}比较，按{EXPORT_EXPLANATION}导出特征贡献和错误分析。

## 本实例输入槽
- {MIN_METRIC} | required=False | type=float | var_name=指标下限 | hint=设置合格指标下限 | default=0.6
- {EXPORT_EXPLANATION} | required=False | type=bool | var_name=导出解释 | hint=是否输出模型解释 | default=True

## 本实例产出
- 评测汇总
- R方明细
- 解释与误差报告

## 本实例质量门禁
- 数据切分无泄漏
- 指标定义明确
- 解释可定位到原始样本

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
