# 实例任务：验证候选势能模型可用性 @ CO2_Cu111_12C13C_MACE_LAMMPS动力学验证

- domain: matchem
- 骨架: tk-matchem-9bb78545
- 场景: sc-a5425d92 (CO2_Cu111_12C13C_MACE_LAMMPS动力学验证)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
- 关联论文: （源场景未提供）

## 本实例步骤描述
基于已确认的训练、验证和测试数据，提出候选势能模型训练或复用方案并完成独立验证。

## 本实例执行 prompt
基于 {TRAINING_DATA} 和 {CANDIDATE_POTENTIAL}，说明训练或复用判断、独立测试、最差构型和适用范围。

## 本实例输入槽
- {TRAINING_DATA} | required=True | type=doc | var_name=训练验证数据 | hint=含能量力和数据来源 | default=
- {CANDIDATE_POTENTIAL} | required=False | type=doc | var_name=候选势能模型 | hint=提供版本和训练信息 | default=

## 本实例产出
- 模型验证报告
- 独立测试指标
- MD 准入结论

## 本实例质量门禁
- 数据划分可追溯
- 独立测试已完成
- 适用范围已说明

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
