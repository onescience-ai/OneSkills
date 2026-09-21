# 雷达QPE输入数据来源约束与核验

## 适用范围

雷达定量降水估计（QPE）任务要求使用真实观测数据而非模拟数据。本卡描述QPE任务中输入数据的来源约束、格式要求、质量标准与核验流程，适用于以天气雷达体扫数据和雨量计数据为输入的QPE业务与研究场景。不适用于纯模拟数据的算法开发单元测试场景。

## 输入

- **雷达体扫数据**：真实业务雷达站的体积扫描数据，格式包括CAPPI（恒定高度平面位置显示）、PPI（平面位置显示）或原始体积扫描数据。数据应来自已部署的气象雷达网络（如中国CINRAD、美国WSR-88D/NEXRAD、欧洲OPERA等）[1][5]。
- **雨量计数据**：经过质量控制的地面雨量计观测数据，用于Z-R关系校准和QPE验证。数据应来自官方气象观测网络，包含时间序列降水累积值[2][6]。
- **数据元数据**：站点编号、扫描时间、仰角信息、数据格式版本、坐标系统信息[5]。

## 输出

- 输入数据核验报告：包含数据来源路径、哈希值、元数据完整性检查结果、数据覆盖时段和空间范围确认。
- execution-manifest.json 中s01阶段应记录真实数据路径和来源信息，而非模拟数据生成记录。

## 流程节点

1. **数据源识别** → 确定目标区域可用的雷达网络和雨量计网络
2. **数据获取** → 通过官方API或数据下载协议获取真实数据
3. **元数据核验** → 检查站点编号、扫描时间、数据格式版本、坐标系统
4. **质量标记** → 记录数据来源路径、文件哈希值、获取时间戳
5. **完整性检查** → 验证数据覆盖所需的时间段和空间范围

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 雷达数据格式 | CAPPI/PPI/体积扫描 | [1] | Subang雷达使用CAPPI格式处理QPE |
| 时间分辨率 | 5 min（典型值） | [2] | 荷兰QPE产品提供5分钟累积 |
| 空间分辨率 | ~1 km²网格 | [2] | 荷兰QPE产品的空间分辨率 |
| 质量控制 | RADVOL-QC系统 | [4] | 包含非气象回波检测与去除 |
| 自适应QC | 神经网络选择最低可用仰角 | [3] | 英国雷达网络的QPE质量控制算法 |

## 边界与分流

- 当目标区域无可用的真实雷达数据时，应在s01阶段明确报告数据来源不可用，不得用模拟数据替代。
- 当雷达数据存在严重质量问题（如大量非气象回波）时，应使用质量控制算法（如RADVOL-QC [4]）预处理后再进入QPE流程。
- 数据获取API不可用时，应记录失败原因并等待用户确认替代方案。

## 质量检查

- execution-manifest.json中s01的artifacts必须包含真实数据路径而非模拟数据生成记录。
- metadata.json中input_data部分必须记录数据来源（站点编号、获取渠道、文件哈希）。
- 数据覆盖时段必须满足后续校准和验证步骤的最低样本量要求。

## 回退策略

- 若真实数据不可获取，应明确标注"数据来源受限"并说明原因，不得默认使用模拟数据。
- 可考虑使用公开数据集（如MRMS、荷兰QPE产品[2]）作为替代数据源。

## 资源召回建议

当任务涉及雷达QPE且输入数据来源未明确时，应召回本卡片以确认数据来源约束。配套资源：radar-qpe-calibration-validation-separation（校准/验证数据划分）、radar-z-r-parameter-selection（Z-R参数选择）。

## 证据来源

[1] SUBANG RADAR CAPPI DATA PROCESSING AND Z-R OPTIMIZATION FOR QUANTITATIVE PRECIPITATION ESTIMATES, Jurnal Teknologi, 2022, DOI: 10.11113/jurnalteknologi.v84.17918
[2] The Dutch real-time gauge-adjusted radar precipitation product, Earth System Science Data, 2025, DOI: 10.5194/essd-17-4715-2025
[3] A Neural-Network Quality Control scheme for improved Quantitative Precipitation Estimation accuracy, J. Atmos. Oceanic Technol., 2021, DOI: 10.1175/jtech-d-20-0120.1
[4] Improvement in algorithms for quality control of weather radar data (RADVOL-QC system), Atmos. Meas. Tech., 2022, DOI: 10.5194/amt-15-261-2022
[5] Required Time Steps for Weather Radar Quantitative Precipitation Estimation, J. Hydrometeorol., 2026, DOI: 10.1175/jhm-d-25-0151.1
[6] Quality-based compositing of weather radar derived precipitation, Meteorol. Appl., 2019, DOI: 10.1002/met.1812
