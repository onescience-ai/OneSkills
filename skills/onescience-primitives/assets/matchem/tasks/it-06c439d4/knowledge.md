# 实例任务：执行 2 ps 短时验证 @ CO2_Cu111_12C13C_MACE_LAMMPS动力学验证

- domain: matchem
- 骨架: tk-matchem-b34abd27
- 场景: sc-a5425d92 (CO2_Cu111_12C13C_MACE_LAMMPS动力学验证)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
- 关联论文: （源场景未提供）

## 本实例步骤描述
在模型和输入预检通过后，分别执行 C12/C13 的短时动力学，检查运行质量和续算能力。

## 本实例执行 prompt
在 {TEST_DURATION_PS} 的短时测试中，按经确认的温度和采样方案执行 C12/C13 动力学并报告有效采样、温度、能量、约束、轨迹和续算能力。

## 本实例输入槽
- {TEST_DURATION_PS} | required=True | type=float | var_name=短时测试时长 | hint=每种同位素 2 ps | default=2.0
- {TARGET_TEMPERATURE} | required=False | type=float | var_name=目标温度 | hint=由用户确认温度 | default=None

## 本实例产出
- C12 测试轨迹
- C13 测试轨迹
- 运行质量报告

## 本实例质量门禁
- 模型正常加载
- 约束持续有效
- 轨迹与续算材料可用
- 无未解释异常

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
