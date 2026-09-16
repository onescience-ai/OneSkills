# 骨架任务：结构或电化学响应获取

- domain: matchem
- 复用场景数: 15
- 实例任务数: 15

## 步骤描述（跨场景聚合去重）
- 执行统一的计算、表征或循环测试。

## 执行 prompt（跨场景聚合去重）
- 按 {COMPUTE_OR_TEST_CONFIG} 获取结构演化、容量、阻抗或失效数据，记录版本、命令或仪器校准。

## 输入槽（var/hint/default）
- {COMPUTE_OR_TEST_CONFIG} | required=False | type=object | var_name=计算或测试配置 | hint=说明软件、仪器、收敛或校准信息。 | default={'mode': 'experiment_or_user_confirmed_simulation'}

## 产出
- 原始响应数据
- 实验/计算日志

## 质量门禁 quality_gate
- 原始数据可追溯
- 对照样采用同一工况

## 可调资源（edge:resource，仅真实存在）
- datasets/xjtu-sy-rolling-bearing-accelerated-life-test-protocol-and-dataset

## 实例任务（本骨架在各场景的实例化）
- matchem-structure-or-electrochemical-battery-particle-carbon-inst
- matchem-structure-or-electrochemical-commercial-li-ion-battery-inst
- matchem-structure-or-electrochemical-high-ionic-conductivity-inst
- matchem-structure-or-electrochemical-ionomer-electrolyte-machine-inst
- matchem-structure-or-electrochemical-li-rich-layered-cathode-inst
- matchem-structure-or-electrochemical-licoo2-high-voltage-timgal-inst
- matchem-structure-or-electrochemical-limn-li-rich-layered-cathode-inst
- matchem-structure-or-electrochemical-lithium-ion-battery-calendar-inst
- matchem-structure-or-electrochemical-lithium-ion-battery-degradat-inst
- matchem-structure-or-electrochemical-lithium-ion-battery-electrod-inst
- matchem-structure-or-electrochemical-lithium-metal-electrolyte-inst
- matchem-structure-or-electrochemical-lithium-sulfur-battery-inst
- matchem-structure-or-electrochemical-porous-silicon-li-ion-inst
- matchem-structure-or-electrochemical-solid-state-battery-lithium-inst
- matchem-structure-or-electrochemical-solid-state-lithium-ion-inst

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
