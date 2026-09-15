# 工作流：wf-matchem-e0e8489b

- domain: matchem
- 步骤数: 4
- 共用场景数: 4

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 缺陷模型与对照定义
- desc: 生成母体和缺陷候选并固定浓度/边界。
- depend: []
- prompt: 根据 {HOST_STRUCTURE} 和 {DEFECT_SET} 建立缺陷候选，定义对照和电荷/化学势参考。
- step_input:
  - {HOST_STRUCTURE} (required=True, type=doc, var_name=母体结构, hint=CIF/POSCAR、晶面、层数或样品信, default=CIF/POSCAR)
  - {DEFECT_SET} (required=True, type=list[str], var_name=缺陷候选, hint=空位、掺杂、边缘、晶界或辐照缺陷及浓度。, default=['specified defects'])
- outputs: ['缺陷结构集', '参考态说明']
- quality_gate: ['缺陷浓度与超胞一致', '电荷补偿明确']

### s02 结构电子或功能响应获取
- desc: 计算或测量缺陷形成、迁移、光学或催化响应。
- depend: ['s01']
- prompt: 在 {ENVIRONMENT} 下获取响应数据，保留软件/仪器、参数和原始文件。
- step_input:
  - {ENVIRONMENT} (required=False, type=object, var_name=环境与表征条件, hint=温度、气氛、电位、光照、应力或表征方案。, default={'temperature_K': 298})
- outputs: ['原始响应数据', '缺陷特征']
- quality_gate: ['参考态和校正项记录', '对照样齐全']

### s03 缺陷功能与稳定性排序
- desc: 比较目标功能、副作用和环境稳定性。
- depend: ['s02']
- prompt: 对缺陷候选排序，区分热力学可行性、动力学可达性和实验可制备性。
- step_input:
  - {ENVIRONMENT} (required=False, type=object, var_name=环境与表征条件, hint=温度、气氛、电位、光照、应力或表征方案。, default={'temperature_K': 298})
- outputs: ['候选排序', '风险与证据缺口']
- quality_gate: ['不将形成能直接等同于实际浓度', '适用域明确']

### s04 验证与输出
- desc: 提出可操作的制备或表征验证路线。
- depend: ['s03']
- prompt: 输出优先缺陷方案、验证表征和 PASS/REJECT/BLOCKED 结论。
- step_input:
- （源场景未提供）
- outputs: ['验证计划', '最终结论']
- quality_gate: ['推荐具备可追溯原始证据', '未验证项单列']

## 使用本工作流的场景（场景→工作流映射）
- MoS2单层原子缺陷工程
- hBN单光子发射原子缺陷设计
- 磷烯单层缺陷工程与空气稳定化
- 锂还原室温氧化物缺陷调控
