# 实例任务：预测IOD指数和发展阶段 @ E78

- domain: climate
- 骨架: tk-climate-7418aff8
- 场景: sc-62dab04b (E78)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E78
- 关联论文: Multi-task machine learning improves multi-seasonal prediction of the Indian Ocean Dipole | doi:

## 本实例步骤描述
按冻结配置执行“预测IOD指数和发展阶段”，完成从印度洋—太平洋海温、热含量和风场到IOD指数轨迹、正负事件类别和概率的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{OUTPUT_INTERVAL}、{ENSEMBLE_SIZE}执行预测IOD指数和发展阶段，将印度洋—太平洋海温、热含量和风场转换为IOD指数轨迹、正负事件类别和概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 预测IOD指数和发展阶段结果
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
