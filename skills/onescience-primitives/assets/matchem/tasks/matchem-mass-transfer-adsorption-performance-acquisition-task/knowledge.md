# 骨架任务：传质或吸附性能获取

- domain: matchem
- 复用场景数: 12
- 实例任务数: 12

## 步骤描述（跨场景聚合去重）
- 计算或测量吸附、扩散、渗透和选择性。

## 执行 prompt（跨场景聚合去重）
- 按 {EVALUATION_CONFIG} 获取原始性能数据，记录模型、仪器、平衡时间和对照。

## 输入槽（var/hint/default）
- {EVALUATION_CONFIG} | required=False | type=object | var_name=评价方法 | hint=说明吸附、扩散、渗透、分离或实验测试方法 | default={'method': 'user-confirmed'}

## 产出
- 原始性能数据
- 方法日志

## 质量门禁 quality_gate
- 平衡与稳态判据明确
- 空白和对照样可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-mass-transfer-adsorption-black-gold-thin-film-solar-inst
- matchem-mass-transfer-adsorption-diamine-grafted-mof-co2-inst
- matchem-mass-transfer-adsorption-hydrophilic-responsive-inst
- matchem-mass-transfer-adsorption-mof-deep-generative-inverse-inst
- matchem-mass-transfer-adsorption-mof-high-throughput-hydrogen-inst
- matchem-mass-transfer-adsorption-mof-molecular-diffusion-inst
- matchem-mass-transfer-adsorption-mof-pre-combustion-co2-inst
- matchem-mass-transfer-adsorption-mof-trace-co2-air-capture-inst
- matchem-mass-transfer-adsorption-monolayer-mos2-nanopore-inst
- matchem-mass-transfer-adsorption-mxene-kevlar-composite-inst
- matchem-mass-transfer-adsorption-mxene-zeolite-gas-separation-inst
- matchem-mass-transfer-adsorption-nanoparticle-template-inst

## 复用场景
- MOF分子扩散增强CO2捕集性能评估
- MOF深度生成逆向设计
- MOF燃烧前CO2捕集遗传算法筛选
- MOF痕量CO2空气捕集材料定制
- MOF高通量储氢筛选
- MXeneKevlar复合膜渗透压发电设计
- MXene分子筛气体分离膜设计
- 二胺接枝MOF协同CO2捕集设计
- 亲水响应膜油水分离设计
- 单层MoS2纳米孔海水淡化设计
- 纳米颗粒模板纳滤膜海水淡化设计
- 黑金薄膜太阳能蒸汽发生设计
