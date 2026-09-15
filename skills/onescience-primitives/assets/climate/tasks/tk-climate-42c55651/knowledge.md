# 骨架任务：联合预测能见度和雾概率

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“联合预测能见度和雾概率”，完成从机场温湿风、能见度历史、NWP或CAMS预报到雾概率、能见度值与等级的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{EVENT_THRESHOLDS}、{ENSEMBLE_SIZE}执行联合预测能见度和雾概率，将机场温湿风、能见度历史、NWP或CAMS预报转换为雾概率、能见度值与等级。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {EVENT_THRESHOLDS} | required=True | type=str | var_name=事件阈值 | hint=输入事件判定阈值。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=20

## 产出
- 中间状态与运行日志
- 联合预测能见度和雾概率结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 每个目标提前量均生成且未使用未来观测
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-540eb726

## 复用场景
- E33
