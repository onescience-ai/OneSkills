# 实例任务：联合生成多时效功率 @ E25

- domain: climate
- 骨架: tk-climate-34e740d0
- 场景: sc-1e3c4752 (E25)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E25
- 关联论文: Spatio-Temporal Graph Neural Networks for Multi-Site PV Power Forecasting | doi:; Photovoltaic yield prediction using an irradiance forecast model based on multiple neural networks | doi:; Short-Term Power Generation Forecasting of a Photovoltaic Plant Based on PSO-BP and GA-BP Neural Networks | doi:; Solar PV power forecasting at Yarmouk University using machine learning techniques | doi:

## 本实例步骤描述
按冻结配置执行“联合生成多时效功率”，完成从多站历史功率、天气预报、电站容量属性到逐站多时效光伏功率的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{QUANTILES}、{OUTPUT_INTERVAL}执行联合生成多时效功率，将多站历史功率、天气预报、电站容量属性转换为逐站多时效光伏功率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {QUANTILES} | required=False | type=str | var_name=概率分位数 | hint=输入概率分位数清单。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None

## 本实例产出
- 联合生成多时效功率结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 功率、负荷或辐照度输出满足物理边界

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
