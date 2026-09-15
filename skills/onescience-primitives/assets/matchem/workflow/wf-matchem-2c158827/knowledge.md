# 工作流：wf-matchem-2c158827

- domain: matchem
- 步骤数: 4
- 共用场景数: 12

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 结构与分离目标定义
- desc: 确认孔道或膜结构及目标分离/捕集指标。
- depend: []
- prompt: 读取 {MATERIAL_MODEL} 与 {FEED_AND_OPERATION}，确定目标组分、竞争组分和性能指标。
- step_input:
  - {MATERIAL_MODEL} (required=True, type=doc, var_name=多孔材料或膜结构, hint=给出孔道、层间距、表面官能团、厚度和来源, default=CIF/膜结构参数)
  - {FEED_AND_OPERATION} (required=True, type=object, var_name=进料与运行条件, hint=组分、浓度、湿度、压力、温度、流量或电场, default={'feed': 'specified mixture', 'temperature_K': 298})
- outputs: ['结构与工况清单', '目标指标']
- quality_gate: ['孔道和边界条件明确', '进料组成与单位一致']

### s02 传质或吸附性能获取
- desc: 计算或测量吸附、扩散、渗透和选择性。
- depend: ['s01']
- prompt: 按 {EVALUATION_CONFIG} 获取原始性能数据，记录模型、仪器、平衡时间和对照。
- step_input:
  - {EVALUATION_CONFIG} (required=False, type=object, var_name=评价方法, hint=说明吸附、扩散、渗透、分离或实验测试方法, default={'method': 'user-confirmed'})
- outputs: ['原始性能数据', '方法日志']
- quality_gate: ['平衡与稳态判据明确', '空白和对照样可追溯']

### s03 选择性稳定性与能耗分析
- desc: 在真实进料约束下比较选择性、通量、循环稳定性和能耗。
- depend: ['s02']
- prompt: 根据 {FEED_AND_OPERATION} 分析竞争吸附、污染、湿度或机械稳定性，输出权衡关系。
- step_input:
  - {FEED_AND_OPERATION} (required=True, type=object, var_name=进料与运行条件, hint=组分、浓度、湿度、压力、温度、流量或电场, default={'feed': 'specified mixture', 'temperature_K': 298})
- outputs: ['性能权衡图', '失效风险清单']
- quality_gate: ['不将单组分吸附直接等同于混合物分离', '未测稳定性明确标注']

### s04 材料或工艺窗口输出
- desc: 提出材料结构与运行条件的可执行组合。
- depend: ['s03']
- prompt: 输出推荐材料/膜和操作窗口，给出验证优先级和 PASS/REJECT/BLOCKED。
- step_input:
- （源场景未提供）
- outputs: ['推荐窗口', '验证计划', '最终结论']
- quality_gate: ['推荐可回溯到原始数据', '不确定性明确']

## 使用本工作流的场景（场景→工作流映射）
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
