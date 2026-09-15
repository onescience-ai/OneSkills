# 声子分析工具 (phonopy-phonon-analysis)

## 定位与适用任务

Phonopy 是后端无关的声子计算编排层：负责有限位移超胞生成、力常数组装、声子色散/DOS/热力学性质分析。力的计算委托给外部后端（VASP、Quantum ESPRESSO、DeePMD/LAMMPS 等）。适用于晶体材料声子谱计算、热导率预估、动力学稳定性判断（虚频检测）、相变研究中的软模分析。

## 安装与访问方式

- 依赖：phonopy Python 包 + 至少一个力计算后端工作流。
- 安装：通过 pip/conda 安装 phonopy；后端按各自方式安装（如 VASP 需许可证、QE 通过包管理器、DeePMD-kit 通过 pip）。
- 命令行入口：`phonopy` CLI（位移生成用 `phonopy -d`，力常数构建用 `phonopy -f`，分析用 `phonopy --band`/`--dos`/`--tprop`）。
- 结构输入格式：POSCAR、.cif 或其他后端兼容的晶体结构文件。

## 核心操作模式

1. **位移超胞生成**：`phonopy -d --dim="2 2 2" -c POSCAR` — 根据对称性生成所有不等价位移超胞文件（POSCAR-xxx 或 DISP-*）。需指定超胞矩阵/尺寸（`--dim`）和位移振幅（`--amplitude`，默认 0.01 Å）。
2. **力数据收集**：将位移超胞路由至选定后端计算力；每个位移结构产出一个力文件（如 vasprun.xml、FORCE-xxx）。必须保持位移-力文件的完整一一映射。
3. **力常数构建**：`phonopy -f vasprun1.xml vasprun2.xml ...` 生成 `FORCE_SETS` 文件；或直接组装力常数矩阵。
4. **声子分析**：
   - 色散关系：`phonopy --band="0 0 0 0.5 0 0 0.5 0.5 0 0 0 0" --nac`（需指定高对称路径）。
   - 态密度：`phonopy --dos --mesh="40 40 40"`。
   - 热力学性质：`phonopy --tprop --tmin=0 --tmax=1000 --tstep=10 --mesh="40 40 40"`。

## 输出契约与关键字段

- `FORCE_SETS`：力常数数据集文件，phonopy 内部格式，包含所有位移对应的力。
- 色散输出：`band.yaml`（频率 vs q-point 路径）、对应绘图数据。
- DOS 输出：`dos.yaml`（频率 vs 态密度）。
- 热力学输出：`thermal_properties.yaml`（温度 vs 自由能/熵/热容）。
- 关键字段：频率单位 THz 或 cm⁻¹；虚频以负值标记，表示动力学不稳定。
- 非解析修正（NAC）：极性材料需 `--nac` 标志并指定 Born 有效电荷和介电常数。

## 性能与合规

- 超胞大小直接决定计算量：原子数 × 位移数 = 后端 DFT/MLFF 单点计算次数。2×2×2 超胞对 8 原子原胞通常产生 ~6-20 个位移。
- q-point mesh 密度影响 DOS/热力学精度：探索性分析用 20×20×20，收敛结果需 40×40×40 或更高。
- 位移振幅默认 0.01 Å；过小导致数值噪声，过大引入非谐效应。
- 许可证：LGPL-3.0-or-later，可自由用于学术研究。

## 常见坑与降级

- **力文件缺失/不一致**：位移编号与力文件必须严格对应，缺失时 phonopy 报错 → 检查后端输出完整性，补齐缺失计算。
- **超胞过小导致虚频**：增大 `--dim` 至 3×3×3 或更大；若仍不稳定可能为真实动力学不稳定。
- **单位/约定不一致**：不同后端输出力的单位（eV/Å vs Ry/Bohr）需统一 → 确认后端接口文档。
- **非标准晶胞 band path 不明**：查阅 Bilbao Crystallographic Server 或 Setyawan-Curtarolo 标准路径；不确定时显式标注所用约定。
- **收敛不充分致虚频**：增加 DFT 截断能/k-point 密度，或使用更高精度力常数（DFPT 替代有限位移）。
- **降级策略**：若无法完成全部位移计算，可先用小超胞 + 低密度 mesh 做探索性分析，标注未收敛。

## 来源与许可

封装自上游 compchem 技能 `analysis__phonopy.md`（LGPL-3.0）。Phonopy 项目仓库：https://github.com/phonopy/phonopy 。本卡不编造 commit 号，仅引用技能文档中明确记录的参数与工作流。
