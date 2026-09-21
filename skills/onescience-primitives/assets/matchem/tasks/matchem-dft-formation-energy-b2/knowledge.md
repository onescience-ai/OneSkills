# DFT计算B2金属间化合物形成能工作流

## 适用范围
当需要高保真验证B2金属间化合物的相稳定性和形成能时，使用第一性原理DFT计算。适用于候选合金的独立验证、热力学稳定性评估、energy above hull计算等任务。需要VASP/ABINIT软件许可和计算资源。

## 输入
- B2结构的POSCAR文件（空间群Pm-3m, #221）
- 元素的POTCAR赝势文件
- 计算资源（VASP许可证 + HPC集群或本地多核机器）

## 输出
- 总能量（TOTEN）和形成能（E_form）
- 收敛性报告（能量收敛、力收敛）
- 验证结论：PASS（energy_above_hull < 25 meV/atom）/ REJECT / BLOCKED

## 流程节点

### 1. 结构准备
```
from pymatgen.core import Structure
# 从CIF/POSCAR读取B2结构
struct = Structure.from_file("B2_CoTi.POSCAR")
# 确认空间群
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
sg = SpacegroupAnalyzer(struct)
assert sg.get_space_group_symbol() == "Pm-3m"  # B2
```

### 2. INCAR文件配置
```
# INCAR关键参数
SYSTEM = B2_CoTi_formation_energy
ENCUT = 520        # 平面波截断能(eV)，需收敛性测试
EDIFF = 1E-6       # 电子步收敛标准(eV)
EDIFFG = -0.01     # 离子步收敛标准(eV/Å)
IBRION = 2         # 离子弛豫（CG算法）
NSW = 100          # 最大离子步数
ISIF = 3           # 允许晶胞形状和体积变化
ISPIN = 1          # 非磁性体系；磁性体系设为2
PREC = Accurate    # 精度设置
LREAL = Auto       # 实空间投影
ALGO = Normal      # 电子优化算法
```

### 3. KPOINTS文件
```
# Gamma-centered Monkhorst-Pack网格
Automatic mesh
0
Gamma
kx ky kz    # 通常 kx = ceil(20/a)，a为晶格常数(Å)
0 0 0        # 偏移
```
- B2结构典型KPOINTS：4×4×4 到 8×8×8（取决于晶格常数）
- 收敛性测试：逐步增加网格密度，直到总能量变化 < 1 meV/atom

### 4. 收敛性检查
```
# ENCUT收敛性测试
for encut in [400, 450, 500, 520, 550, 600]:
    # 运行VASP并记录总能量
    # 绘制E vs ENCUT曲线，选择能量平台的最低ENCUT

# KPOINTS收敛性测试
for k in [2, 3, 4, 5, 6, 8]:
    # 运行VASP并记录总能量
    # 绘制E vs k曲线
```

### 5. 形成能计算
```
E_form = E_compound - (x_A * E_element_A + x_B * E_element_B)
# 其中：
# E_compound: B2化合物的DFT总能量（每原子）
# E_element_A/B: 纯元素在对应参考态的能量（每原子）
# x_A/x_B: 元素的摩尔分数
```
- 参考态选择：金属元素使用其稳定晶体结构（如Co→hcp, Ti→hcp, Ni→fcc）
- 每个参考态需单独计算并收敛

### 6. 热力学稳定性判据
- energy_above_hull = E_form - E_form_convex_hull（由pymatgen计算）
- energy_above_hull < 25 meV/atom → 热力学稳定（PASS）
- 25-50 meV/atom → 亚稳（需进一步验证）
- > 50 meV/atom → 不稳定（REJECT）

## 关键参数

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| ENCUT | 520 eV | [1][2] | B2金属间化合物常用值，需收敛验证 |
| EDIFF | 1E-6 eV | [1] | 电子步收敛标准 |
| EDIFFG | -0.01 eV/Å | [1] | 离子步收敛标准 |
| KPOINTS | 4×4×4 ~ 8×8×8 | [1][2] | Gamma-centered，取决于晶格常数 |
| ISPIN | 1（非磁）/2（磁性） | [1] | CoTi非磁用1，NiAl等磁性用2 |
| 稳定性阈值 | < 25 meV/atom | [1] | energy_above_hull判据 |
| 形成能范围 | -2~0 eV/atom | [1][3] | B2金属间化合物典型范围 |

## 边界与分流
- 无VASP许可证 → 标记BLOCKED，列出所需资源
- 无HPC集群 → 使用ABINIT或QE作为替代DFT代码
- 磁性体系 → ISPIN=2，需额外测试不同磁构型
- 多主元体系 → 使用SQS（Special Quasi-random Structures）近似无序构型
- 计算时间过长 → 先用较小KPOINTS和ENCUT做初步筛选，再对候选做精细计算

## 质量检查
- 收敛性：能量变化 < 1 meV/atom（ENCUT和KPOINTS）
- 力收敛：最大残余力 < 0.01 eV/Å
- 形成能物理合理性：负值表示放热形成
- 与文献值对比：与已知B2形成能数据（如Materials Project）偏差 < 10%

## 回退策略
- DFT计算不可用 → 使用简化热力学模型（Miedema模型）估算，但必须标注BLOCKED和方法局限性
- 计算资源不足 → 减小超胞尺寸或使用更粗糙的收敛标准，并在报告中标注

## 资源召回建议
- 当任务需要高保真验证候选合金的相稳定性时召回本卡
- 配套资源：pymatgen（结构操作和热力学分析）、pymatgen-diff（相图计算）、seekpath（高对称路径）

## 证据来源
[1] Khenissa R. et al., "Point defects of intermetallic compounds B2 Nickel-based: DFT calculations", Journal of Nanoparticle Research, 2025, DOI: 10.1007/s11051-025-06243-z
[2] La Rosa L. et al., "Atomistic simulations reveal slip selection in B2-type intermetallic alloys", Acta Materialia, 2025, DOI: 10.1016/j.actamat.2025.121561
[3] Ke H. & Taylor C.D., "DFT-Based Calculation of Dissolution Activation Energy and Kinetics of Ni-Cr Alloys", Journal of The Electrochemical Society, 2020, DOI: 10.1149/1945-7111/abbbbd
[4] Kadde A. et al., "Enthalpy of Formation Modeling Using Third Order Group Contribution Technics and Calculation by DFT Method", International Journal of Thermodynamics, 2020, DOI: 10.5541/ijot.647800
