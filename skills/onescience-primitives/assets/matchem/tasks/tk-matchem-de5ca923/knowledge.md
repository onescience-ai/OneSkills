# 骨架任务：响应测试或模拟

- domain: matchem
- 复用场景数: 5
- 实例任务数: 5

## 步骤描述（跨场景聚合去重）
- 获得材料在目标条件下的原始响应。

## 执行 prompt（跨场景聚合去重）
- 根据 {MEASUREMENT_DATA} 或新测试/模拟获取原始数据，记录仪器、软件、校准和异常样本。

## 输入槽（var/hint/default）
- {MEASUREMENT_DATA} | required=False | type=doc | var_name=表征数据 | hint=力学、显微、谱学或原位测试数据。 | default=optional

## 产出
- 原始响应数据
- 运行日志

## 质量门禁 quality_gate
- 对照条件一致
- 异常样本不静默删除

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-39987506
- it-40cd6fb0
- it-6b8adfbf
- it-8ea55262
- it-deaf147d

## 复用场景
- CrCoNi中高熵合金低温断裂韧性分析
- 复杂合金热稳定纳米颗粒扩散调控
- 激光粉末床熔融钥孔波动与孔隙形成分析
- 难熔高熵合金位错迁移与短程有序分析
- 高熵金属玻璃纳米颗粒电合成与电催化设计
