# 骨架任务：材料与工况建模

- domain: matchem
- 复用场景数: 15
- 实例任务数: 15

## 步骤描述（跨场景聚合去重）
- 核对材料组成、初始状态和电池工况。

## 执行 prompt（跨场景聚合去重）
- 读取 {MATERIAL_STRUCTURE} 与 {CELL_CONDITION}；明确满锂/脱锂状态、对照样和失效判据。

## 输入槽（var/hint/default）
- {MATERIAL_STRUCTURE} | required=True | type=doc | var_name=电极或电解质材料信息 | hint=结构文件、组成、粒径或配方及来源。 | default=CIF/POSCAR/配方表
- {CELL_CONDITION} | required=True | type=object | var_name=电池工况 | hint=电压窗口、倍率、温度、负载量和循环数。 | default={'voltage_window_V': [2.8, 4.5], 'temperature_C': 25}

## 产出
- 初始状态记录
- 材料与工况清单

## 质量门禁 quality_gate
- 材料化学计量和电压参考明确
- 缺失电解液或对电极信息时标记 BLOCKED

## 可调资源（edge:resource，仅真实存在）
- tools/molecular-structure-preparation

## 实例任务（本骨架在各场景的实例化）
- matchem-material-condition-modeling-battery-particle-carbon-inst
- matchem-material-condition-modeling-commercial-li-ion-battery-inst
- matchem-material-condition-modeling-high-ionic-conductivity-inst
- matchem-material-condition-modeling-ionomer-electrolyte-machine-inst
- matchem-material-condition-modeling-li-rich-layered-cathode-inst
- matchem-material-condition-modeling-licoo2-high-voltage-timgal-inst
- matchem-material-condition-modeling-limn-li-rich-layered-cathode-inst
- matchem-material-condition-modeling-lithium-ion-battery-calendar-inst
- matchem-material-condition-modeling-lithium-ion-battery-degradat-inst
- matchem-material-condition-modeling-lithium-ion-battery-electrod-inst
- matchem-material-condition-modeling-lithium-metal-electrolyte-inst
- matchem-material-condition-modeling-lithium-sulfur-battery-inst
- matchem-material-condition-modeling-porous-silicon-li-ion-inst
- matchem-material-condition-modeling-solid-state-battery-lithium-inst
- matchem-material-condition-modeling-solid-state-lithium-ion-inst

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
