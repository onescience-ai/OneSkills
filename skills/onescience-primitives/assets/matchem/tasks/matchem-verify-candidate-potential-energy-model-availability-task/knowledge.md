# 骨架任务：验证候选势能模型可用性

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 核验或补充 DFT 参考标签，按来源分组划分数据，独立验证复用或新训练的 MACE 势。

## 执行 prompt（跨场景聚合去重）
- 核验 {TRAINING_DATA} 的来源、单位与完整性，必要时在已确认的范围及预算内补充 DFT/AIMD。按来源轨迹或构型族划分数据，基于独立能量误差、分元素力误差、最差构型和界面覆盖判定 {CANDIDATE_POTENTIAL} 或新训练 MACE 势的准入。

## 输入槽（var/hint/default）
- {TRAINING_DATA} | required=False | type=doc | var_name=训练验证数据 | hint=已有 DFT 能量、原子力和来源，正式数据也可在授权范围内补充 | default=
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
- models/data-efficient-machine-learning-potentials-modeling-catalytic
- tools/reaxnet-polarizable-long-range-neural-network-potential

## 实例任务（本骨架在各场景的实例化）
- matchem-verify-candidate-potential-co2-cu111-water-k-interface-inst

## 复用场景
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
