# 气候4R框架与downscaleR.keras包

## 适用范围

用于将粗分辨率气候模式输出（如全球气候模式 GCM 或区域气候模式 RCM 的日/月尺度变量）统计降尺度到高分辨率格点场。典型触发条件包括：需要将 CMIP5/6 集合预报降尺度到观测站点或高分辨率格网、需要构建基于 CNN 的多变量非线性降尺度模型、需要在一个可复现的框架中完成从数据获取到模型验证的完整流程。

该框架同时支持多种经典统计降尺度方法（如 BCSD、MOS、analog methods），而 downscaleR.keras 子包专门提供基于 Keras/TensorFlow 的深度学习降尺度能力。当任务涉及空间特征提取、多通道输入（多个预报变量）或需要端到端的训练-预测-评估管线时，该子包尤为适用。

## 输入

- **必需**：
  - 目标区域的气候预测变量（predictor），通常为多个气象场的时间序列（如海平面气压、位势高度、比湿等），以多通道方式组织
  - 观测格点数据（predictand），作为训练标签（如 E-OBS 降水或温度格点场）
  - 实验分组与时间范围定义（训练期、验证期、测试期）
  - 空间域范围（经度、纬度边界）
  
- **可选**：
  - 第三方数据集路径或远程访问凭证（用于自动拉取 ERA-Interim、CMIP5 等数据）
  - 额外的后处理参数（如偏差校正选项）
  - 批量处理配置（用于集合成员批量降尺度）

输入数据需要满足 climate4R 统一的数据结构要求，通常为列表对象，包含逐格点的时间序列值、坐标信息和时间属性。downscaleR.keras 内部会自动处理数据的归一化和维度排列。

## 输出

- 降尺度后的逐格点气候变量时间序列
- 训练好的 Keras 模型对象（可保存为 HDF5 或 RDS 格式用于后续推理）
- 模型评估统计指标（如 RMSE、相关系数、偏差等）
- 可视化诊断图（可选，依赖绘图函数）

## 流程节点

data access → preprocessing → train/test split → model building → training → prediction → validation。

各节点简要说明：

1. **data access**：使用 climate4R 的 `loadGridData()` 或 `storeDP()` 等函数从远程服务器拉取气候数据，或读取本地已下载的 NetCDF/GRIB 文件。数据自动以统一的列表格式返回。

2. **preprocessing**：调用 `gridReshape()`、`stdGrid()` 等函数进行空间裁剪、时间切片、重采样和标准化。downscaleR.keras 要求输入数据的网格分辨率在训练期和预测期保持一致。

3. **train/test split**：使用 `dataSplit()` 将数据划分为训练集、验证集和测试集，确保时间或空间上不重叠。

4. **model building**：通过 `downscaleTrain.keras()` 构建 CNN 架构。典型的卷积结构包括输入层连接多层卷积（如三层卷积，通道数递减），使用 3×3 空间卷积核，后接全连接层输出逐格点预测值。具体架构参数需根据预报变量数量、目标分辨率和可用训练样本量进行调整。

5. **training**：调用训练函数，传入训练数据和超参数（epochs、batch size、优化器、学习率等）。训练过程中监控验证集损失，可设置早停（early stopping）防止过拟合。

6. **prediction**：使用 `downscalePredict.keras()` 对测试期或未来情景的粗分辨率输入进行推理，输出高分辨率格点场。

7. **validation**：通过 `valueGrid()` 或 `value()` 函数计算预测值与观测值的统计指标，生成评估报告。

## 边界与分流

- **输入变量数量极少（仅 1 个预报变量）时**：CNN 的空间特征提取优势可能不明显，可考虑使用更简单的全连接网络或多层感知机（MLP），此时仍可借助 downscaleR.keras 的接口实现，但应简化卷积层深度。

- **目标变量为极值事件（如强降水阈值）时**：连续值 CNN 直接输出可能不够准确，需结合后处理或改用分类-回归混合策略。

- **需要动力降尺度（如嵌套高分辨率 RCM）时**：本工具属于统计降尺度范畴，无法替代动力方法；两者可互为补充。

- **单变量降尺度且数据量有限时**：可回退到经典统计方法（如 BCSD、MOS），这些方法在 climate4R 的 downscaleR 主包中已有实现。

- **上下游衔接**：降尺度结果可直接输入到后续的气候影响评估流程（如作物模型、水文模型），也可与 climate4R.value 包配合进行更全面的极端事件指标计算。

## 质量检查

- 检查输入数据的时间覆盖范围和缺失值比例，缺失率超过一定阈值（如 10%）时需评估其对训练的影响
- 对比降尺度结果与观测场的空间分布图和时间序列，目视检查是否存在明显的系统性偏差
- 计算测试集上的关键统计指标：均方根误差（RMSE）、Pearson 相关系数、偏差（bias）、Nash-Sutcliffe 效率系数等
- 检查模型在极端值区间的表现，因为 CNN 在均值附近的预测通常优于极端事件的捕获
- 保存训练日志（loss 曲线），确认模型是否收敛、是否出现过拟合迹象

## 回退策略

- **远程数据访问失败**：可切换为本地数据路径，手动下载 NetCDF 文件后通过 `loadGridData()` 指定文件路径读取
- **Keras/TensorFlow 环境配置问题**：检查 R 与 Python 的接口连接（reticulate 包），确认 TensorFlow 后端版本兼容；必要时降级至稳定版本
- **输入维度不匹配**：使用 `makeStandGrid()` 重新对齐预报变量与观测变量的时空维度
- **训练不收敛**：降低学习率、增加正则化（如 dropout）、减少网络深度，或改用经典统计方法作为基线对比
- **计算资源不足**：减小 batch size、使用 CPU-only 模式，或在云平台（如 Google Colab）上运行 Python 原生 Keras 代码

## 资源召回建议

- **climate4R 主框架**：https://github.com/SantanderMeteorologyGroup/climate4R — 提供完整的数据访问、预处理和多方法降尺度工具链
- **downscaleR.keras 子包**：https://github.com/SantanderMeteorologyGroup/downscaleR.keras — 本工具的核心仓库，包含 API 文档和示例
- **Keras 官方文档**：https://keras.io/ — 用于理解底层 CNN 架构设计和超参数调优
- **TensorFlow 后端**：https://www.tensorflow.org/ — 确保 R 环境中的 Python 后端正确安装
- **E-OBS 数据集**：https://www.knmi.nl/research-and-climate-data/datasets/daily-european-gridded-temperature-and-precipitation-data — 常用的欧洲高分辨率观测格点数据
- **CMIP 数据门户**：https://esgf-node.llnl.gov/projects/cmip5/ — 获取 GCM 输出数据
