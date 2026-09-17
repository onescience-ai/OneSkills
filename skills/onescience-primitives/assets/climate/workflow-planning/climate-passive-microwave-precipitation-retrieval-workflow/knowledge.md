# 被动微波卫星瞬时降水率反演工作流

## 适用范围

本卡片服务于从多通道被动微波卫星亮温数据反演瞬时降水率的完整工作流，涵盖输入数据预检、预处理对齐、方法配置验证、核心反演计算和独立验证五个阶段。适用场景包括使用GPM GMI、AMSR2、TMI等传感器数据进行降水估计，以及对现有降水产品进行精度评估。不适用于红外或可见光降水估计、气候模式降水输出后处理、以及非降水变量（如土壤湿度、雪深）的反演。

## 输入

- 多通道微波亮温数据（至少6-36 GHz频率范围，含垂直和水平极化）
- 扫描几何参数（经纬度、扫描角、天顶角）
- 环境辅助量（地表类型、地形高度、海表温度、大气状态）
- 目标区域和时段定义（空间范围、时间窗口、最小覆盖率要求）
- 传感器元数据（轨道信息、分辨率、定标系数、质量标志）

## 输出

- 反演后的瞬时降水率场（mm/h）
- 降水识别掩膜（降水/无降水分类）
- 质量控制标志（反演置信度、数据完整性）
- 验证报告（按海陆、强度、天气型分层的性能指标）
- 输入数据与版本清单、任务范围和资料截止时间表

## 流程节点

### s01 输入数据预检

**操作**：核验卫星亮温数据的来源、版本、时空覆盖、变量、单位、质量标志、使用权限和资料截止时间

**参数**：
- 数据来源：NASA GES DISC、JAXA、EUMETSAT等官方数据中心
- 数据版本：Level-1C或Level-1B格式
- 时空覆盖：确保数据覆盖目标区域和时段
- 质量标志：检查数据质量标志，排除异常或缺失数据

**质量门禁**：
- 所有必需输入均存在且路径、版本和来源可追溯
- 时空覆盖满足目标区域和时段要求
- 输出输入数据与版本清单、任务范围和资料截止时间表

**证据**：[1][2][4]

### s02 预处理对齐

**操作**：执行辐射定标配置（亮温值校正）、几何配准配置（经纬度投影变换）和切片配置（时空子集提取）

**参数**：
- 辐射定标：应用传感器特定的定标系数，校正亮温值
- 几何配准：将卫星扫描几何投影到统一的地理坐标系
- 时空对齐：确保多通道数据在时间和空间上一致
- 质量掩膜：应用缺测处理和质量控制掩膜

**质量门禁**：
- 预处理后的时间轴、坐标、单位和形状可检查
- 多通道亮温、扫描几何和环境辅助量在时间、空间、单位和质量标志上一致
- 输出对齐后的标准输入、掩膜与样本索引和预处理转换记录

**证据**：[11][18]

### s03 方法配置验证

**操作**：冻结方法配置，执行最小干运行验证输入输出契约

**参数**：
- 方法工件：确定反演算法版本和依赖关系
- 方法配置：冻结算法参数（如阈值、系数、模型权重）
- 随机种子：确保结果可复现
- 最小干运行：使用小样本数据执行完整流程

**质量门禁**：
- 方法工件、配置和运行环境属于兼容版本
- 最小干运行正常退出且结果不存在NaN或Inf
- 目标变量和输出结构与任务定义一致
- 输出方法工件与配置身份报告、输入输出兼容性矩阵和最小干运行日志

**证据**：[12][17]

### s04 核心反演计算

**操作**：先识别降水，再反演雨雪率

**降水识别阶段**：
- 多通道特征提取：亮温梯度、极化差、频率差
- 海陆区分：海洋和陆地采用不同的识别阈值
- 降水类型判别：层状云、对流云、混合云

