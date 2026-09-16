# 实例任务：退化机制与性能指标分析 @ 电池颗粒碳粘结剂脱粘机器学习统计

- domain: matchem
- 骨架: matchem-degradation-mechanism-and-performance-analysis-task
- 场景: matchem-battery-particle-carbon-binder-debonding-ml-statistics-scenario (电池颗粒碳粘结剂脱粘机器学习统计)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- 电池颗粒碳粘结剂脱粘机器学习统计
- 关联论文: Machine-learning-revealed statistics of the particle-carbon/binder detachment in lithium-ion battery cathodes | doi:

## 本实例步骤描述
量化相变、应变、界面、锂沉积或容量变化。

## 本实例执行 prompt
依据 {CELL_CONDITION} 计算性能指标并建立结构-性能关联，区分相关性和机制证据。

## 本实例输入槽
- {CELL_CONDITION} | required=True | type=object | var_name=电池工况 | hint=电压窗口、倍率、温度、负载量和循环数。 | default={'voltage_window_V': [2.8, 4.5], 'temperature_C': 25}

## 本实例产出
- 性能指标表
- 机制证据链

## 本实例质量门禁
- 不得将单次循环外推为寿命
- 不确定性和异常样本保留

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
