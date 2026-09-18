# 钙钛矿太阳能电池接触钝化优化场景

## 适用范围
适用于平面钙钛矿太阳能电池的接触界面钝化优化研究，旨在提高器件效率和稳定性。涉及器件结构设计、钝化分子筛选、DFT计算建模、性能表征和多目标评估。

## 输入
- 钙钛矿太阳能电池器件参数（层序、材料、厚度、面积）
- 钝化分子结构（SMILES、吸附位点）
- DFT计算参数（泛函、截断能、k点网格）
- 性能测试标准（J-V曲线、稳定性测试、迟滞分析）

## 输出
- 器件设计表（层序、材料组成、制备方法）
- 失效判据（效率衰减阈值、稳定性测试条件）
- 钝化方案候选列表（分子名称、吸附能、钝化效率）
- 性能数据（PCE、Voc、FF、Jsc、迟滞指数）
- 优先方案排序和复核计划

## 流程节点
1. **器件设计表制定** → 2. **钝化方案建模** → 3. **性能表征** → 4. **方案评估** → 5. **DFT计算验证** → 6. **结果解释**

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 钙钛矿层材料 | CH3NH3PbI3 | [1] | 常用钙钛矿吸光层 |
| 钝化分子 | Urotropin | [1] | 1D纳米线构建剂 |
| DFT泛函 | PBE | [2] | 常用GGA泛函 |
| 截断能 | 500 eV | [2] | 平面波基组 |
| k点网格 | 4×4×1 | [2] | 表面模型 |

## 边界与分流
- 若DFT计算资源不足，可使用半经验方法或机器学习势函数替代
- 若实验数据缺失，可基于文献数据进行模拟
- 若钝化方案无效，需返回分子设计阶段重新筛选

## 质量检查
- 验证器件设计表是否包含所有必要字段
- 检查DFT计算收敛性（能量变化<1e-4 eV）
- 确认性能数据符合国际标准（如ISOS）

## 回退策略
- 若DFT计算失败，检查输入文件格式和计算参数
- 若性能数据异常，重新进行测试或使用参考数据
- 若方案评估无共识，采用多目标决策分析（如TOPSIS）

## 资源召回建议
- 当需要钙钛矿器件设计规范时召回本卡片
- 当需要钝化分子筛选方法时召回本卡片
- 当需要DFT计算参数设置时召回本卡片

## 证据来源
[1] Construction of 1D perovskite nanowires by Urotropin passivation towards efficient and stable perovskite solar cell, Zardari et al., Solar Energy Materials and Solar Cells, 2021, DOI: 10.1016/j.solmat.2021.111119
[2] Enhanced Perovskite Solar Cell Performance via 2Amino-5-iodobenzoic Acid Passivation, ACS Applied Materials & Interfaces, 2022, DOI: 10.1021/acsami.1c22454.s001
[3] Synergistic Defect Passivation by Metformin Halides for Improving Perovskite Solar Cell Performance, The Journal of Physical Chemistry C, 2023, DOI: 10.1021/acs.jpcc.3c02121.s001
[4] Understanding of Defect Passivation Effect on Wide Band Gap pin Perovskite Solar Cell, ACS Applied Materials & Interfaces, 2024, DOI: 10.1021/acsami.4c05838.s001