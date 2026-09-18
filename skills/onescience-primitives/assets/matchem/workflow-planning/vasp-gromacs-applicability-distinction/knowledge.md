# VASP与GROMACS适用场景区分

## 适用范围
当材料模拟任务需要选择计算软件时，根据任务类型（第一性原理计算 vs 分子动力学模拟）选择合适的软件。适用于固态电解质、电池材料、催化材料等领域的计算模拟。

## 输入
- 任务类型：电子结构计算、离子迁移能垒、相稳定性、原子运动轨迹、扩散系数等
- 计算精度要求：量子力学精度 vs 经典力学精度
- 时间尺度：皮秒到纳秒（MD） vs 电子步（DFT）
- 体系大小：原子数（DFT适用于小体系，MD适用于大体系）

## 输出
- 软件选择建议：VASP或GROMACS
- 计算方法：DFT、AIMD、经典MD
- 输入文件模板：INCAR/POSCAR/KPOINTS（VASP）或 topology/parameters（GROMACS）

## 流程节点
1. 分析任务需求 → 2. 确定计算方法 → 3. 选择软件 → 4. 准备输入文件 → 5. 执行计算

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| VASP适用场景 | 电子结构、离子迁移能垒、相稳定性 | [D1] | 第一性原理计算（DFT） |
| GROMACS适用场景 | 原子运动轨迹、扩散系数 | [D2] | 分子动力学模拟（MD） |
| 固态电解质离子电导率预测 | DFT+AIMD（从头算分子动力学） | [归因报告] | 而非经典MD |
| 力场类型 | Buckingham势（经典MD） vs DFT势 | [归因报告] | VASP使用DFT势，GROMACS使用经典力场 |

## 边界与分流
- 如果任务需要电子结构信息（如能带结构、态密度），必须使用VASP或其他DFT软件
- 如果任务需要长时间尺度原子运动（如扩散系数），可使用GROMACS进行经典MD
- 对于固态锂离子导体离子电导率预测，优先使用VASP/CP2K等进行AIMD
- 如果用户指定VASP但任务适合GROMACS，应提醒用户并建议调整

## 质量检查
- 验证软件选择与任务类型匹配
- 检查输入文件格式是否正确
- 确认计算方法符合精度要求

## 回退策略
- 如果VASP不可用，可尝试CP2K等其他AIMD软件
- 如果GROMACS不可用，可尝试LAMMPS等其他MD软件
- 如果任务既需要DFT又需要MD，可串联使用VASP和GROMACS

## 资源召回建议
- 当任务涉及材料模拟软件选择时召回本卡片
- 当场景HPC配置与实际执行工具不匹配时召回本卡片
- 当需要区分第一性原理计算和分子动力学模拟时召回本卡片

## 补充证据（开源权威文档）
[D1] VASP Documentation, University of Vienna, 2026, URL: https://www.vasp.at/wiki/（accessed_at，交叉验证）
[D2] GROMACS Documentation, GROMACS Development Team, 2026, URL: https://manual.gromacs.org/（accessed_at，交叉验证）

## 证据来源
[归因报告] 任务369归因报告，issues[1].optimization_plan，2026