# 实例任务：生成格点次日大火概率和风险等级 @ E37

- domain: climate
- 骨架: tk-climate-8111eb84
- 场景: sc-bec83fee (E37)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E37
- 关联论文: Wildfire Danger Prediction and Understanding With Deep Learning | doi:; Evaluation of machine learning and deep learning algorithms for fire prediction in Southeast Asia | doi:; Predicting Forest Fire Using Remote Sensing Data And Machine Learning | doi:

## 本实例步骤描述
按冻结配置执行“生成格点次日大火概率和风险等级”，完成从近期天气、土壤、植被、地形和人类活动特征到次日大火概率及危险等级图的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{WARNING_THRESHOLDS}、{UNCERTAINTY_CONFIG}执行生成格点次日大火概率和风险等级，将近期天气、土壤、植被、地形和人类活动特征转换为次日大火概率及危险等级图。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {WARNING_THRESHOLDS} | required=True | type=str | var_name=预警阈值 | hint=输入分级预警阈值。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 本实例产出
- 生成格点次日大火概率和风险等级结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 预警阈值在独立验证集上冻结后评估

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
