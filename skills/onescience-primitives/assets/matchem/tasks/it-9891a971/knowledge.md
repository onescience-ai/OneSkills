# 实例任务：结构与分离目标定义 @ MOF分子扩散增强CO2捕集性能评估

- domain: matchem
- 骨架: tk-matchem-33e5dc32
- 场景: sc-1ac80f69 (MOF分子扩散增强CO2捕集性能评估)
- step_id: s01
- depend: []

## 场景研究主体
- MOF分子扩散增强CO2捕集性能评估
- 关联论文: Molecular diffusion enhanced performance evaluation of metal-organic frameworks for CO2 capture | doi:

## 本实例步骤描述
确认孔道或膜结构及目标分离/捕集指标。

## 本实例执行 prompt
读取 {MATERIAL_MODEL} 与 {FEED_AND_OPERATION}，确定目标组分、竞争组分和性能指标。

## 本实例输入槽
- {MATERIAL_MODEL} | required=True | type=doc | var_name=多孔材料或膜结构 | hint=给出孔道、层间距、表面官能团、厚度和来源 | default=CIF/膜结构参数
- {FEED_AND_OPERATION} | required=True | type=object | var_name=进料与运行条件 | hint=组分、浓度、湿度、压力、温度、流量或电场 | default={'feed': 'specified mixture', 'temperature_K': 298}

## 本实例产出
- 结构与工况清单
- 目标指标

## 本实例质量门禁
- 孔道和边界条件明确
- 进料组成与单位一致

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
