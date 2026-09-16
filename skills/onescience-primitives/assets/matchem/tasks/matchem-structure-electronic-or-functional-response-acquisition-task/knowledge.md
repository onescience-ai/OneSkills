# 骨架任务：结构电子或功能响应获取

- domain: matchem
- 复用场景数: 4
- 实例任务数: 4

## 步骤描述（跨场景聚合去重）
- 计算或测量缺陷形成、迁移、光学或催化响应。

## 执行 prompt（跨场景聚合去重）
- 在 {ENVIRONMENT} 下获取响应数据，保留软件/仪器、参数和原始文件。

## 输入槽（var/hint/default）
- {ENVIRONMENT} | required=False | type=object | var_name=环境与表征条件 | hint=温度、气氛、电位、光照、应力或表征方案。 | default={'temperature_K': 298}

## 产出
- 原始响应数据
- 缺陷特征

## 质量门禁 quality_gate
- 参考态和校正项记录
- 对照样齐全

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-structure-electronic-or-hbn-single-photon-emission-inst
- matchem-structure-electronic-or-lithium-reduction-room-inst
- matchem-structure-electronic-or-mos2-monolayer-atomic-inst
- matchem-structure-electronic-or-phosphorene-monolayer-inst

## 复用场景
- MoS2单层原子缺陷工程
- hBN单光子发射原子缺陷设计
- 磷烯单层缺陷工程与空气稳定化
- 锂还原室温氧化物缺陷调控
