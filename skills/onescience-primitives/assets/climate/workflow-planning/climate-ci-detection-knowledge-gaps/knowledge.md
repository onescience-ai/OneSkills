# 静止气象卫星驱动的对流初生识别：关键知识缺口补充

## 适用范围

**适用场景**：
- 静止气象卫星（FY-4A/AGRI、Himawari-8/AHI等）驱动的对流初生（CI）检测任务
- 需要补充卫星数据格式、CI概率阈值、机器学习方法、验证协议和质量标志等知识
- 归因报告中识别出知识缺口需要填补的任务

**不适用场景**：
- 非静止卫星数据的处理
- 已具备完整知识体系的成熟CI检测系统
- 实时业务运行系统（本知识适用于开发和验证阶段）

## 输入

**必需输入**：
- 归因报告中的知识缺口描述
- 任务执行中的具体问题和失败原因

**可选输入**：
- 已有的CI检测工作流卡片
- 相关论文和技术文档

## 输出

**输出产物**：
- 知识卡片集合，涵盖5个关键知识领域
- 每个知识卡片包含适用范围、输入输出、关键参数、边界条件等
- 基于权威来源的可追溯证据

**验证标准**：
- 知识内容基于实际检索到的论文证据
- 每条关键事实有证据来源标注
- 符合onescience-primitives的格式规范

## 流程节点

### 节点1：卫星数据格式与获取知识补充
**目的**：补充FY-4A/AGRI、Himawari-8/AHI等静止卫星数据的标准格式、获取渠道和验证协议

**关键知识点**：
1. **数据格式标准**：
   - FY-4A/AGRI：NetCDF4/HDF5格式，时间分辨率15分钟（REGC区域扫描4-6分钟），空间分辨率4km
   - Himawari-8/AHI：NetCDF4/HDF5格式，时间分辨率10分钟，空间分辨率2km
   - 光谱通道：FY-4A/AGRI具有14个通道，包括6个可见光/近红外、2个中波红外、2个水汽、4个长波红外通道 [1]
   - AGRI通道波长：VIS(0.65μm)、SWIR(1.61μm)、MWIR(3.75μm)、WV(6.25/7.1μm)、IR(8.5/10.8/12/13.5μm) [1]

2. **数据获取渠道**：
   - 国家卫星气象中心（NSMC）：FY系列卫星数据，http://satellite.nsmc.org.cn/DataPortal/cn/ [1]
   - JAXA：Himawari系列卫星数据
   - NOAA：GOES系列卫星数据
   - FY-4A数据可从http://data.nsmc.org.cn/portalsite/default.aspx免费下载 [2]

3. **辐射定标性能**：
   - FY-4A/AGRI在VNIR波段存在明显衰减：9.11%总衰减率，4.0%年均衰减率 [5]
   - 与Aqua/MODIS对比，FY-4A/AGRI辐射水平低24.99% [5]
   - 建议使用深对流云（DCC）方法进行交叉定标验证，整体不确定度<5% [5]

4. **验证协议**：
   - 数据完整性检查：时间序列连续性、空间覆盖完整性
   - 辐射定标验证：与地面观测站数据对比或DCC交叉定标
   - 几何定位精度验证：地标匹配检查

**质量门禁**：
- 数据格式符合标准规范
- 时间和空间覆盖满足任务要求
- 辐射定标和几何定位精度达标
- 考虑辐射衰减对长期序列分析的影响

### 节点2：对流初生标签生成与验证知识补充
**目的**：补充对流初生标签的生成方法和独立验证要求

**关键知识点**：
1. **CI定义与标签生成方法**：
   - CI定义：雷达反射率因子首次达到≥35 dBZ的对流单体生成时刻 [1]
   - 雷达回波法：基于雷达反射率因子阈值（≥35 dBZ），最小CS覆盖面积16个网格点（约16 km²）[1]
   - 光学流追踪法：使用光流方法计算CS速度向量，判断是否为新生成的CI [1]
   - CI分类：Developing CI（面积和回波强度在后续30分钟内增强）和Declining CI [1]

2. **独立验证要求**：
   - 验证资料必须独立于训练数据
   - 来自不同传感器（如雷达验证卫星检测结果）、不同时段或不同区域
   - 验证协议需预先登记并严格执行
   - CIDS数据集使用地面气象观测验证CI标签质量 [1]

3. **标签质量控制**：
   - 标签一致性检验：多源数据交叉验证
   - 时间一致性：标签与观测时间匹配（10分钟间隔）[1]
   - 空间一致性：标签与云图特征匹配
   - 异常区域识别：日频率>20%的区域可能存在雷达质量问题 [1]

