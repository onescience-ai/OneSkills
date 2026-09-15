# 实例任务：滚动预测多时效风速场 @ E95

- domain: climate
- 骨架: tk-climate-bc1a36a1
- 场景: sc-ff3a2b7c (E95)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E95
- 关联论文: Adapting a deep convolutional RNN model with imbalanced regression loss for improved spatio-temporal forecasting of extreme wind speed events in the short to medium range | doi:

## 本实例步骤描述
按冻结配置执行“滚动预测多时效风速场”，完成从历史区域风场、环境气象场、强风事件标签到多时效风速格点和超阈概率的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{OUTPUT_INTERVAL}、{ENSEMBLE_SIZE}执行滚动预测多时效风速场，将历史区域风场、环境气象场、强风事件标签转换为多时效风速格点和超阈概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 滚动预测多时效风速场结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 滚动过程中未读取起报时间之后的观测或分析资料

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