**降水率反演阶段**：
- 物理反演：基于辐射传输方程的迭代反演
- 统计反演：多元回归、查找表、神经网络
- 机器学习反演：深度神经网络、随机森林、支持向量机

**参数**：
- 海洋反演：利用低频通道（6-10 GHz）的发射率差异
- 陆地反演：利用高频通道（37-85 GHz）的散射信号
- 雨雪区分：利用频率依赖的散射特性差异

**质量门禁**：
- 反演算法基于被动微波辐射传输原理
- 考虑云、降水、地表的微波辐射特性
- 区分降水识别和降水率估计两个阶段
- 针对不同地表类型（海、陆）采用不同的反演策略
- 输出反演结果和质量控制标志

**证据**：[6][12][17][18]

### s06 独立验证

**操作**：使用独立验证资料进行分层验证

**验证资料来源**：
- 地面雨量站网络（如GHCN、DWD、JMA）
- 地基雷达数据（如NEXRAD、CASAREO）
- 其他卫星产品（如TRMM、GPM-IMERG、CMORPH）
- 原位观测（如船舶、浮标）

**分层维度**：
- 海陆：海洋和陆地分开验证
- 弱度：小雨（<1 mm/h）、中雨（1-10 mm/h）、大雨（>10 mm/h）
- 天气型：层状云、对流云、锋面降水
- 传感器：不同卫星传感器分开验证

**验证指标**：
- 连续指标：RMSE、MAE、相关系数（R）、偏差（Bias）
- 分类指标：POD（检测概率）、FAR（虚报率）、CSI（临界成功指数）
- 业务门限：RMSE ≤ 2.5 mm/h，R ≥ 0.75，总体精度 ≥ 70%

**质量门禁**：
- 独立验证资料独立于算法开发数据
- 按海陆、强度、天气型和传感器进行分层验证
- 计算规定的验证指标并与业务门限比较
- 输出验证报告和性能诊断

**证据**：[4][9][10]

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 频率范围 | 6-189 GHz | [1][2] | 覆盖发射和散射信号敏感区 |
| 极化方式 | 垂直+水平 | [1][11] | 利用极化差信息 |
| 空间分辨率 | 5-25 km | [1][4] | 取决于频率和传感器 |
| 时间分辨率 | 0.5-3小时 | [1][2] | 取决于轨道类型 |
| 降水识别阈值 | 海洋: 亮温差>10K; 陆地: 37GHz亮温<275K | [6][12] | 经验阈值，需根据传感器调整 |
| 反演算法类型 | 物理/统计/机器学习 | [12][17] | 根据数据条件和精度要求选择 |
| 验证资料独立性 | 未参与训练、参数选择或阈值调优 | [4][9] | 确保评估的客观性 |

### 校准数值（以下数值来自GPM GMI体系，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| GMI通道数 | 13 | [1][6] | 10.65-183 GHz |
| GMI空间分辨率 | 5-20 km | [1] | 取决于频率 |
| 业务RMSE门限 | ≤ 2.5 mm/h | [9] | 对地面观测的误差容限 |
| 业务相关系数门限 | ≥ 0.75 | [9] | 表示算法有效性的最低要求 |
| 业务精度门限 | ≥ 70% | [9] | 总体估计精度 |

## 边界与分流

- **无真实卫星数据**：若无法获取真实卫星亮温数据，应报告数据缺失并寻求确认，不得使用模拟数据替代
- **数据质量不达标**：若输入数据质量标志异常或缺失严重，应降级为摘要级分析或拒绝处理
- **方法配置不兼容**：若方法工件与运行环境不兼容，应暂停执行并报告配置问题
- **性能未达门限**：若验证指标未达业务门限，应进行误差分析、分层分析和敏感性分析，识别性能瓶颈后优化算法
- **传感器不支持**：若目标传感器不在已知算法支持范围内，应先验证算法适用性或开发适配模块

## 质量检查

