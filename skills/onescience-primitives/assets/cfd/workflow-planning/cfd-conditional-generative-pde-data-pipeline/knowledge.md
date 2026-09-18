# 条件生成模型多物理PDE数据接入与预处理全流程

## 适用范围

面向条件生成模型（CVAE、扩散模型等）在多物理PDE场量预测任务中，从数据源接入到模型训练前的完整数据准备流程。适用于扩散-反应方程、Navier-Stokes方程等多物理PDE数据集的标准化接入与质量保障。不适用于纯图像生成或非PDE时间序列任务。

## 输入

- PDEBench或其他公开PDE数据集（HDF5或NetCDF格式）
- 数据契约定义文件（JSON格式，规定字段、单位、坐标）
- 目标物理量说明（浓度场、温度场、速度场等）

## 输出

- 标准化数据集（训练集/验证集/测试集，无泄漏切分）
- 数据契约文件（dataset_contract.json）
- 归一化统计量文件（normalization.json，含mean、std、min、max）
- 数据审计报告（data_audit.md，含所有质量检查项结果）

## 流程节点

### 1. 数据源接入
- **操作**：从PDEBench下载HDF5文件，或从CFD求解器导出NetCDF
- **参数**：file_format=hdf5/netcdf, grid_resolution=64x64, n_samples>=100
- **工具**：h5py/netCDF4 Python库
- **质量门禁**：文件可读性检查、数据维度匹配、变量名与契约一致

### 2. 数据契约定义
- **操作**：定义input_fields、target_fields、units、coordinates字段
- **参数**：input_fields=["u", "v", "p"], target_fields=["u_next", "v_next"], units=["m/s", "m/s", "Pa"]
- **工具**：JSON schema验证
- **质量门禁**：所有必需字段存在、单位格式一致（SI制）、坐标维度与网格匹配

### 3. 归一化
- **操作**：对场量进行z-score归一化
- **参数**：method=z-score, clip_range=[-5, 5]
- **工具**：NumPy/PyTorch统计函数
- **质量门禁**：归一化后mean≈0, std≈1；无NaN/Inf值；数值范围在合理物理量级内

### 4. 数据审计
- **操作**：执行完整审计检查清单
- **参数**：检查项包括缺失值、单位一致性、坐标有效性、数据泄漏
- **工具**：自定义审计脚本
- **质量门禁**：所有检查项PASS，无NOT_VALID_FOR_SCIENTIFIC_CONCLUSIONS标记

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| z-score归一化后mean | ≈0 | [论文1] | PDE解空间数据归一化后的标准分布特征 |
| z-score归一化后std | ≈1 | [论文1] | 确保各物理量量级一致 |
| 数据泄漏检测 | train/val/test无重叠 | [论文2] | 按时间步或工况切分，避免未来信息泄露 |
| 数值范围检查 | 无NaN/Inf | [论文3] | 合成数据生成时需控制数值稳定性 |

### 校准数值（扩散-反应PDE体系）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 浓度场典型量级 | 0-10 | 常识 | 扩散-反应PDE中浓度场的物理合理范围 |
| 温度场典型量级 | 300-1000K | 常识 | 热传导相关PDE的温度范围 |
| Forward Euler时间步长 | ≤0.01s | 常识 | 显式求解器的稳定性条件（CFL条件） |
| 网格分辨率 | 64x64或128x128 | [论文2] | PDEBench标准分辨率 |

## 边界与分流

- **HDF5文件损坏**：尝试重新下载；若PDEBench不可用，改用NetCDF格式或其他PDE数据源
- **归一化统计量异常**（mean>10^6或std>10^6）：检查原始数据生成脚本的时间步长和扩散系数设置，修正后重新生成
- **数据泄漏**：按时间步切分数据时，确保训练集只包含t<T_val的数据，验证集包含t≥T_val的数据
- **物理量纲不一致**：检查units字段是否统一为SI制，必要时进行量纲转换

## 质量检查

- [ ] dataset_manifest.json中data_type为real（非synthetic_generated）
- [ ] normalization.json中mean和std在合理量级（|mean|<100, std<100）
- [ ] data_audit.md中所有检查项为PASS
- [ ] 无"NOT_VALID_FOR_SCIENTIFIC_CONCLUSIONS"标记
- [ ] 训练集/验证集/测试集无样本重叠
- [ ] 所有场量无负值（若物理约束要求non-negative）

## 回退策略

- 若PDEBench数据不可用，可使用LAMMPS/GROMACS等分子动力学模拟数据作为替代
- 若HDF5解析失败，尝试scipy.io.loadmat或pickle格式
- 若归一化后仍存在异常值，改用分位数归一化或RobustScaler

## 资源召回建议

- 本卡片适用于多物理PDE条件生成模型任务的数据准备阶段
- 配套资源：cfd-boundary-embedded-neural-operator-data-intake-contract-validation（数据接入与契约核验详细流程）
- 配套资源：cfd-boundary-embedded-neural-operator-preprocessing-data-splitting（预处理与切分详细流程）

## 补充证据（开源文档/用户自有，可选）

PDEBench官方文档（https://github.com/pdebench/PDEBench）提供了HDF5文件格式规范和数据集列表，作为数据源接入的权威参考。

## 证据来源

[1] Glyn-Davies A, Vadeboncoeur A, Akyildiz OD, Kazlauskaite I, Girolami M. "A primer on variational inference for physics-informed deep generative models", Phil. Trans. R. Soc. A, 2025, DOI: 10.1098/rsta.2024.0324

[2] Li et al. "Regime-adaptive partial differential equations for interpretable multi-ethnic population dynamics", Scientific Reports, 2025, DOI: 10.1038/s41598-025-26832-1

[3] "Energy-Consistent Neural Networks with Fenchel-Young Loss for Physics-Informed Prediction of Sheet Metal Forming", Materials, 2026, DOI: 10.3390/ma19081571
