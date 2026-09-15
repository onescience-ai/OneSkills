# 实例任务：输出各10分钟窗发生概率 @ E52

- domain: climate
- 骨架: tk-climate-14b7635f
- 场景: sc-acdba65e (E52)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E52
- 关联论文: Nowcasting lightning occurrence from commonly available meteorological parameters using machine learning techniques | doi:; Horizontal grid spacing comparison among Random Forest algorithms to nowcast Cloud-to-Ground lightning occurrence | doi:

## 本实例步骤描述
按冻结配置执行“输出各10分钟窗发生概率”，完成从近期地面气象观测、站点位置、历史雷电标签到分时间窗雷电发生概率和告警的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{EVENT_THRESHOLDS}、{ENSEMBLE_SIZE}执行输出各10分钟窗发生概率，将近期地面气象观测、站点位置、历史雷电标签转换为分时间窗雷电发生概率和告警。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {EVENT_THRESHOLDS} | required=True | type=str | var_name=事件阈值 | hint=输入事件判定阈值。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 输出各10分钟窗发生概率结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 每个目标提前量均生成且未使用未来观测

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
