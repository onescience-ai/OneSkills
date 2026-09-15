# 骨架任务：选择性稳定性与能耗分析

- domain: matchem
- 复用场景数: 12
- 实例任务数: 12

## 步骤描述（跨场景聚合去重）
- 在真实进料约束下比较选择性、通量、循环稳定性和能耗。

## 执行 prompt（跨场景聚合去重）
- 根据 {FEED_AND_OPERATION} 分析竞争吸附、污染、湿度或机械稳定性，输出权衡关系。

## 输入槽（var/hint/default）
- {FEED_AND_OPERATION} | required=True | type=object | var_name=进料与运行条件 | hint=组分、浓度、湿度、压力、温度、流量或电场 | default={'feed': 'specified mixture', 'temperature_K': 298}

## 产出
- 失效风险清单
- 性能权衡图

## 质量门禁 quality_gate
- 不将单组分吸附直接等同于混合物分离
- 未测稳定性明确标注

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-05dfd702
- it-220c7e47
- it-347ae219
- it-484ced46
- it-5450de68
- it-62fa9731
- it-84d48ea0
- it-ce701050
- it-d6de794c
- it-f3a996db
- it-f4d804d0
- it-f8aa8861

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
