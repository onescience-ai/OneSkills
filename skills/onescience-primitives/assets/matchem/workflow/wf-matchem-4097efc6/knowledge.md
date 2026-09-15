# 工作流：wf-matchem-4097efc6

- domain: matchem
- 步骤数: 4
- 共用场景数: 5

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 材料与对照方案定义
- desc: 固定成分、工艺、微结构和对照样。
- depend: []
- prompt: 读取 {MATERIAL_AND_PROCESS} 与 {LOAD_OR_REACTION_CONDITION}，定义变量、对照和失效/性能判据。
- step_input:
  - {MATERIAL_AND_PROCESS} (required=True, type=object, var_name=材料与工艺参数, hint=成分、微结构、制备或加工路径及对照样。, default={'composition': 'specified', 'process': 'specified'})
  - {LOAD_OR_REACTION_CONDITION} (required=True, type=object, var_name=载荷或反应条件, hint=温度、应变率、环境、反应时间或电化学条件, default={'temperature_K': 298})
- outputs: ['试样或模型清单', '对照方案']
- quality_gate: ['变量单一可追溯', '工况与单位明确']

### s02 响应测试或模拟
- desc: 获得材料在目标条件下的原始响应。
- depend: ['s01']
- prompt: 根据 {MEASUREMENT_DATA} 或新测试/模拟获取原始数据，记录仪器、软件、校准和异常样本。
- step_input:
  - {MEASUREMENT_DATA} (required=False, type=doc, var_name=表征数据, hint=力学、显微、谱学或原位测试数据。, default=optional)
- outputs: ['原始响应数据', '运行日志']
- quality_gate: ['对照条件一致', '异常样本不静默删除']

### s03 机制与性能定量分析
- desc: 建立组成/工艺-微结构-性能或反应关系。
- depend: ['s02']
- prompt: 在 {LOAD_OR_REACTION_CONDITION} 下计算性能、结构变化和机制证据，报告不确定性。
- step_input:
  - {LOAD_OR_REACTION_CONDITION} (required=True, type=object, var_name=载荷或反应条件, hint=温度、应变率、环境、反应时间或电化学条件, default={'temperature_K': 298})
- outputs: ['量化指标', '机制分析']
- quality_gate: ['相关性与因果证据区分', '统计样本量明确']

### s04 窗口输出与复核
- desc: 输出可执行材料/工艺窗口和验证计划。
- depend: ['s03']
- prompt: 给出推荐窗口、限制条件和 PASS/REJECT/BLOCKED；未完成独立复核时明确写出。
- step_input:
- （源场景未提供）
- outputs: ['推荐窗口', '验证计划', '最终结论']
- quality_gate: ['结论可追溯', '安全和可制造性限制明确']

## 使用本工作流的场景（场景→工作流映射）
- CrCoNi中高熵合金低温断裂韧性分析
- 复杂合金热稳定纳米颗粒扩散调控
- 激光粉末床熔融钥孔波动与孔隙形成分析
- 难熔高熵合金位错迁移与短程有序分析
- 高熵金属玻璃纳米颗粒电合成与电催化设计
