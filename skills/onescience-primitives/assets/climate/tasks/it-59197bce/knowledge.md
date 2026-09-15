# 实例任务：投影得到指数和位相振幅 @ E19

- domain: climate
- 骨架: tk-climate-609ba397
- 场景: sc-69cdbd58 (E19)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E19
- 关联论文: A modified transformer model for the extended-range forecast of intraseasonal oscillation | doi:; Deep learning for bias correction of MJO prediction | doi:; On the importance of historical context and bias correction in deep learning MJO prediction models | doi:; Deep learning reveals moisture as the primary predictability source of MJO | doi:

## 本实例步骤描述
按冻结配置执行“投影得到指数和位相振幅”，完成从热带风场、温度和对流异常历史到MJO或ISO指数、位相振幅及空间异常的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{OUTPUT_INTERVAL}、{ENSEMBLE_SIZE}执行投影得到指数和位相振幅，将热带风场、温度和对流异常历史转换为MJO或ISO指数、位相振幅及空间异常。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 投影得到指数和位相振幅结果
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