**质量门禁**：
- 标签生成方法明确且可追溯
- 验证资料独立且协议完整
- 标签质量控制通过一致性检验
- 使用Developing CI作为正样本可提高标签质量 [1]

### 节点3：CI概率阈值选择与校准知识补充
**目的**：补充对流初生概率的典型范围和阈值选择方法

**关键知识点**：
1. **CI概率典型范围**：
   - 通常在0.1-0.8之间，具体取决于区域和季节
   - 热带地区概率较高（0.3-0.8）
   - 中纬度地区概率中等（0.2-0.6）
   - 高纬度地区概率较低（0.1-0.4）

2. **阈值选择方法**：
   - ROC曲线优化：最大化真阳性率与假阳性率的平衡
   - F1-score优化：平衡精确率和召回率
   - 成本敏感分析：考虑漏检和误检的业务成本
   - 自适应阈值：基于数据分布动态调整
   - 固定阈值0.5可能导致零检测（如归因报告中最大概率仅0.360的情况）

3. **概率校准技术**：
   - Platt缩放：将分类器输出转换为概率
   - isotonic回归：非参数概率校准
   - 贝叶斯校准：考虑先验信息的概率校准

4. **多尺度评估**：
   - CSI-1：4km分辨率像素级评估
   - CSI-2：8km分辨率下采样评估
   - CSI-4：16km分辨率下采样评估 [2]

**质量门禁**：
- 阈值选择基于数据统计而非固定值
- 进行了敏感性分析
- 概率校准通过可靠性检验
- 使用多空间尺度评估确保结果稳健性

### 节点4：机器学习在CI检测中的应用知识补充
**目的**：补充机器学习在对流初生检测中的应用方法

**关键知识点**：
1. **常用ML/DL方法**：
   - 卷积神经网络（CNN）：适用于图像特征提取，如PCINet用于降水云识别 [3]
   - UNet：用于雷达反射率重建和对流检测 [2][4]
   - 扩散模型（DDMS）：用于4小时卫星对流临近预报，优于PredRNN-v2和NowcastNet [2]
   - EfficientNet：轻量级网络，适用于小样本数据集，如DAM-EfficientNet用于冰雹检测 [6]
   - 注意力机制（CBAM/ECA）：增强关键特征提取能力 [6]

2. **特征工程最佳实践**：
   - FY-4A卫星特征：9个通道（VIS/SWIR/MWIR/WV/LWIR），10分钟时间分辨率 [1]
   - 雷达特征：10种产品（CR、HBR、CAPPI 2-7km、ET、VIL），0.01°分辨率 [1]
   - 推导特征：6.25–10.8μm亮温差、13.5–10.8μm亮温差趋势 [1]
   - 环境场特征：NWP分析/预报场、地形、日变化 [1]

3. **模型训练流程**：
   - 数据划分：训练集、验证集、测试集（如CIDS数据集2018-2023年数据）[1]
   - 交叉验证：k折交叉验证评估模型性能
   - 超参数调优：网格搜索或贝叶斯优化
   - 模型评估：POD、FAR、CSI、准确率等 [6]
   - DAM-EfficientNet在冰雹检测中达到98.53%准确率、97.92% POD、2.08% FAR [6]

4. **数据集构建**：
   - CIDS数据集：136,728样本，4,159,491个CI，其中1,789,208个Developing CI [1]
   - 时间分辨率：10分钟
   - 空间覆盖：104–125°E，20–40°N [1]

**质量门禁**：
- 模型选择考虑任务复杂度和数据特性
- 特征工程基于物理意义和数据统计
- 模型评估使用独立测试集
- 考虑数据不平衡问题（CI为稀有事件）

### 节点5：验证协议与指标计算知识补充
**目的**：补充独立验证资料的类型和获取方法，以及POD/FAR/CSI等指标的计算方法

**关键知识点**：
1. **独立验证资料类型**：
   - 雷达数据：反射率因子、径向速度（CINRAD S/C波段，122-157部雷达拼图）[1]
   - 地面观测：自动气象站数据（1,008个国家级站点）[1]
   - 探空数据：温度、湿度、风廓线
   - 其他卫星数据：极轨卫星观测、GPM降水产品 [4]

2. **验证协议设计原则**：
   - 独立性：验证资料不参与模型训练
   - 代表性：样本覆盖目标区域和时段（3-9月暖季）[1]
   - 一致性：验证标准与训练标准一致
   - 可追溯性：验证过程可重复

3. **指标计算方法**：
   - POD（检测概率）：TP/(TP+FN)
   - FAR（虚警率）：FP/(TP+FP)
   - CSI（临界成功指数）：TP/(TP+FP+FN) [2]
   - HSS（Heidke技能评分）：考虑随机一致性
   - 多尺度CSI评估：CSI-1(4km)、CSI-2(8km)、CSI-4(16km) [2]

