# 流固耦合公开基准数据集来源

## 适用范围
面向流固耦合（FSI）逆向设计任务，提供公开基准数据集的来源清单、获取方式和使用建议。适用于需要FSI训练数据进行模型训练、验证或基准对比的场景；不适用于需要商业软件专有数据或需申请授权的受限数据集。

## 输入
- 任务需求（FSI类型：刚体/柔性体、流体类型：不可压缩/可压缩）
- 数据格式要求（HDF5、NPZ、VTK等）
- 计算资源约束（数据量、分辨率）

## 输出
- 可用数据集清单（名称、来源、格式、许可）
- 数据获取路径（URL、DOI）
- 数据格式说明（变量定义、单位、坐标系）
- 使用建议（适用场景、局限性）

## 数据集来源分类

### 经典FSI基准案例
| 数据集名称 | 来源 | 格式 | 许可 | 适用场景 |
|-----------|------|------|------|----------|
| Turek FSI Benchmark (FSI1/FSI2/FSI3) | turtleFSI/Turek & Hron (2006) | FEniCS格式 | GPL-3.0 | 柔性体涡激振动 |
| Flexible Flapping Flag | preCICE tutorials | OpenFOAM+CalculiX | LGPL-3.0 | 涡激振动、流致振动 |
| Oscillating Cylinder | ANSYS/COMSOL验证案例 | 商业格式 | 有限使用 | 涡脱落、FSI耦合 |

### 开源FSI求解器教程数据
| 求解器 | GitHub仓库 | Stars | 数据格式 | 特点 |
|--------|-----------|-------|----------|------|
| turtleFSI | KVSlab/turtleFSI | 81 | FEniCS | 单体FSI求解器，含Turek基准 |
| preCICE | precice/precice | 970 | 多格式 | 多物理场耦合库，含教程数据 |
| SPHinXsys | Xiangyu-Hu/SPHinXsys | 590 | SPH格式 | SPH方法FSI仿真 |
| LIFE | joconnor22/LIFE | 53 | LBM格式 | 格子玻尔兹曼-浸入边界法 |

### 公开FSI数据集
| 数据集 | 来源 | 格式 | 许可 | 描述 |
|--------|------|------|------|------|
| FSI-Benchmark (AAAI 2026) | HGATSolver论文 | NumPy | 学术使用 | 异构图注意力FSI基准 |
| Cylinder Wake FSI | Diff-FlowFSI论文 | JAX数组 | 开源 | 可微CFD平台验证数据 |
| NACA Airfoil FSI | 公开文献 | VTK/HDF5 | 学术使用 | 翼型流固耦合 |

## 获取方式

### 1. 通过求解器教程获取
```bash
# preCICE FSI教程
git clone https://github.com/precice/tutorials.git
cd tutorials/fluid-structure-interaction

# turtleFSI Turek基准
git clone https://github.com/KVSlab/turtleFSI.git
cd turtleFSI/turtleFSI/problems
```

### 2. 通过论文补充材料获取
- 许多FSI论文在arXiv/会议网站提供数据下载
- 需检查论文许可协议（通常为学术使用）

### 3. 通过在线平台获取
- Zenodo: 搜索"fluid-structure interaction benchmark"
- Figshare: 搜索"FSI dataset"
- Papers With Code: 查找FSI相关任务的数据集

## 关键参数

### 通用判据
| 参数 | 说明 | 来源 |
|------|------|------|
| 数据许可 | 优先选择MIT/Apache/BSD许可 | 最佳实践 |
| 数据格式 | 优先选择通用格式（HDF5/NumPy/VTK） | 工程实践 |
| 文档完整性 | 需有变量定义、单位、坐标系说明 | 数据质量 |
| 可复现性 | 需提供生成代码或脚本 | 学术规范 |

### 典型FSI数据变量
| 变量名 | 物理含义 | 单位 | 说明 |
|--------|----------|------|------|
| velocity | 流体速度场 | m/s | 通常包含u,v,w分量 |
| pressure | 流体压力场 | Pa | 绝对压力或表压 |
| displacement | 固体位移场 | m | 柔性体变形 |
| stress | 固体应力场 | Pa | von Mises应力 |
| interface_force | 流固界面力 | N | 耦合界面数据 |

## 边界与分流
- 商业软件数据（ANSYS、COMSOL）需检查许可条款，通常不适用于开源项目
- 需申请的数据集会阻塞任务，应标记为BLOCKED并提供替代方案
- 数据量不足时可使用合成数据（需标注为合成数据，不用于最终验收）

## 质量检查
- 数据文件完整性校验（MD5/SHA256）
- 变量单位一致性检查
- 时间序列连续性验证
- 流固界面数据对齐验证

## 回退策略
- 公开数据集不可用时，使用求解器教程数据作为替代
- 教程数据不足时，使用合成数据进行原型验证（需标注）
- 商业数据可用时，需获取书面授权并记录来源

## 资源召回建议
- 本卡片为数据源级卡片，可被以下需求召回：FSI数据获取、流固耦合数据集、benchmark dataset、data acquisition for FSI
- 配套卡片：cfd-differentiable-physics-fsi-inverse-design-scenario（场景卡片）
- 配套卡片：cfd-differentiable-physics-fsi-inverse-design-workflow（工作流卡片）

## 补充证据（开源文档）
[D1] preCICE Coupling Library, TU Munich & University of Stuttgart, https://precice.org（accessed 2026-09-17）
[D2] turtleFSI Documentation, KVSlab, https://turtlefsi2.readthedocs.io（accessed 2026-09-17）

## 证据来源
[1] Diff-FlowFSI: A GPU-Optimized Differentiable CFD Platform for High-Fidelity Turbulence and FSI Simulations, arXiv:2505.23940, 2025
[2] HGATSolver: A Heterogeneous Graph Attention Solver for Fluid-Structure Interaction, AAAI 2026, DOI: 10.1609/aaai.v40i2.37129
[3] turtleFSI: A Robust and Monolithic FEniCS-based Fluid-Structure Interaction Solver, JOSS 2020, DOI: 10.21105/joss.02089
