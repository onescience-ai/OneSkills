# 工作流：matchem-material-condition-modeling-structure-or-electrochemical-workflow

- domain: matchem
- 步骤数: 4
- 共用场景数: 15

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 材料与工况建模
- desc: 核对材料组成、初始状态和电池工况。
- depend: []
- prompt: 读取 {MATERIAL_STRUCTURE} 与 {CELL_CONDITION}；明确满锂/脱锂状态、对照样和失效判据。
- step_input:
  - {MATERIAL_STRUCTURE} (required=True, type=doc, var_name=电极或电解质材料信息, hint=结构文件、组成、粒径或配方及来源。, default=CIF/POSCAR/配方表)
  - {CELL_CONDITION} (required=True, type=object, var_name=电池工况, hint=电压窗口、倍率、温度、负载量和循环数。, default={'voltage_window_V': [2.8, 4.5], 'temperature_C': 25})
- outputs: ['材料与工况清单', '初始状态记录']
- quality_gate: ['材料化学计量和电压参考明确', '缺失电解液或对电极信息时标记 BLOCKED']

### s02 结构或电化学响应获取
- desc: 执行统一的计算、表征或循环测试。
- depend: ['s01']
- prompt: 按 {COMPUTE_OR_TEST_CONFIG} 获取结构演化、容量、阻抗或失效数据，记录版本、命令或仪器校准。
- step_input:
  - {COMPUTE_OR_TEST_CONFIG} (required=False, type=object, var_name=计算或测试配置, hint=说明软件、仪器、收敛或校准信息。, default={'mode': 'experiment_or_user_confirmed_simulation'})
- outputs: ['原始响应数据', '实验/计算日志']
- quality_gate: ['对照样采用同一工况', '原始数据可追溯']

### s03 退化机制与性能指标分析
- desc: 量化相变、应变、界面、锂沉积或容量变化。
- depend: ['s02']
- prompt: 依据 {CELL_CONDITION} 计算性能指标并建立结构-性能关联，区分相关性和机制证据。
- step_input:
  - {CELL_CONDITION} (required=True, type=object, var_name=电池工况, hint=电压窗口、倍率、温度、负载量和循环数。, default={'voltage_window_V': [2.8, 4.5], 'temperature_C': 25})
- outputs: ['性能指标表', '机制证据链']
- quality_gate: ['不得将单次循环外推为寿命', '不确定性和异常样本保留']

### s04 方案排序与独立复核
- desc: 输出可执行的材料或工况改进建议。
- depend: ['s03']
- prompt: 根据性能、稳定性和安全约束排序候选；没有独立复核时写明待验证。
- step_input:
- （源场景未提供）
- outputs: ['推荐方案', '验证计划', 'PASS/REJECT/BLOCKED 结论']
- quality_gate: ['推荐依据可回溯', '实验验证与计算预测分开报告']

## 使用本工作流的场景（场景→工作流映射）
- LiCoO2高电压TiMgAl协同掺杂优化
- LiMn富锂层状正极电流密度退化分析
- 商用锂离子电池电压松弛容量估计
- 固态电池锂沉积原位CT机器学习检测
- 固态锂离子导体无监督发现
- 多孔硅锂离子电池负极结构设计
- 富锂层状正极结构退化与氧释放分析
- 电池颗粒碳粘结剂脱粘机器学习统计
- 离子聚合物电解质机器学习配方发现
- 锂硫电池多硫化物吸附扩散协同设计
- 锂离子电池日历老化预测
- 锂离子电池电极微结构深度学习分割
- 锂离子电池衰减参数物理数据融合反演
- 锂金属电解液界面枝晶恒电势模拟
- 高离子电导电解液基础模型配方设计
