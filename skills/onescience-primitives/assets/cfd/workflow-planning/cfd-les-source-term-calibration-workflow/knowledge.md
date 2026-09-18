# LES等效源项校准与后验CFD耦合工作流

## 适用范围

面向LES等效源项校准与高保真后验CFD耦合任务，定义从RANS数据到LES源项映射的完整工作流。适用于需要将数据驱动模型嵌入CFD求解器执行后验稳定性验证的任务，包括源项注入接口设计、求解器耦合配置和HPC资源评估。不适用于仅需先验评估（不嵌入求解器）的任务。

## 输入

- 任务目标：将训练好的LES等效源项模型嵌入CFD求解器进行后验验证
- 数据需求：RANS基准场、LES训练数据、模型权重文件、网格与边界条件配置
- 格式要求：OpenFOAM字典文件、NumPy数组或VTK场文件

## 输出

- 求解器耦合配置（sourceTerm注入字典）
- 后验场文件（速度场、压力场、湍流量）
- 稳定性评估指标（stability_horizon、收敛行为）
- 求解器稳定性报告（solver_stability.csv）

## 流程节点

1. **前置条件检查** → 2. **源项接口设计** → 3. **求解器配置** → 4. **后验推进执行** → 5. **稳定性评估**

### 步骤1：前置条件检查
- 操作：验证CFD求解器可用性、HPC环境就绪性、输入数据完整性
- 参数：求解器二进制路径、网格文件、边界条件文件、模型权重文件
- 工具：环境检测脚本
- 质量门禁：求解器可执行、网格有效、模型文件完整

### 步骤2：源项接口设计
- 操作：设计模型输出到求解器源项的映射接口
- 参数：源项注入方式（explicit/implicit）、场变量名、时间步耦合策略
- 工具：OpenFOAM fvOptions字典
- 质量门禁：接口格式与求解器兼容、物理量纲一致

### 步骤3：求解器配置
- 操作：配置LES求解器参数（pimpleFoam/highFoam等）
- 参数：湍流模型、离散格式、时间步长、Courant数限制
- 工具：OpenFOAM字典文件
- 质量门禁：配置合理、CFL<1、收敛判据设置

### 步骤4：后验推进执行
- 操作：运行耦合求解器执行后验推进
- 参数：最大物理时间、输出频率、重启检查点
- 工具：OpenFOAM求解器 + SLURM作业调度
- 质量门禁：残差单调下降、物理量无发散、质量守恒误差<1%

### 步骤5：稳定性评估
- 操作：评估模型在求解器中的长期稳定性
- 参数：stability_horizon（稳定推进步数）、能谱偏差、统计量收敛
- 工具：后处理脚本
- 质量门禁：stability_horizon>阈值、统计量收敛

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 求解器可用性检查 | 二进制可执行+版本验证 | [1] | 求解器必须在PATH中或指定路径 |
| 网格有效性 | 负体积=0, 正交性>0.1 | [OpenFOAM标准] | 网格质量门禁 |
| 模型接口格式 | fvOptions/sourceTerm | [1] | OpenFOAM标准源项注入方式 |
| CFL限制 | <1.0（显式）/ <5.0（隐式） | [领域标准] | 时间步稳定性要求 |
| 稳定性判据 | 统计量收敛+无发散 | [2] | 后验推进成功标准 |
| HPC最低配置 | 4节点×32核×64GB | [5] | 中等规模LES最低要求 |

### 校准数值（体系专属值）

以下数值来自典型LES源项校准任务，供量级校准；其他体系需以自身证据重新锚定：

| 参数 | 典型值 | 来源 | 说明 |
|------|--------|------|------|
| RANS-to-LES映射误差 | <5%（速度场L2） | [1] | NASA Hump案例 |
| 联合训练Reynolds数外推倍数 | 4x | [2] | 壁湍流案例 |
| SGS模型能谱偏差 | <10%（惯性区） | [3] | 多尺度CNN结果 |
| 后验稳定推进步数 | >1000步 | [3] | 无发散判据 |
| HPC作业运行时间 | 2-24小时 | [5] | 取决于网格规模 |

## 边界与分流

### 前提1：CFD求解器可用且已安装
- **不成立时转向**：使用onescience-installer安装OpenFOAM，或标注BLOCKED状态跳过后验步骤，仅输出先验评估结果

### 前提2：HPC计算资源可申请
- **不成立时转向**：在本地执行小规模测试（降低网格分辨率），或标注BLOCKED状态并记录资源需求

### 前提3：模型输出格式与求解器接口兼容
- **不成立时转向**：增加格式转换层，将模型输出转为OpenFOAM兼容的field格式

### 前提4：RANS基准场和边界条件文件存在
- **不成立时转向**：使用解析解或简化边界条件，或标注BLOCKED状态

## 质量检查

1. **求解器启动检查**：求解器能正常启动并读取配置
2. **源项注入验证**：源项场量纲正确、数值范围合理
3. **CFL稳定性**：Courant数在安全范围内
4. **质量守恒验证**：进出口流量守恒误差<1%
5. **长期稳定性**：统计量在足够推进步数后收敛

## 回退策略

1. **求解器不可用**：标注BLOCKED，仅输出先验评估，记录所需求解器版本和安装方式
2. **HPC资源不足**：降低网格分辨率，使用本地小规模测试验证接口正确性
3. **源项注入导致发散**：减小源项幅值或增大时间步松弛因子
4. **模型精度不足**：返回训练阶段重新优化模型

## 资源召回建议

- **何时召回本卡片**：当任务需要将LES/湍流模型嵌入CFD求解器执行后验验证时
- **配套资源**：
  - cfd-openfoam-porous-media-setup：OpenFOAM安装与配置
  - cfd-model-validation-metrics：模型验收指标体系
  - general-cfd-task-artifacts：CFD任务产物清单
  - cfd-data-driven-model-data-availability-check：数据可用性检查

## 证据来源

[1] Saverio L, Bucci MA, Farro G, et al. "An End-to-End PyTorch Interface for Differentiable PDE Solvers: A RANS Model-Correction Study", arXiv:2605.28858, 2026. — 可微PDE求解器框架，RANS闭合项优化方法
[2] Fan X, Liu Y, Wang M, et al. "Differentiable Hybrid Neural-CFD Modelling of Wall-Bounded Turbulence", arXiv:2607.17357, 2026. — SGS和壁面闭合联合学习，4x Re外推
[3] Jalaali B, Okabayashi K. "Multiscale Convolutional Neural Networks for Subgrid-scale Modeling in LES", arXiv:2502.10814, 2025. — 多尺度CNN SGS建模
[4] Yue L, Somasekharan N, et al. "Foam-Agent 2.0: End-to-End Composable Multi-Agent Framework for Automating CFD", arXiv:2509.18178, 2025. — OpenFOAM自动化工作流，88.2%成功率
[5] Maulik R, Fytanidis D, et al. "PythonFOAM: In-situ data analyses with OpenFOAM and Python", arXiv:2103.09389, 2021. — Python-OpenFOAM接口，HPC可扩展性
[6] Guan Y, Subel A, et al. "Learning physics-constrained SGS closures in small-data regime", arXiv:2201.07347, 2022. — 物理约束SGS闭合，小数据训练
