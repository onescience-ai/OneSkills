# 骨架任务：缺陷功能与稳定性排序

- domain: matchem
- 复用场景数: 4
- 实例任务数: 4

## 步骤描述（跨场景聚合去重）
- 比较目标功能、副作用和环境稳定性。

## 执行 prompt（跨场景聚合去重）
- 对缺陷候选排序，区分热力学可行性、动力学可达性和实验可制备性。

## 输入槽（var/hint/default）
- {ENVIRONMENT} | required=False | type=object | var_name=环境与表征条件 | hint=温度、气氛、电位、光照、应力或表征方案。 | default={'temperature_K': 298}

## 产出
- 候选排序
- 风险与证据缺口

## 质量门禁 quality_gate
- 不将形成能直接等同于实际浓度
- 适用域明确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-defect-functionality-and-hbn-single-photon-emission-inst
- matchem-defect-functionality-and-lithium-reduction-room-inst
- matchem-defect-functionality-and-mos2-monolayer-atomic-inst
- matchem-defect-functionality-and-phosphorene-monolayer-inst

## 复用场景
- MoS2单层原子缺陷工程
- hBN单光子发射原子缺陷设计
- 磷烯单层缺陷工程与空气稳定化
- 锂还原室温氧化物缺陷调控
