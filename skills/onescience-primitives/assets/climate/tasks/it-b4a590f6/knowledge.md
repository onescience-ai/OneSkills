# 实例任务：生成多月入流预测 @ E65

- domain: climate
- 骨架: tk-climate-da128859
- 场景: sc-edddeefe (E65)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E65
- 关联论文: Developing reservoir monthly inflow forecasts using artificial intelligence and climate phenomenon information | doi:; Climate-informed monthly runoff prediction model using machine learning and feature importance analysis | doi:

## 本实例步骤描述
按冻结配置执行“生成多月入流预测”，完成从月入流、气象历史、气候模态指数到未来数月入库流量及区间的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{INITIAL_STATE}、{ENSEMBLE_SIZE}执行生成多月入流预测，将月入流、气象历史、气候模态指数转换为未来数月入库流量及区间。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {INITIAL_STATE} | required=False | type=str | var_name=初始水文状态 | hint=输入初始水文状态路径。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 生成多月入流预测结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 水量、状态范围和洪峰时序不存在非物理异常

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
