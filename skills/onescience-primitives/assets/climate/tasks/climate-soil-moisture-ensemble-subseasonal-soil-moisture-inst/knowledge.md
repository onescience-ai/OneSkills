# 实例任务：生成土壤湿度集合 @ E46

- domain: climate
- 骨架: climate-soil-moisture-ensemble-task
- 场景: climate-subseasonal-soil-moisture-drought-probability-forecast-scenario (E46)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E46
- 关联论文: Skillful subseasonal soil moisture drought forecasts with deep learning-dynamic models | doi:; A comprehensive study of deep learning for soil moisture prediction | doi:

## 本实例步骤描述
按冻结配置执行“生成土壤湿度集合”，完成从初始土壤湿度、气象预报、陆面属性到土壤湿度异常、分位数与干旱概率的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{INITIAL_STATE}、{ENSEMBLE_SIZE}执行生成土壤湿度集合，将初始土壤湿度、气象预报、陆面属性转换为土壤湿度异常、分位数与干旱概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {INITIAL_STATE} | required=False | type=str | var_name=初始水文状态 | hint=输入初始水文状态路径。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=20

## 本实例产出
- 生成土壤湿度集合结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 水量、状态范围和洪峰时序不存在非物理异常

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/large-ensemble-testbed
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
