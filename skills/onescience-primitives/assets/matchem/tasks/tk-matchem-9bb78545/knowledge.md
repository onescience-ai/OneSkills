# 骨架任务：验证候选势能模型可用性

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 基于已确认的训练、验证和测试数据，提出候选势能模型训练或复用方案并完成独立验证。

## 执行 prompt（跨场景聚合去重）
- 基于 {TRAINING_DATA} 和 {CANDIDATE_POTENTIAL}，说明训练或复用判断、独立测试、最差构型和适用范围。

## 输入槽（var/hint/default）
- {TRAINING_DATA} | required=True | type=doc | var_name=训练验证数据 | hint=含能量力和数据来源 | default=
- {CANDIDATE_POTENTIAL} | required=False | type=doc | var_name=候选势能模型 | hint=提供版本和训练信息 | default=

## 产出
- MD 准入结论
- 模型验证报告
- 独立测试指标

## 质量门禁 quality_gate
- 数据划分可追溯
- 独立测试已完成
- 适用范围已说明

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-ec230ad5

## 复用场景
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
