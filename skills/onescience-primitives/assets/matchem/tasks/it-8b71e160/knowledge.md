# 实例任务：形成验证结论与后续建议 @ CO2_Cu111_12C13C_MACE_LAMMPS动力学验证

- domain: matchem
- 骨架: tk-matchem-a99d7422
- 场景: sc-a5425d92 (CO2_Cu111_12C13C_MACE_LAMMPS动力学验证)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
- 关联论文: （源场景未提供）

## 本实例步骤描述
汇总模型与短时动力学证据，判定是否具备进入长时采样的条件，并说明当前结论边界。

## 本实例执行 prompt
基于短时验证结果，判定是否可进入 {LONG_RUN_GOAL}；区分已证实、待确认和不可回答事项。

## 本实例输入槽
- {LONG_RUN_GOAL} | required=False | type=str | var_name=长时目标 | hint=未确认时留空 | default=

## 本实例产出
- 验收判定
- 风险与限制说明
- 后续采样建议

## 本实例质量门禁
- 结论与证据一致
- 短时结果未被过度解释
- 后续范围需用户确认

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
