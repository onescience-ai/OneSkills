# CMIP6 温度—降水区域气候统计降尺度

## 适用范围

**触发条件**：用户需要将 CMIP6 全球气候模型(GCM)输出降尺度到区域/本地尺度，生成高分辨率温度和降水气候投影。

**适用场景**：
- 区域气候变化影响评估
- 极端气候事件（高温、强降水）的区域投影
- 气候服务产品开发（如 CMIP6-MedPlus 数据集）
- 气候适应策略制定需要本地化气候信息

**不适用场景**：
- 需要动力降尺度（如嵌套区域气候模型 WRF）
- 需要实时天气预报（应使用数值天气预报模型）
- 需要大气成分或海洋动力学过程模拟

## 输入

- **CMIP6 GCM 输出**：NetCDF 格式的日/月尺度温度(tas)、降水(pr)等变量
- **观测/再分析数据**：用于训练降尺度模型的参考数据（如 ERA5、CERRA、站点观测）
- **地理信息**：目标区域边界、地形数据（DEM）
- **时间范围**：历史期（通常 1985-2014）和未来情景期（SSP1-2.6, SSP2-4.5, SSP5-8.5 等）

## 输出

- **降尺度后的气候投影**：高分辨率（如 0.25°）的温度和降水日/月数据
- **不确定性度量**：模型间变率、降尺度方法引入的不确定性
- **验证报告**：历史期模拟与观测的对比统计指标

## 流程节点

### 节点 1：GCM 模型选择与评估
- **操作**：从 CMIP6 候选模型中选择表现较好的 GCM 子集
- **参数**：历史期模拟技能评分（温度、降水的偏差、相关系数）
- **质量门禁**：排除历史期偏差过大的 GCM（如降水偏差 > 50%）

### 节点 2：数据预处理
- **操作**：格式统一、时间对齐、空间裁剪、缺失值处理
- **参数**：目标分辨率、时间频率（日/月）
- **工具**：xarray, CDO, NCO
- **质量门禁**：检查数据完整性、时间连续性

### 节点 3：降尺度模型训练
- **操作**：在历史期建立 GCM 输出与观测之间的统计关系
- **方法选择**：
  - **经验分位数映射 (EQM)**：校正 GCM 输出的累积分布函数 [Fedele et al., 2025]
  - **经验统计降尺度 (ESD)**：建立 GCM 大尺度变量与本地观测的回归关系 [Chen et al., 2024]
  - **深度学习降尺度**：使用 CNN/Transformer 学习空间-时间降尺度映射 [Ansari & Ansari, 2024]
  - **机器学习框架**：时空统计降尺度框架，如 MOIRAI 项目 [Varotsos et al., 2026]
- **参数**：训练期长度（通常 20-30 年）、预测变量选择
- **质量门禁**：交叉验证、独立时段验证

### 节点 4：降尺度应用与偏差校正
- **操作**：将训练好的模型应用于 GCM 未来情景输出
- **参数**：偏差校正方法（线性、分位数映射、 delta 方法）
- **质量门禁**：检查降尺度后统计量（均值、方差、极值）是否合理

### 节点 5：不确定性分析
- **操作**：量化不同来源的不确定性
- **方法**：方差分解（GCM 间变率 vs 降尺度方法 vs 情景不确定性）[Lafferty & Sriver, 2023]
- **质量门禁**：不确定性范围是否覆盖观测变率

### 节点 6：结果验证与发布
- **操作**：独立观测验证、极端事件再现能力评估
- **参数**：RMSE、相关系数、bias、极端指数（如 Rx1day, TXx）
- **质量门禁**：历史期验证通过率 > 80%

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 目标分辨率 | 0.25° | [Fedele et al., 2025] | CMIP6-MedPlus 数据集标准分辨率 |
| 训练期长度 | 20-30 年 | [Chen et al., 2024] | 平衡统计稳定性和数据可用性 |
| EQM 分位数箱数 | 100-200 | [Fedele et al., 2025] | 平衡分布拟合精度和样本量 |
| 历史基准期 | 1985-2014 | [Fedele et al., 2025] | IPCC AR6 标准气候态参考期 |
| 极端事件阈值 | 百分位数 | [Jerez et al., 2024] | 超越概率方法定义极端事件 |
| GCM 最小数量 | 5-9 个 | [Fedele et al., 2025] | 平衡计算成本和不确定性覆盖 |

