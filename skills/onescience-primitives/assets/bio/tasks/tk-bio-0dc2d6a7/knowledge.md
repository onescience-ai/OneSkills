# 骨架任务：评测与解释汇总

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 计算RMSE并输出残基、结构域或样本层解释。
- 计算R方并输出残基、结构域或样本层解释。
- 计算Spearman相关并输出残基、结构域或样本层解释。
- 计算宏平均F1并输出残基、结构域或样本层解释。
- 计算效应相关性并输出残基、结构域或样本层解释。
- 计算检索召回率并输出残基、结构域或样本层解释。

## 执行 prompt（跨场景聚合去重）
- 计算RMSE并与{MIN_METRIC}比较，按{EXPORT_EXPLANATION}导出特征贡献和错误分析。
- 计算R方并与{MIN_METRIC}比较，按{EXPORT_EXPLANATION}导出特征贡献和错误分析。
- 计算Spearman相关并与{MIN_METRIC}比较，按{EXPORT_EXPLANATION}导出特征贡献和错误分析。
- 计算宏平均F1并与{MIN_METRIC}比较，按{EXPORT_EXPLANATION}导出特征贡献和错误分析。
- 计算效应相关性并与{MIN_METRIC}比较，按{EXPORT_EXPLANATION}导出特征贡献和错误分析。
- 计算检索召回率并与{MIN_METRIC}比较，按{EXPORT_EXPLANATION}导出特征贡献和错误分析。

## 输入槽（var/hint/default）
- {MIN_METRIC} | required=False | type=float | var_name=指标下限 | hint=设置合格指标下限 | default=0.6
- {EXPORT_EXPLANATION} | required=False | type=bool | var_name=导出解释 | hint=是否输出模型解释 | default=True

## 产出
- RMSE明细
- R方明细
- Spearman相关明细
- 宏平均F1明细
- 效应相关性明细
- 检索召回率明细
- 解释与误差报告
- 评测汇总

## 质量门禁 quality_gate
- 指标定义明确
- 数据切分无泄漏
- 解释可定位到原始样本

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-47a3479c
- it-4e8a349b
- it-5ea81487
- it-61ed64ee
- it-634e3379
- it-aaaac170
- it-b3f8afc3
- it-cf0e618c
- it-ec654490
- it-ed856c21

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