- 输入数据完整性：所有必需变量存在、路径可访问、版本明确
- 预处理一致性：多通道数据时间轴、坐标、单位和形状一致
- 方法配置有效性：最小干运行正常退出、无NaN/Inf
- 反演结果物理合理性：降水率值域合理、空间分布连续、与亮温特征一致
- 验证指标达标：RMSE、R、POD、FAR、CSI等达到业务门限
- 文档完整性：输入数据清单、预处理记录、方法配置、验证报告齐全

## 回退策略

- 全文抓取失败时：使用摘要级证据进行知识抽取，标注证据等级为"摘要级"
- 独立验证资料不可用时：使用交叉验证或留出法作为替代方案
- 算法性能严重不足时：回退到已验证的基准算法，再逐步优化
- 数据源不可访问时：记录阻塞原因，等待数据可用后重新执行

## 资源召回建议

本卡片应在以下场景被召回：
- 用户需要从被动微波卫星数据反演降水率
- 用户需要评估卫星降水产品的精度
- 用户需要设计降水反演算法的验证方案
- 用户需要了解GPM、AMSR2、TMI等传感器的降水反演能力

配套资源：
- 气象领域原语（如辐射传输模型、大气廓线数据）
- 数据处理组件（如亮温预处理、几何配准工具）
- 可视化规范（如降水场制图、验证散点图）

## 证据来源

[1] The Global Precipitation Measurement (GPM) Mission for Science and Society, Hou et al., Bulletin of the American Meteorological Society, 2016, DOI: 10.1175/BAMS-D-15-00254.1
[2] A Review of Global Precipitation Data Sets: Data Sources, Estimation, and Intercomparison, Sun et al., Reviews of Geophysics, 2017, DOI: 10.1002/2017RG000574
[3] Constructing a Multifrequency Passive Microwave Hail Retrieval and Climatology, Smith et al., Journal of Applied Meteorology and Climatology, 2019, DOI: 10.1175/JAMC-D-18-0188.1
[4] Assessment of GPM-IMERG and Other Precipitation Products against Gauge Data, Tang et al., Remote Sensing, 2016, DOI: 10.3390/rs8070534
[5] Satellite Estimation of Falling Snow: A GPM Constellation Study, Kulie et al., Journal of Applied Meteorology and Climatology, 2019, DOI: 10.1175/JAMC-D-18-0136.1
[6] Microphysical properties of frozen particles inferred from GPM Microwave Imager, Olson et al., Atmospheric Chemistry and Physics, 2017, DOI: 10.5194/acp-17-9149-2017
[7] Exploring Deep Neural Networks to Retrieve Rain and Snow in High Latitudes, Paloscia et al., Water Resources Research, 2018, DOI: 10.1029/2018WR023934
[8] A Review of Merged High-Resolution Satellite Precipitation Product Accuracy, Prakash et al., Journal of Hydrometeorology, 2016, DOI: 10.1175/JHM-D-15-0211.1
[9] Evaluation of GPM-era Global Satellite Precipitation Products over Multiple Climates, Vergara et al., Remote Sensing, 2019, DOI: 10.3390/rs11141688
[10] Global Precipitation Estimates from Cross-Track Passive Microwave Observations, Ferraro et al., Journal of Hydrometeorology, 2015, DOI: 10.1175/JHM-D-14-0200.1
[11] The Passive Microwave Neural Network Precipitation Retrieval (PNPR) Algorithm, Amorati et al., Remote Sensing, 2018, DOI: 10.3390/rs10071143
[12] A 1DVAR retrieval applied to GMI: Algorithm description, validation, and sensitivity, Gao et al., Journal of Geophysical Research: Atmospheres, 2016, DOI: 10.1029/2016JD025196
[13] Validation of the New Algorithm for Rain Rate Retrieval from AMSR2 Data Using TMI, Ushio et al., Advances in Meteorology, 2015, DOI: 10.1155/2015/169528