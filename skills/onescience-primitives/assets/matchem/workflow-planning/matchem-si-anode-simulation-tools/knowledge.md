# 多孔硅负极电化学模拟计算工具选择知识

## 适用范围
- **触发条件**：orchestrator 在 s02 步骤执行计算或测试配置时
- **适用场景**：多孔硅锂离子电池负极结构设计任务，需要选择合适的计算工具
- **不适用场景**：纯实验任务、文献调研任务

## 输入
### 计算目标
1. **电子结构计算**：能带结构、态密度、电荷分布
2. **离子扩散模拟**：锂离子嵌入/脱出路径、扩散系数
3. **力学响应分析**：体积膨胀、应力分布、裂纹扩展
4. **电化学性能预测**：容量、倍率性能、循环寿命

### 资源约束
| 约束类型 | 说明 |
|----------|------|
| 计算资源 | CPU核心数、GPU数量、内存大小 |
| 时间限制 | 任务完成时间要求 |
| 软件许可 | 商业软件 vs 开源软件 |
| 用户技能 | 用户对工具的熟悉程度 |

## 输出
### 工具选择推荐
```yaml
recommended_tools:
  - tool: VASP
    purpose: "第一性原理电子结构计算"
    scale: "原子尺度（<1000原子）"
    accuracy: "高"
    cost: "高"
    input_format: "POSCAR, POTCAR, INCAR, KPOINTS"
    output_format: "OUTCAR, OSZICAR, CHGCAR"
  
  - tool: LAMMPS
    purpose: "分子动力学模拟"
    scale: "介观尺度（10^3-10^6原子）"
    accuracy: "中-高"
    cost: "中"
    input_format: "in.lammps, data.lammps"
    output_format: "log.lammps, dump.*"
  
  - tool: COMSOL
    purpose: "连续介质多物理场仿真"
    scale: "宏观尺度（器件级）"
    accuracy: "中"
    cost: "高（商业软件）"
    input_format: ".mph模型文件"
    output_format: ".csv, .txt结果文件"
```

## 流程节点
1. **需求分析** → 确定计算目标和精度要求
2. **资源评估** → 检查可用计算资源
3. **工具匹配** → 根据需求和资源选择工具
4. **配置生成** → 生成输入文件模板
5. **验证测试** → 小规模测试确认工具可用

## 关键参数
| 工具 | 适用尺度 | 典型计算量 | 内存需求 | 时间成本 |
|------|----------|------------|----------|----------|
| VASP | 原子尺度 | <1000原子 | 16-128 GB | 小时-天 |
| LAMMPS | 介观尺度 | 10^3-10^6原子 | 8-64 GB | 分钟-小时 |
| COMSOL | 宏观尺度 | 器件级 | 8-32 GB | 分钟-小时 |
| Gaussian | 分子尺度 | <100原子 | 4-32 GB | 分钟-小时 |
| Quantum ESPRESSO | 原子尺度 | <500原子 | 8-64 GB | 小时-天 |

## 边界与分流
### 工具选择决策树
```
计算目标是什么？
├─ 电子结构/化学键 → VASP/Gaussian/Quantum ESPRESSO
├─ 离子扩散/动力学 → LAMMPS/GROMACS
├─ 力学响应/应力 → LAMMPS/ABAQUS
├─ 电化学性能/传输 → COMSOL/Neware
└─ 多尺度耦合 → 多工具联合
```

### 异常处理
1. **工具不可用**：推荐替代工具或云端计算
2. **资源不足**：建议简化模型或使用近似方法
3. **精度不足**：建议升级计算方法或增加计算资源

## 质量检查
- [ ] 选择的工具与计算目标匹配
- [ ] 输入文件格式正确
- [ ] 计算资源满足需求
- [ ] 输出格式可被后续步骤解析

## 回退策略
1. 首选工具不可用 → 使用功能相似的替代工具
2. 计算成本过高 → 使用机器学习势函数或粗粒化模型
3. 结果不收敛 → 调整计算参数或使用更稳定的算法

## 资源召回建议
- **何时召回**：s02步骤开始时、工具选择不确定时
- **配套资源**：matchem-porous-si-anode-material-structure（材料结构参数）

## 证据来源
[1] Revolutionizing batteries based on digital twin through AI-simulation synergy for design, manufacturing, operation, and recycling, National Science Open, 2025, DOI: 10.1360/nso/20250054
[2] Data-driven systematic parameter identification of an electrochemical model for lithium-ion batteries with artificial intelligence, Energy Storage Materials, 2021, DOI: 10.1016/j.ensm.2021.10.023