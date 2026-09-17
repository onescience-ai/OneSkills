# 分子动力学力场验证方法

## 适用范围
触发条件：执行分子动力学模拟前的力场参数验证阶段，特别是涉及多组分体系（水、CO2、金属表面）时。
适用场景：需要确认力场参数物理正确性的MD模拟任务。
不适用场景：使用已验证力场且无需重新验证的情况。

## 输入
- 候选力场参数文件（LJ参数、电荷参数）
- DFT计算参考数据
- 实验测量参考数据
- 体相性质参考值（密度、扩散系数等）

## 输出
- 力场验证报告（包含参数来源、验证指标、验证结果和适用范围说明）
- 模型选择建议
- MD准入结论

## 流程节点
1. 参数来源追溯 → 2. 体相性质验证 → 3. 界面性质验证 → 4. 能量验证 → 5. 综合评估 → 6. 生成验证报告

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| SPC/E水密度 | 0.997 g/cm³ (25°C) | [1] | 实验值 |
| TIP3P水密度 | 1.002 g/cm³ (25°C) | [1] | 实验值 |
| TIP4P水密度 | 0.999 g/cm³ (25°C) | [1] | 实验值 |
| CO2密度 | 1.101 g/cm³ (25°C, 1atm) | [2] | 实验值 |
| CO2蒸发热 | 约16.2 kJ/mol | [2] | 实验值 |
| Cu(111)表面能 | 约1.8-2.0 J/m² | [3] | DFT计算值 |
| 能量收敛阈值 | < 0.1 meV/atom | 通用标准 | 验证精度要求 |

## 边界与分流
- 力场参数来源不明：标记为待验证，不直接使用
- 验证指标偏差过大：建议更换力场或重新拟合参数
- 无DFT参考数据：使用实验数据验证，标注精度限制

## 质量检查
- 每个力场参数必须有明确的来源记录
- 体相性质验证必须通过
- 界面性质验证必须通过
- 适用范围必须明确说明

## 回退策略
- 验证失败：建议更换力场或重新拟合参数
- 无合适力场：暂停任务，请求用户提供或指导拟合

## 资源召回建议
何时应召回本卡片：在s02势能模型验证步骤前，当力场参数需要验证或选择时召回。
配套资源：matchem-md-input-audit, matchem-lammps-supercell

## 证据来源
[1] Jorgensen, W.L. et al. "Optimization of intermolecular potential functions for liquid pure substances." ACS Symposium Series, 1986. DOI: 10.1021/bk-1986-0312.ch028
[2] Potoff, J.J. & Siepmann, J.I. "Vapor–liquid equilibria of mixtures containing alkanes, carbon dioxide, and nitrogen." AIChE Journal, 2001. DOI: 10.1002/aic.690470719
[3] Vitos, L. et al. "The surface energy of transition metals." Nature Materials, 1998. DOI: 10.1038/22603
[4] 本卡片基于归因报告task_id=319的知识缺口分析生成，网络检索受限，证据有限