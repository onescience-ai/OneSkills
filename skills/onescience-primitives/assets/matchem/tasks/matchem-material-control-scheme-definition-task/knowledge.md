# 骨架任务：材料与对照方案定义

- domain: matchem
- 复用场景数: 5
- 实例任务数: 5

## 步骤描述（跨场景聚合去重）
- 固定成分、工艺、微结构和对照样。

## 执行 prompt（跨场景聚合去重）
- 读取 {MATERIAL_AND_PROCESS} 与 {LOAD_OR_REACTION_CONDITION}，定义变量、对照和失效/性能判据。

## 输入槽（var/hint/default）
- {MATERIAL_AND_PROCESS} | required=True | type=object | var_name=材料与工艺参数 | hint=成分、微结构、制备或加工路径及对照样。 | default={'composition': 'specified', 'process': 'specified'}
- {LOAD_OR_REACTION_CONDITION} | required=True | type=object | var_name=载荷或反应条件 | hint=温度、应变率、环境、反应时间或电化学条件 | default={'temperature_K': 298}

## 产出
- 对照方案
- 试样或模型清单

## 质量门禁 quality_gate
- 变量单一可追溯
- 工况与单位明确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-material-control-scheme-complex-alloy-thermal-inst
- matchem-material-control-scheme-crconi-medium-high-entropy-inst
- matchem-material-control-scheme-high-entropy-metallic-glass-inst
- matchem-material-control-scheme-laser-powder-bed-fusion-inst
- matchem-material-control-scheme-refractory-high-entropy-inst

## 复用场景
- CrCoNi中高熵合金低温断裂韧性分析
- 复杂合金热稳定纳米颗粒扩散调控
- 激光粉末床熔融钥孔波动与孔隙形成分析
- 难熔高熵合金位错迁移与短程有序分析
- 高熵金属玻璃纳米颗粒电合成与电催化设计