**质量门禁**：
- 验证资料独立且协议完整
- 指标计算正确且样本足够
- 结果可追溯且可重复
- 使用多尺度评估确保结果稳健性

### 节点6：质量标志与不确定性估计知识补充
**目的**：补充质量标志的定义和生成方法，以及不确定性估计的常用技术

**关键知识点**：
1. **质量标志定义**：
   - 数据有效性：观测数据是否有效
   - 缺测状态：数据是否存在缺失
   - 可疑状态：数据质量是否可疑
   - 算法状态：算法执行是否正常

2. **不确定性估计技术**：
   - 观测误差：仪器精度、定标误差（FY-4A/AGRI VNIR波段衰减导致的不确定性）[5]
   - 算法误差：模型误差、参数不确定性
   - 代表性误差：点到面的代表性
   - 抽样误差：样本量不足引起的误差
   - 扩散模型可提供集合预测，自然量化预报不确定性 [2]

3. **产品元数据要求**：
   - 数据来源和版本信息
   - 处理算法和参数配置
   - 质量标志和不确定性信息
   - 使用限制和注意事项

**质量门禁**：
- 质量标志完整且定义明确
- 不确定性估计方法合理
- 产品元数据符合标准要求
- 考虑辐射定标衰减对不确定性的影响

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| CI雷达反射率阈值 | ≥35 dBZ | [1] | 对流初生典型阈值，首次达到此值的对流单体 |
| CI最小CS面积 | 16个网格点（约16 km²） | [1] | 确保每个CS对应至少一个FY-4数据点 |
| CI时间分辨率 | 10分钟 | [1] | CIDS数据集时间分辨率 |
| 雷达拼图空间分辨率 | 0.01° × 0.01° | [1] | 122部雷达最大值拼图 |
| FY-4A/AGRI通道数 | 14个 | [1][5] | 6个VNIR、2个SWIR、2个WV、4个LWIR |
| FY-4A/AGRI时间分辨率 | 15分钟（REGC 4-6分钟） | [1][2] | 全盘扫描vs区域扫描 |
| FY-4A/AGRI空间分辨率 | 2-4km | [1][6] | 通道相关，VNIR最高0.5km |

### 校准数值（来自CIDS/FY-4A体系，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| CIDS数据集规模 | 136,728样本，4,159,491个CI | [1] | 2018-2023年东南中国 |
| Developing CI比例 | 43%（1,789,208个） | [1] | 面积和回波强度增强的CI |
| FY-4A/AGRI辐射衰减率 | 9.11%总衰减，4.0%年均 | [5] | VNIR波段2018-2020年 |
| FY-4A/AGRI相对偏差 | -24.99% | [5] | 相对于Aqua/MODIS |
| DCC定标不确定度 | <5% | [5] | 深对流云交叉定标方法 |
| DAM-EfficientNet准确率 | 98.53% | [6] | 冰雹检测任务 |
| DAM-EfficientNet POD | 97.92% | [6] | 冰雹检测任务 |
| DAM-EfficientNet FAR | 2.08% | [6] | 冰雹检测任务 |
| DAM-EfficientNet CSI | 95.92% | [6] | 冰雹检测任务 |

## 边界与分流

**异常处理**：
- 卫星数据格式不兼容：检查数据标准版本，必要时进行格式转换
- CI概率阈值不合理：基于数据统计重新校准阈值，避免使用固定阈值0.5
- ML模型性能不佳：检查特征工程和超参数配置
- 验证资料不独立：寻找替代验证数据源或调整验证协议
- 质量标志不完整：补充缺失的质量标志字段

**降级策略**：
- 数据格式问题：使用兼容性更好的标准格式
- 阈值选择问题：采用自适应阈值算法或ROC曲线优化
- ML模型问题：使用更简单的模型或集成方法
- 验证问题：明确说明验证限制
- 质量标志问题：提供基础质量标志

**分支条件**：
- 网络检索可用时：优先使用OpenAlex API获取最新论文
- 网络检索不可用时：基于已有知识生成卡片，标注"证据有限"
- 已有相关卡片时：检查是否可以补充而非新建

## 质量检查

**验证点**：
1. 卡片格式符合onescience-primitives规范
2. metadata.json包含所有必需字段
3. knowledge.md包含推荐章节中的至少5个
4. 关键事实有证据来源标注
5. 卡片可被onescience-primitives召回

**阈值**：
- 卡片完整性：100%
- 证据覆盖率：≥80%
- 格式合规性：100%

