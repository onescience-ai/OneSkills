# 骨架任务：验证与输出

- domain: matchem
- 复用场景数: 4
- 实例任务数: 4

## 步骤描述（跨场景聚合去重）
- 提出可操作的制备或表征验证路线。

## 执行 prompt（跨场景聚合去重）
- 输出优先缺陷方案、验证表征和 PASS/REJECT/BLOCKED 结论。

## 输入槽（var/hint/default）
- （源场景未提供）

## 产出
- 最终结论
- 验证计划

## 质量门禁 quality_gate
- 推荐具备可追溯原始证据
- 未验证项单列

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-verification-output-hbn-single-photon-emission-inst
- matchem-verification-output-lithium-reduction-room-inst
- matchem-verification-output-mos2-monolayer-atomic-inst
- matchem-verification-output-phosphorene-monolayer-inst

## 复用场景
- MoS2单层原子缺陷工程
- hBN单光子发射原子缺陷设计
- 磷烯单层缺陷工程与空气稳定化
- 锂还原室温氧化物缺陷调控
