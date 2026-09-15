# 实例任务：滚动生成多周病例预测 @ E43

- domain: climate
- 骨架: tk-climate-c7767bf7
- 场景: sc-7d1fa1a7 (E43)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E43
- 关联论文: Deep learning models for forecasting dengue fever based on climate data in Vietnam | doi:; Machine learning and dengue forecasting- Comparing random forests and artificial neural networks for predicting dengue burden at national and sub-national scales in Colombia | doi:; Machine learning methods reveal the temporal pattern of dengue incidence using meteorological factors in metropolitan Manila, Philippines | doi:

## 本实例步骤描述
按冻结配置执行“滚动生成多周病例预测”，完成从气象历史与预报、病例序列、季节人口信息到周病例数、风险等级与概率的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{SCENARIO_CONDITIONS}、{UNCERTAINTY_CONFIG}执行滚动生成多周病例预测，将气象历史与预报、病例序列、季节人口信息转换为周病例数、风险等级与概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {SCENARIO_CONDITIONS} | required=False | type=str | var_name=情景条件 | hint=输入目标情景条件。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 本实例产出
- 滚动生成多周病例预测结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 预测关系与因果归因声明严格区分

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
