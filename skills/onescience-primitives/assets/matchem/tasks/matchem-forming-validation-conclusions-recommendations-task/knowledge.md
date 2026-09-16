# 骨架任务：形成验证结论与后续建议

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 汇总模型与短时动力学证据，判定是否具备进入长时采样的条件，并说明当前结论边界。

## 执行 prompt（跨场景聚合去重）
- 基于短时验证结果，判定是否可进入 {LONG_RUN_GOAL}；区分已证实、待确认和不可回答事项。

## 输入槽（var/hint/default）
- {LONG_RUN_GOAL} | required=False | type=str | var_name=长时目标 | hint=未确认时留空 | default=

## 产出
- 后续采样建议
- 风险与限制说明
- 验收判定

## 质量门禁 quality_gate
- 后续范围需用户确认
- 短时结果未被过度解释
- 结论与证据一致

## 可调资源（edge:resource，仅真实存在）
- tools/reaxnet-polarizable-long-range-neural-network-potential

## 实例任务（本骨架在各场景的实例化）
- matchem-forming-validation-conclusions-co2-cu111-water-k-interface-inst

## 复用场景
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
