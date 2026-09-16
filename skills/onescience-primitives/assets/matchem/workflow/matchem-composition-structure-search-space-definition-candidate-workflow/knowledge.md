# 工作流：matchem-composition-structure-search-space-definition-candidate-workflow

- domain: matchem
- 步骤数: 4
- 共用场景数: 6

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 成分与结构搜索空间定义
- desc: 建立成分、压力和对称性约束。
- depend: []
- prompt: 根据 {COMPOSITION} 和 {STRUCTURE_CONSTRAINTS} 生成合法搜索空间；不明确的价态或压力边界标记 BLOCKED。
- step_input:
  - {COMPOSITION} (required=True, type=str, var_name=成分与化学计量, hint=给出元素、比例、价态假设和电荷约束。, default=目标化学式)
  - {STRUCTURE_CONSTRAINTS} (required=True, type=object, var_name=结构约束, hint=空间群、压力、原子数、层状或配位约束。, default={'pressure_GPa': 0, 'max_atoms': 64})
- outputs: ['搜索空间清单', '初始构型']
- quality_gate: ['化学计量和电荷约束一致', '结构约束可复现']

### s02 候选结构生成与去重
- desc: 生成多样候选构型并去除等价结构。
- depend: ['s01']
- prompt: 在 {STRUCTURE_CONSTRAINTS} 内生成并去重候选，保留生成器、种子和对称性信息。
- step_input:
  - {STRUCTURE_CONSTRAINTS} (required=True, type=object, var_name=结构约束, hint=空间群、压力、原子数、层状或配位约束。, default={'pressure_GPa': 0, 'max_atoms': 64})
- outputs: ['候选结构库', '去重日志']
- quality_gate: ['无原子重叠', '等价结构不重复计数']

### s03 弛豫与稳定性排序
- desc: 对候选结构统一弛豫并计算稳定性指标。
- depend: ['s02']
- prompt: 按 {RELAX_CONFIG} 弛豫候选，比较能量、体积和稳定性；不同设置的结果不得直接排序。
- step_input:
  - {RELAX_CONFIG} (required=False, type=object, var_name=弛豫设置, hint=如采用第一性原理计算，必须写明软件、泛函, default={'method': 'user-confirmed'})
- outputs: ['弛豫结构', '稳定性排序']
- quality_gate: ['收敛标准统一', '参考态定义明确']

### s04 结构验证与输出
- desc: 对优先结构做独立检查和可合成性判断。
- depend: ['s03']
- prompt: 输出前列候选及结构文件；把动力学、有限温度或实验验证缺口明确列为待验证项。
- step_input:
- （源场景未提供）
- outputs: ['优先结构', '验证清单', 'PASS/REJECT/BLOCKED 结论']
- quality_gate: ['不将能量最低等同于可实验合成', '输入和命令可复现']

## 使用本工作流的场景（场景→工作流映射）
- 图神经网络晶体结构预测与优化
- 有限温度晶体结构预测
- 钙钛矿氧化物与卤化物容忍因子稳定性筛选
- 钠酰胺条件晶体结构深度生成预测
- 高压晶体结构深度学习搜索
- 高居里温度二维铁磁材料高通量筛选
