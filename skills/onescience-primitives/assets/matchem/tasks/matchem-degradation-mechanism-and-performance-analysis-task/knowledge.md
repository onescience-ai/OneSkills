# 骨架任务：退化机制与性能指标分析

- domain: matchem
- 复用场景数: 15
- 实例任务数: 15

## 步骤描述（跨场景聚合去重）
- 量化相变、应变、界面、锂沉积或容量变化。

## 执行 prompt（跨场景聚合去重）
- 依据 {CELL_CONDITION} 计算性能指标并建立结构-性能关联，区分相关性和机制证据。

## 输入槽（var/hint/default）
- {CELL_CONDITION} | required=True | type=object | var_name=电池工况 | hint=电压窗口、倍率、温度、负载量和循环数。 | default={'voltage_window_V': [2.8, 4.5], 'temperature_C': 25}

## 产出
- 性能指标表
- 机制证据链

## 质量门禁 quality_gate
- 不得将单次循环外推为寿命
- 不确定性和异常样本保留

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-degradation-mechanism-and-battery-particle-carbon-inst
- matchem-degradation-mechanism-and-commercial-li-ion-battery-inst
- matchem-degradation-mechanism-and-high-ionic-conductivity-inst
- matchem-degradation-mechanism-and-ionomer-electrolyte-machine-inst
- matchem-degradation-mechanism-and-li-rich-layered-cathode-inst
- matchem-degradation-mechanism-and-licoo2-high-voltage-timgal-inst
- matchem-degradation-mechanism-and-limn-li-rich-layered-cathode-inst
- matchem-degradation-mechanism-and-lithium-ion-battery-calendar-inst
- matchem-degradation-mechanism-and-lithium-ion-battery-degradat-inst
- matchem-degradation-mechanism-and-lithium-ion-battery-electrod-inst
- matchem-degradation-mechanism-and-lithium-metal-electrolyte-inst
- matchem-degradation-mechanism-and-lithium-sulfur-battery-inst
- matchem-degradation-mechanism-and-porous-silicon-li-ion-inst
- matchem-degradation-mechanism-and-solid-state-battery-lithium-inst
- matchem-degradation-mechanism-and-solid-state-lithium-ion-inst

## 复用场景
- LiCoO2高电压TiMgAl协同掺杂优化
- LiMn富锂层状正极电流密度退化分析
- 商用锂离子电池电压松弛容量估计
- 固态电池锂沉积原位CT机器学习检测
- 固态锂离子导体无监督发现
- 多孔硅锂离子电池负极结构设计
- 富锂层状正极结构退化与氧释放分析
- 电池颗粒碳粘结剂脱粘机器学习统计
- 离子聚合物电解质机器学习配方发现
- 锂硫电池多硫化物吸附扩散协同设计
- 锂离子电池日历老化预测
- 锂离子电池电极微结构深度学习分割
- 锂离子电池衰减参数物理数据融合反演
- 锂金属电解液界面枝晶恒电势模拟
- 高离子电导电解液基础模型配方设计
