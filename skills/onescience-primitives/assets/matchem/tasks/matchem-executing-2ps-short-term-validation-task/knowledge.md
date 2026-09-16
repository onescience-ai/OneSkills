# 骨架任务：执行 2 ps 短时验证

- domain: matchem
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 在模型和输入预检通过后，分别执行 C12/C13 的短时动力学，检查运行质量和续算能力。

## 执行 prompt（跨场景聚合去重）
- 在 {TEST_DURATION_PS} 的短时测试中，按经确认的温度和采样方案执行 C12/C13 动力学并报告有效采样、温度、能量、约束、轨迹和续算能力。

## 输入槽（var/hint/default）
- {TEST_DURATION_PS} | required=True | type=float | var_name=短时测试时长 | hint=每种同位素 2 ps | default=2.0
- {TARGET_TEMPERATURE} | required=False | type=float | var_name=目标温度 | hint=由用户确认温度 | default=None

## 产出
- C12 测试轨迹
- C13 测试轨迹
- 运行质量报告

## 质量门禁 quality_gate
- 无未解释异常
- 模型正常加载
- 约束持续有效
- 轨迹与续算材料可用

## 可调资源（edge:resource，仅真实存在）
- datasets/xjtu-sy-rolling-bearing-accelerated-life-test-protocol-and-dataset

## 实例任务（本骨架在各场景的实例化）
- matchem-executing-2ps-short-term-co2-cu111-water-k-interface-inst

## 复用场景
- CO2_Cu111_12C13C_MACE_LAMMPS动力学验证
