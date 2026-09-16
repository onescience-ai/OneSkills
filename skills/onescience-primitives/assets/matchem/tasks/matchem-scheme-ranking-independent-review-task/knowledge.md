# 骨架任务：方案排序与独立复核

- domain: matchem
- 复用场景数: 15
- 实例任务数: 15

## 步骤描述（跨场景聚合去重）
- 输出可执行的材料或工况改进建议。

## 执行 prompt（跨场景聚合去重）
- 根据性能、稳定性和安全约束排序候选；没有独立复核时写明待验证。

## 输入槽（var/hint/default）
- （源场景未提供）

## 产出
- PASS/REJECT/BLOCKED 结论
- 推荐方案
- 验证计划

## 质量门禁 quality_gate
- 实验验证与计算预测分开报告
- 推荐依据可回溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-scheme-ranking-independent-battery-particle-carbon-inst
- matchem-scheme-ranking-independent-commercial-li-ion-battery-inst
- matchem-scheme-ranking-independent-high-ionic-conductivity-inst
- matchem-scheme-ranking-independent-ionomer-electrolyte-machine-inst
- matchem-scheme-ranking-independent-li-rich-layered-cathode-inst
- matchem-scheme-ranking-independent-licoo2-high-voltage-timgal-inst
- matchem-scheme-ranking-independent-limn-li-rich-layered-cathode-inst
- matchem-scheme-ranking-independent-lithium-ion-battery-calendar-inst
- matchem-scheme-ranking-independent-lithium-ion-battery-degradat-inst
- matchem-scheme-ranking-independent-lithium-ion-battery-electrod-inst
- matchem-scheme-ranking-independent-lithium-metal-electrolyte-inst
- matchem-scheme-ranking-independent-lithium-sulfur-battery-inst
- matchem-scheme-ranking-independent-porous-silicon-li-ion-inst
- matchem-scheme-ranking-independent-solid-state-battery-lithium-inst
- matchem-scheme-ranking-independent-solid-state-lithium-ion-inst

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
