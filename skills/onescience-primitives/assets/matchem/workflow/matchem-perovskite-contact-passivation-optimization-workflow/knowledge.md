# 钙钛矿太阳能电池接触钝化优化工作流

## 适用范围
适用于钙钛矿太阳能电池接触界面钝化优化的完整工作流，从器件设计到结果验证。

## 输入
- 研究目标：提高钙钛矿太阳能电池效率和稳定性
- 已知材料：钙钛矿层、传输层、电极层
- 约束条件：计算资源、实验条件

## 输出
- 器件设计表和失效判据
- 钝化方案候选列表
- 性能数据和机制分析
- 优先方案和复核计划

## 流程节点
1. **器件设计表制定** → 2. **钝化方案建模** → 3. **性能表征** → 4. **方案评估** → 5. **DFT计算验证** → 6. **结果解释**

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 器件结构 | Glass/ITO/ETL/Perovskite/HTL/Au | [1] | 标准平面结构 |
| 钝化分子类型 | Lewis碱、Brønsted碱 | [1] | 常见钝化机理 |
| DFT计算类型 | 结构优化、单点能、态密度 | [2] | 标准计算流程 |
| 性能指标 | PCE、Voc、FF、Jsc | [3] | 核心效率参数 |
| 稳定性测试 | ISOS标准 | [4] | 国际标准 |

## 边界与分流
- 若计算资源有限，可使用简化模型或机器学习势函数
- 若实验数据缺失，可基于文献数据进行模拟
- 若多个方案性能相近，采用多目标决策分析

## 质量检查
- 验证器件设计表完整性
- 检查DFT计算收敛性
- 确认性能数据可靠性
- 验证方案评估合理性

## 回退策略
- 若DFT计算失败，调整计算参数或使用替代方法
- 若性能数据异常，重新测试或使用参考数据
- 若方案评估无共识，采用敏感性分析

## 资源召回建议
- 当需要钙钛矿钝化工作流规划时召回本卡片
- 当需要钝化方案筛选方法时召回本卡片
- 当需要性能表征标准时召回本卡片

## 证据来源
[1] Construction of 1D perovskite nanowires by Urotropin passivation towards efficient and stable perovskite solar cell, Zardari et al., Solar Energy Materials and Solar Cells, 2021, DOI: 10.1016/j.solmat.2021.111119
[2] Enhanced Perovskite Solar Cell Performance via 2Amino-5-iodobenzoic Acid Passivation, ACS Applied Materials & Interfaces, 2022, DOI: 10.1021/acsami.1c22454.s001
[3] Synergistic Defect Passivation by Metformin Halides for Improving Perovskite Solar Cell Performance, The Journal of Physical Chemistry C, 2023, DOI: 10.1021/acs.jpcc.3c02121.s001
[4] Understanding of Defect Passivation Effect on Wide Band Gap pin Perovskite Solar Cell, ACS Applied Materials & Interfaces, 2024, DOI: 10.1021/acsami.4c05838.s001