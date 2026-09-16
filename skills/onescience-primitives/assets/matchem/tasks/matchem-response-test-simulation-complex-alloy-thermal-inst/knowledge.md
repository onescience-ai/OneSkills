# 实例任务：响应测试或模拟 @ 复杂合金热稳定纳米颗粒扩散调控

- domain: matchem
- 骨架: matchem-response-test-simulation-task
- 场景: matchem-complex-alloy-thermal-stable-nanoparticle-diffusion-control-scenario (复杂合金热稳定纳米颗粒扩散调控)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- 复杂合金热稳定纳米颗粒扩散调控
- 关联论文: Achieving thermally stable nanoparticles in chemically complex alloys via controllable sluggish lattice diffusion | doi:

## 本实例步骤描述
获得材料在目标条件下的原始响应。

## 本实例执行 prompt
根据 {MEASUREMENT_DATA} 或新测试/模拟获取原始数据，记录仪器、软件、校准和异常样本。

## 本实例输入槽
- {MEASUREMENT_DATA} | required=False | type=doc | var_name=表征数据 | hint=力学、显微、谱学或原位测试数据。 | default=optional

## 本实例产出
- 原始响应数据
- 运行日志

## 本实例质量门禁
- 对照条件一致
- 异常样本不静默删除

## 可调资源（edge:resource，仅真实存在）
- models/data-efficient-machine-learning-potentials-modeling-catalytic

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