**失败处理**：
- 格式不合规：重新生成卡片
- 证据不足：如实标注"证据有限"
- 无法召回：检查卡片命名和标签

## 回退策略

**失败时的替代方案**：
1. 网络检索失败：基于已有知识生成卡片
2. 论文获取失败：使用摘要信息
3. 全文解析失败：使用摘要级知识
4. 卡片生成失败：记录失败原因并建议手动补充

**降级处理**：
- 证据不足时标注"证据有限"
- 无法验证时说明限制条件
- 知识不完整时列出已知部分

## 资源召回建议

**何时应召回本卡片**：
- 执行静止气象卫星驱动的对流初生识别任务时
- 需要补充卫星数据格式知识时
- 需要CI概率阈值选择指导时
- 需要ML方法在CI检测中应用指导时
- 需要验证协议设计指导时
- 需要质量标志生成指导时

**配套资源**：
- `geostationary-satellite-convective-initiation-detection`：CI检测工作流卡片
- `climate-satellite-precipitation-validation`：卫星降水验证卡片
- `machine-learning-based-satellite-precipitation-estimation`：ML卫星降水估计卡片

## 补充证据（批次更新 2026-09-16）

[1] Liu Y, Xiong A, Liu N, Li Y, Chen Z. (2026). A dataset for machine learning model to convective initiation detection and nowcasting over southeastern China. Scientific Data, 13, 557. DOI: 10.1038/s41597-026-06902-3

[2] Dai K, Li X, Fang J, et al. (2025). Four-hour thunderstorm nowcasting using a deep diffusion model for satellite data. PNAS, 122(51). DOI: 10.1073/pnas.2517520122

[3] Ma G, Huang J, Zhang Y, et al. (2023). A Deep Learning-Based Algorithm for Identifying Precipitation Clouds Using Fengyun-4A Satellite Observation Data. Sensors, 23(15), 6832. DOI: 10.3390/s23156832

[4] Yang L, Zhao Q, Xue Y, et al. (2022). Radar Composite Reflectivity Reconstruction Based on FY-4A Using Deep Learning. Sensors, 23(1), 81. DOI: 10.3390/s23010081

[5] Zhong B, Ma Y, Yang A, Wu J. (2021). Radiometric Performance Evaluation of FY-4A/AGRI Based on Aqua/MODIS. Sensors, 21(5), 1859. DOI: 10.3390/s21051859

[6] Liu R, Dai H, Chen Y, et al. (2024). A study on the DAM-EfficientNet hail rapid identification algorithm based on FY-4A_AGRI. Scientific Reports, 14, 3505. DOI: 10.1038/s41598-024-54142-5

[7] Mecikalski JR, et al. (2019). A Novel Framework of Detecting Convective Initiation Combining Automated Sampling, Machine Learning, and Repeated Model Tuning from Geostationary Satellite Data. Remote Sensing, 11(12), 1454. DOI: 10.3390/rs11121454

## 证据来源

[1] Liu Y, Xiong A, Liu N, Li Y, Chen Z. (2026). A dataset for machine learning model to convective initiation detection and nowcasting over southeastern China. Scientific Data, 13, 557. DOI: 10.1038/s41597-026-06902-3

[2] Dai K, Li X, Fang J, et al. (2025). Four-hour thunderstorm nowcasting using a deep diffusion model for satellite data. PNAS, 122(51). DOI: 10.1073/pnas.2517520122

[3] Ma G, Huang J, Zhang Y, et al. (2023). A Deep Learning-Based Algorithm for Identifying Precipitation Clouds Using Fengyun-4A Satellite Observation Data. Sensors, 23(15), 6832. DOI: 10.3390/s23156832

[4] Yang L, Zhao Q, Xue Y, et al. (2022). Radar Composite Reflectivity Reconstruction Based on FY-4A Using Deep Learning. Sensors, 23(1), 81. DOI: 10.3390/s23010081

[5] Zhong B, Ma Y, Yang A, Wu J. (2021). Radiometric Performance Evaluation of FY-4A/AGRI Based on Aqua/MODIS. Sensors, 21(5), 1859. DOI: 10.3390/s21051859

[6] Liu R, Dai H, Chen Y, et al. (2024). A study on the DAM-EfficientNet hail rapid identification algorithm based on FY-4A_AGRI. Scientific Reports, 14, 3505. DOI: 10.1038/s41598-024-54142-5

[7] Mecikalski JR, et al. (2019). A Novel Framework of Detecting Convective Initiation Combining Automated Sampling, Machine Learning, and Repeated Model Tuning from Geostationary Satellite Data. Remote Sensing, 11(12), 1454. DOI: 10.3390/rs11121454
