# 实例任务：生成未解析尺度残差集合 @ E55

- domain: climate
- 骨架: tk-climate-c6dea4bd
- 场景: sc-b1822141 (E55)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E55
- 关联论文: Residual Corrective Diffusion Modeling for Km-scale Atmospheric Downscaling | doi:; A deep learning approach for improving spatiotemporal resolution of numerical weather prediction forecasts | doi:

## 本实例步骤描述
按冻结配置执行“生成未解析尺度残差集合”，完成从粗网格大气状态、地形与静态地理量到公里尺度多变量确定性场或集合细场的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{ENSEMBLE_SIZE}、{OUTPUT_INTERVAL}执行生成未解析尺度残差集合，将粗网格大气状态、地形与静态地理量转换为公里尺度多变量确定性场或集合细场。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=生成成员数 | hint=输入生成成员数量。 | default=20
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None

## 本实例产出
- 生成未解析尺度残差集合结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 输出均值、极端尾部和空间频谱均可检查
- 多变量和垂直层输出保持跨变量物理协调

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
