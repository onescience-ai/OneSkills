# Porous Material Model Validation with GCMC

## 适用范围
面向多孔材料性质预测模型的独立验证任务，使用Grand-Canonical Monte Carlo (GCMC) 高保真模拟或实验吸附数据作为基准，验证机器学习/GNN模型的预测准确性。适用于任何需要独立验证数据的多孔材料建模任务；不适用于不需要独立验证的探索性分析。

## 输入
- 待验证的模型预测结果（吸附等温线、选择性、容量等）
- 独立验证数据源（GCMC模拟结果、实验测量数据）
- 验证指标定义（RMSE、MARD、R²、相关系数等）
- 验证协议（数据分割、交叉验证、外部验证集）

## 输出
- 验证报告（模型预测 vs 独立基准的对比分析）
- 验证指标计算结果
- 偏差分析与误差来源识别
- 模型适用性评估

## 流程节点
1. **验证数据获取** → 从公开数据库或文献获取GCMC/实验数据
2. **数据对齐** → 确保验证数据与模型输入使用相同的结构表示和力场
3. **指标计算** → 计算模型预测与基准的偏差指标
4. **偏差分析** → 分析偏差来源（力场误差、结构差异、采样不足等）
5. **适用性评估** → 基于验证结果评估模型在目标任务上的适用性

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| GCMC模拟精度 | MARD <10% | [1] | 与实验数据的平均相对偏差 |
| 结构表示 | UFF力场 | [1] | 原子间相互作用的力场描述 |
| 吸附质模型 | TraPPE-UA | [1] | 吸附分子的力场模型 |
| 截断距离 | 14 Å | [1] | Lennard-Jones相互作用截断 |
| 初始化周期 | 20000 | [1] | GCMC模拟的初始化周期数 |
| 生产周期 | 100000 | [1] | GCMC模拟的生产周期数 |
| 孔径计算 | Zeo++ | [1] | 使用100个Monte Carlo样本 |
| 验证指标 | Pearson r, MARD, R² | [1] | 统计验证指标 |
| 可接受阈值 | r > 0.9, MARD <20% | [1] | 模型验证通过的最低标准 |

## 边界与分流
- **验证数据不可得**：使用交叉验证或留出法作为替代，但标注为内部验证
- **GCMC模拟计算量大**：使用cDFT作为快速替代（计算速度提升2-4个数量级，精度损失<10%）
- **实验数据与模拟数据冲突**：以实验数据为准，记录冲突待裁决
- **模型偏差超出阈值**：分析偏差来源，考虑修正模型或重新训练
- **多个验证指标矛盾**：根据任务需求选择主指标（如工业筛选优先关注排名一致性）

## 质量检查
- 验证数据是否与模型使用相同的结构表示
- 验证指标是否覆盖了任务关注的所有KPI
- 偏差分析是否识别了主要误差来源
- 模型适用性评估是否给出了明确结论
- 验证报告是否包含独立数据来源信息

## 回退策略
- 如果GCMC数据不可用：使用cDFT（快速但精度稍低）或实验文献数据
- 如果所有验证数据均不可得：标注为"待验证"，不强行给出验证结论
- 如果验证失败：分析原因，提出改进建议

## 资源召回建议
- 需要召回本卡片的场景：用户提到"GCMC""验证""吸附等温线""基准测试""独立验证"等关键词
- 配套资源：matchem/tasks/porous-material-gnn-foundation-model-selection（模型选择）、matchem/tasks/porous-material-database-sourcing（数据获取）

## 证据来源
[1] Schnieders MJ, et al. "Fast process-level screening of metal-organic frameworks for adsorption-based gas separation." Digital Discovery, 2025. DOI: 10.1039/d6me00066e（全文级证据：GCMC模拟参数、验证协议、cDFT vs GCMC对比验证流程）
[2] GCMC for NU-2100 authors. "Analyzing the gas storage capacities of NU-2100 MOF via GCMC simulations: a materials informatics approach." Adsorption, 2025. DOI: 10.1007/s10450-025-00641-4
[3] GCMC pore distribution authors. "GCMC kernel for analyzing the pore size distribution of porous carbons." Adsorption, 2023. DOI: 10.1007/s10450-023-00418-7
[4] GCMC-MD shale gas authors. "GCMC-MD prediction of adsorption and diffusion behavior of shale gas in nanopores." Fuel, 2024. DOI: 10.1016/j.fuel.2024.133052
[5] DSLM from GCMC authors. "Modified Dual-Site Langmuir Adsorption Equilibrium Models from A GCMC Molecular Simulation." Applied Sciences, 2020. DOI: 10.3390/app10175979
