# 钝化方案建模任务

## 适用范围
适用于钙钛矿太阳能电池界面钝化方案的分子设计、结构建模和DFT计算流程。

## 输入
- 钝化分子类型（Lewis碱、Brønsted碱、离子液体）
- 钙钛矿表面结构（如MAPbI3(001)面）
- DFT计算参数（泛函、截断能、k点网格）

## 输出
- 候选钝化方案列表（分子名称、SMILES结构、吸附位点、计算方法）
- 工艺日志（DFT参数、收敛性、计算时间）
- 吸附能和钝化效率数据

## 操作步骤
1. 选择钝化分子（如Urotropin、2Amino-5-iodobenzoic Acid）
2. 构建钙钛矿表面模型
3. 进行DFT结构优化
4. 计算吸附能（E_ads = E_total - E_surface - E_molecule）
5. 分析电子结构（态密度、能带结构）
6. 评估钝化效率（缺陷态密度减少）

## 输出产物
- `passivation_candidates.json`：候选钝化方案列表
- `calculation_log.md`：工艺日志
- `adsorption_energy.csv`：吸附能数据

## 质量门禁
- 验证DFT计算收敛性（能量变化<1e-4 eV）
- 检查吸附能负值（表示稳定吸附）
- 确认钝化效率（缺陷态密度减少>50%）

## 回退策略
- 若DFT计算失败，调整计算参数或使用替代方法
- 若吸附能异常，检查分子构象和表面模型
- 若钝化效率低，尝试其他分子类型

## 资源召回建议
- 当需要钝化分子设计方法时召回本任务
- 当需要DFT计算参数设置时召回本任务
- 当需要吸附能计算方法时召回本任务

## 证据来源
[1] Enhanced Perovskite Solar Cell Performance via 2Amino-5-iodobenzoic Acid Passivation, ACS Applied Materials & Interfaces, 2022, DOI: 10.1021/acsami.1c22454.s001