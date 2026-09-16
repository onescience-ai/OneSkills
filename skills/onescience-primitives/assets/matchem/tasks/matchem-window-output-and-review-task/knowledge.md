# 骨架任务：窗口输出与复核

- domain: matchem
- 复用场景数: 5
- 实例任务数: 5

## 步骤描述（跨场景聚合去重）
- 输出可执行材料/工艺窗口和验证计划。

## 执行 prompt（跨场景聚合去重）
- 给出推荐窗口、限制条件和 PASS/REJECT/BLOCKED；未完成独立复核时明确写出。

## 输入槽（var/hint/default）
- （源场景未提供）

## 产出
- 推荐窗口
- 最终结论
- 验证计划

## 质量门禁 quality_gate
- 安全和可制造性限制明确
- 结论可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-window-output-and-review-complex-alloy-thermal-inst
- matchem-window-output-and-review-crconi-medium-high-entropy-inst
- matchem-window-output-and-review-high-entropy-metallic-glass-inst
- matchem-window-output-and-review-laser-powder-bed-fusion-inst
- matchem-window-output-and-review-refractory-high-entropy-inst

## 复用场景
- CrCoNi中高熵合金低温断裂韧性分析
- 复杂合金热稳定纳米颗粒扩散调控
- 激光粉末床熔融钥孔波动与孔隙形成分析
- 难熔高熵合金位错迁移与短程有序分析
- 高熵金属玻璃纳米颗粒电合成与电催化设计
