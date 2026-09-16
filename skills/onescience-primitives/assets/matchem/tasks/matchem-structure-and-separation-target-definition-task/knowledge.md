# 骨架任务：结构与分离目标定义

- domain: matchem
- 复用场景数: 12
- 实例任务数: 12

## 步骤描述（跨场景聚合去重）
- 确认孔道或膜结构及目标分离/捕集指标。

## 执行 prompt（跨场景聚合去重）
- 读取 {MATERIAL_MODEL} 与 {FEED_AND_OPERATION}，确定目标组分、竞争组分和性能指标。

## 输入槽（var/hint/default）
- {MATERIAL_MODEL} | required=True | type=doc | var_name=多孔材料或膜结构 | hint=给出孔道、层间距、表面官能团、厚度和来源 | default=CIF/膜结构参数
- {FEED_AND_OPERATION} | required=True | type=object | var_name=进料与运行条件 | hint=组分、浓度、湿度、压力、温度、流量或电场 | default={'feed': 'specified mixture', 'temperature_K': 298}

## 产出
- 目标指标
- 结构与工况清单

## 质量门禁 quality_gate
- 孔道和边界条件明确
- 进料组成与单位一致

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- matchem-structure-and-separation-black-gold-thin-film-solar-inst
- matchem-structure-and-separation-diamine-grafted-mof-co2-inst
- matchem-structure-and-separation-hydrophilic-responsive-inst
- matchem-structure-and-separation-mof-deep-generative-inverse-inst
- matchem-structure-and-separation-mof-high-throughput-hydrogen-inst
- matchem-structure-and-separation-mof-molecular-diffusion-inst
- matchem-structure-and-separation-mof-pre-combustion-co2-inst
- matchem-structure-and-separation-mof-trace-co2-air-capture-inst
- matchem-structure-and-separation-monolayer-mos2-nanopore-inst
- matchem-structure-and-separation-mxene-kevlar-composite-inst
- matchem-structure-and-separation-mxene-zeolite-gas-separation-inst
- matchem-structure-and-separation-nanoparticle-template-inst

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
