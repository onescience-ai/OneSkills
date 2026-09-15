# 实例任务：重建三维温盐场并融合多尺度背景信息 @ E48

- domain: climate
- 骨架: tk-climate-0ab59d34
- 场景: sc-8d796207 (E48)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E48
- 关联论文: Rapid reconstruction of temperature and salinity fields based on machine learning and the assimilation application | doi:; Super-resolution data assimilation | doi:

## 本实例步骤描述
按冻结配置执行“重建三维温盐场并融合多尺度背景信息”，完成从稀疏温盐剖面、卫星表层观测和背景场到规则网格三维温盐分析场的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{CYCLE_CONFIG}、{FORECAST_HORIZON}、{CHECKPOINT_INTERVAL}执行重建三维温盐场并融合多尺度背景信息，将稀疏温盐剖面、卫星表层观测和背景场转换为规则网格三维温盐分析场。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {CYCLE_CONFIG} | required=True | type=str | var_name=循环配置 | hint=输入分析循环配置。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=验证预报时效 | hint=输入验证预报时效。 | default=None
- {CHECKPOINT_INTERVAL} | required=True | type=str | var_name=中间保存间隔 | hint=输入中间状态保存间隔。 | default=None

## 本实例产出
- 重建三维温盐场并融合多尺度背景信息结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 分析增量和循环状态不存在未解释的突变

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