## 边界与分流

- **GCM 选择策略**：当候选 GCM 过多时，优先选择 CMIP6 历史期表现好的子集；当 GCM 过少时（< 3），降低统计显著性要求
- **降尺度方法选择**：数据充足时优先 EQM（物理意义明确）；数据稀缺时考虑 ESD 或深度学习（需要正则化）
- **极端事件处理**：常规统计降尺度可能低估极端事件，需结合极值理论或深度学习方法
- **计算资源约束**：大规模降尺度任务（如多 GCM × 多情景 × 高分辨率）需要 HPC 环境支持

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| 历史期温度 bias | < 1°C | 检查训练期选择，重新校正 |
| 历史期降水 bias | < 20% | 检查降水分布拟合，调整分位数箱 |
| 时间相关系数 | > 0.8 | 检查预测变量选择 |
| 极端事件再现 | 通过 KS 检验 (p>0.05) | 增加训练样本或改用极值方法 |
| 空间一致性 | 变异系数合理 | 检查地形效应，考虑空间降尺度 |

## 回退策略

1. **降尺度失败**：回退到简单的偏差校正方法（如线性缩放）
2. **GCM 不可用**：使用替代 GCM 或多模式集合均值
3. **观测数据缺失**：使用再分析数据（ERA5）作为替代
4. **极端事件再现差**：结合统计降尺度与极值理论（如 GEV 拟合）

## 资源召回建议

- **召回时机**：执行 CMIP6 区域气候投影、气候影响评估、气候服务开发时
- **配套资源**：
  - `climate-hpc-remote-computing-environment`：HPC 环境配置与 SLURM 作业调度知识
  - `climate-climate-data-processing`：气候数据处理管线知识
  - `climate-extreme-event-analysis`：极端气候事件分析方法

## 证据来源

[1] Fedele G, Reder A, Mercogliano P. Statistical Downscaling over Italy using EQM: CMIP6 Climate Projections for the 1985-2100 Period. *Scientific Data*, 2025. DOI: 10.1038/s41597-025-05270-8
[2] Todaro V, Secci D, D'Oria M. CMIP6-MedPlus dataset: climate projections for the Mediterranean region using statistical downscaling. *Earth System Science Data*, 2026. DOI: 10.5194/essd-2026-337
[3] Jerez C, Lagos-Zuñiga M, Montserrat S. Evaluating CMIP6 models under different statistical downscaling methods for climate assessments in the north of Chile. *EGUsphere*, 2024. DOI: 10.5194/egusphere-egu24-12446
[4] Lafferty DC, Sriver RL. Downscaling and bias-correction contribute considerable uncertainty to local climate projections in CMIP6. *Earth and Space Science*, 2023. DOI: 10.22541/essoar.168286894.44910061/v1
[5] Varotsos KV, She J, Hilt ME. A machine-learning framework for spatio-temporal statistical downscaling of CMIP6 climate projections. *EMS Annual Meeting Abstracts*, 2026. DOI: 10.5194/ems2026-643
[6] Chen CT, Tung YS, Wang CY. Future Climate Change in Taiwan Using CMIP6 Empirical-Statistical Downscaling. *ESSOAr*, 2024. DOI: 10.22541/essoar.173325198.81911088/v1
[7] Ansari D, Ansari T. Deep Learning for Climate Downscaling: Generating high-resolution gridded temperature projections over India from low-resolution CMIP6 data. *ESSOAr*, 2024. DOI: 10.22541/essoar.171319464.47617328/v1