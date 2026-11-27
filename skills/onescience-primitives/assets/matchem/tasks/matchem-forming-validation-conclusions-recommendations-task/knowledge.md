# 骨架任务：形成验证结论与后续建议

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 汇总结构、模型和两套动力学证据，逐项签收并归档。

## 执行 prompt（跨场景聚合去重）
- 逐项标注 PASS、PARTIAL、REJECT 或 BLOCKED 并附归档证据。记录上游失败位置、影响及最后健康产物，按证据判定是否具备进入 {LONG_RUN_GOAL} 的条件。

## 输入槽（var/hint/default）
- {LONG_RUN_GOAL} | required=False | type=str | var_name=长时目标 | hint=未确认时留空 | default=

## 产出
- 后续采样建议
- 风险与限制说明
- 验收判定
- 复现归档及文件校验清单

## 质量门禁 quality_gate
- 后续范围需用户确认
- 短时结果未被过度解释
- 结论与证据一致

## 可调资源（edge:resource，仅真实存在）
- 使用上游结构、模型和短测任务的交接证据。

## 实例任务（本骨架在各场景的实例化）
- matchem-forming-validation-conclusions-co2-cu111-water-k-interface-inst

## 复用场景
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
