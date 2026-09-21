# VASP计算工作流

## 适用范围
VASP密度泛函理论(DFT)计算工作流，用于材料性能的高精度计算验证。包括结构优化、电子结构计算、稳定性分析、带隙计算等。适用于数据驱动材料筛选中的独立验证环节。

## 输入
- 初始晶体结构（POSCAR格式）
- 计算参数设置（INCAR文件）
- 赝势文件（POTCAR文件）
- k点网格设置（KPOINTS文件）

## 输出
- 优化后的晶体结构
- 电子结构数据（能带结构、态密度）
- 总能量和形成能
- 带隙值和其他电子性质

## 流程节点
1. **输入文件准备** → 准备POSCAR、INCAR、POTCAR、KPOINTS文件
2. **结构优化** → 离子弛豫和电子自洽计算
3. **静态计算** → 在优化结构上进行高精度计算
4. **性质计算** → 能带结构、态密度、光学性质等
5. **结果分析** → 提取关键物理量，验证计算收敛性

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| ENCUT | 520 eV | [1] | 平面波截断能 |
| KPOINTS | Γ-centered | [1] | k点网格生成方式 |
| ISPIN | 2 | [2] | 自旋极化设置 |
| EDIFF | 1E-6 | [2] | 电子自洽收敛标准 |
| EDIFFG | -0.01 | [2] | 离子弛豫收敛标准 |
| LREAL | .FALSE. | [2] | 实空间投影设置 |
| PREC | Accurate | [2] | 计算精度设置 |

## 边界与分流
- 计算不收敛：调整 ENCUT、KPOINTS 密度或算法参数
- 磁性系统：根据材料特性设置 ISPIN 和磁矩
- 大规模计算：使用并行计算和任务调度系统
- 高精度需求：使用 HSE06 杂化泛函或 GW 近似

## 质量检查
- 验证能量收敛性（电子和离子）
- 检查力的收敛标准（< 0.01 eV/Å）
- 与Materials Project数据对比验证
- 检查带隙值是否在合理范围内

## 回退策略
- VASP不可用时：使用Quantum ESPRESSO等替代DFT软件
- 计算资源不足时：使用低精度设置或简化模型
- 收敛困难时：尝试不同算法或初始结构

## 资源召回建议
- 当任务需要高精度计算验证时召回此卡片
- 配套使用Materials Project API获取初始结构
- 与机器学习模型卡片结合进行数据驱动筛选

## 证据来源
[1] Scaling deep learning for materials discovery, Nature, 2023, DOI: 10.1038/s41586-023-06735-9
[2] Automated Adsorption Workflow for Semiconductor Surfaces and the Application to Zinc Telluride, Journal of Chemical Information and Modeling, 2021, DOI: 10.1021/acs.jcim.1c00340
[D1] VASP Wiki - The VASP Manual, VASP Software GmbH, 2026, URL: https://www.vasp.at/wiki/index.php/The_VASP_Manual
[D2] VASP Wiki - Calculation setup, VASP Software GmbH, 2026, URL: https://www.vasp.at/wiki/index.php/Category:Calculation_setup