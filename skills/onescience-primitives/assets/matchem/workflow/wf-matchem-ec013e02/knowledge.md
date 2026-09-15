# 工作流：wf-matchem-ec013e02

- domain: matchem
- 步骤数: 4
- 共用场景数: 7

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 参考数据审计与覆盖定义
- desc: 审计结构、能量、力和目标状态的覆盖范围。
- depend: []
- prompt: 读取 {REFERENCE_DATA}，检查重复、异常、化学空间和高温/缺陷/界面覆盖；缺少目标状态时标记 BLOCKED。
- step_input:
  - {REFERENCE_DATA} (required=True, type=doc, var_name=参考量子化学或第一性原理数据, hint=结构、能量、力、应力、计算设置和数据许可, default=extxyz/npz/数据库导出)
- outputs: ['数据审计', '训练验证划分']
- quality_gate: ['训练验证测试严格隔离', '标签计算设置可追溯']

### s02 根源势函数训练
- desc: 按已声明的根源模型训练机器学习势。
- depend: ['s01']
- prompt: 使用 {POTENTIAL_CONFIG} 训练势函数，记录模型根源、版本、随机种子和所有超参数。
- step_input:
  - {POTENTIAL_CONFIG} (required=True, type=object, var_name=势函数根源模型配置, hint=模型根源、截断、特征、训练种子和版本。, default={'model': 'specified root potential', 'seed': 42})
- outputs: ['模型检查点', '训练日志']
- quality_gate: ['模型名称不以变体替代根源', '训练过程可复现']

### s03 能量力应力与外推验证
- desc: 评估预测误差、外推和物理一致性。
- depend: ['s02']
- prompt: 在独立集上报告能量、力、应力误差和外推检测，不以训练误差代替泛化。
- step_input:
  - {REFERENCE_DATA} (required=True, type=doc, var_name=参考量子化学或第一性原理数据, hint=结构、能量、力、应力、计算设置和数据许可, default=extxyz/npz/数据库导出)
- outputs: ['验证报告', '失败构型清单']
- quality_gate: ['独立集不参与调参', '外推构型单独标记']

### s04 分子动力学或结构探索验证
- desc: 在目标条件下进行短程验证和失效分析。
- depend: ['s03']
- prompt: 按 {MD_CONFIG} 进行验证；将势函数不稳定、非物理结构或适用域外结果标记 REJECT/BLOCKED。
- step_input:
  - {MD_CONFIG} (required=False, type=object, var_name=分子动力学验证配置, hint=温度、压力、时间步、体系尺寸和参考计算。, default={'temperature_K': 300, 'steps': 10000})
- outputs: ['MD/探索轨迹', '适用域结论', 'PASS/REJECT/BLOCKED']
- quality_gate: ['不把势函数置信度当作量子或实验验证', '软件版本和命令完整']

## 使用本工作流的场景（场景→工作流映射）
- HfO2非晶液相机器学习势主动学习
- MOF量子精度机器学习势温度主动学习
- 催化反应机器学习势主动学习与增强采样
- 可极化长程相互作用基础机器学习势
- 层状材料可迁移机器学习原子势验证
- 神经网络势长程静电自洽训练
- 缺陷势能面机器学习势探索
