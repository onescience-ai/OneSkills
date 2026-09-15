# 骨架任务：滚动预测干旱指数

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“滚动预测干旱指数”，完成从历史气象序列、气候因子到SPI等干旱指数、等级与发生概率的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{INITIAL_STATE}、{ENSEMBLE_SIZE}执行滚动预测干旱指数，将历史气象序列、气候因子转换为SPI等干旱指数、等级与发生概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {INITIAL_STATE} | required=False | type=str | var_name=初始水文状态 | hint=输入初始水文状态路径。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 产出
- 中间状态与运行日志
- 滚动预测干旱指数结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 水量、状态范围和洪峰时序不存在非物理异常
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-e01ac85c

## 复用场景
- E18
