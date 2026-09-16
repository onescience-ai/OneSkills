# 骨架任务：能量力应力与外推验证

- domain: matchem
- 复用场景数: 7
- 实例任务数: 7

## 步骤描述（跨场景聚合去重）
- 评估预测误差、外推和物理一致性。

## 执行 prompt（跨场景聚合去重）
- 在独立集上报告能量、力、应力误差和外推检测，不以训练误差代替泛化。

## 输入槽（var/hint/default）
- {REFERENCE_DATA} | required=True | type=doc | var_name=参考量子化学或第一性原理数据 | hint=结构、能量、力、应力、计算设置和数据许可 | default=extxyz/npz/数据库导出

## 产出
- 失败构型清单
- 验证报告

## 质量门禁 quality_gate
- 外推构型单独标记
- 独立集不参与调参

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-energy-force-stress-and-catalytic-reaction-ml-inst
- matchem-energy-force-stress-and-defective-potential-energy-inst
- matchem-energy-force-stress-and-hfo2-amorphous-liquid-ml-inst
- matchem-energy-force-stress-and-layered-material-transferabl-inst
- matchem-energy-force-stress-and-mof-quantum-ml-potential-inst
- matchem-energy-force-stress-and-neural-network-potential-inst
- matchem-energy-force-stress-and-polarizable-long-range-inst

## 复用场景
- HfO2非晶液相机器学习势主动学习
- MOF量子精度机器学习势温度主动学习
- 催化反应机器学习势主动学习与增强采样
- 可极化长程相互作用基础机器学习势
- 层状材料可迁移机器学习原子势验证
- 神经网络势长程静电自洽训练
- 缺陷势能面机器学习势探索
