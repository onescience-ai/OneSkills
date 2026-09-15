# 实例任务：生成多时效沙尘发生、强度和影响区 @ E92

- domain: climate
- 骨架: tk-climate-255dbcd3
- 场景: sc-6152ecb0 (E92)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E92
- 关联论文: Deep multi-task learning for early warnings of dust events implemented for the Middle East | doi:

## 本实例步骤描述
按冻结配置执行“生成多时效沙尘发生、强度和影响区”，完成从气象预报、气溶胶观测、地表与沙尘历史到沙尘概率、浓度等级和影响区的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{LEAD_TIMES}、{WARNING_THRESHOLDS}执行生成多时效沙尘发生、强度和影响区，将气象预报、气溶胶观测、地表与沙尘历史转换为沙尘概率、浓度等级和影响区。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=沙尘预警配置 | hint=输入沙尘预警配置。 | default=None
- {LEAD_TIMES} | required=True | type=str | var_name=目标提前期 | hint=输入目标提前期清单。 | default=None
- {WARNING_THRESHOLDS} | required=True | type=str | var_name=沙尘预警阈值 | hint=输入沙尘预警阈值。 | default=None

## 本实例产出
- 生成多时效沙尘发生、强度和影响区结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 预警阈值在独立验证集上冻结后评估
- 每个提前期均输出沙尘发生、强度和影响区域

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
