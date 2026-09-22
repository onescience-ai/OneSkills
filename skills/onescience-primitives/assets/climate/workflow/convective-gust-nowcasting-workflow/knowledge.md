# 对流阵风临近预报标准工作流

## 适用范围
适用于基于天气雷达数据的对流阵风（Convective Gust）临近预报任务，涵盖从数据获取、预处理、方法配置、模型推理到独立验证的完整流程。

## 流程节点

### s01 数据获取
- **操作**：获取雷达反射率数据和辅助气象数据（ERA5、地面观测等）
- **工具**：数据API或本地文件读取
- **质量门禁**：数据完整性检查、时间戳验证

### s02 数据预处理
- **操作**：质量控制、格式转换、坐标对齐、时间归一化
- **工具**：NetCDF处理库（xarray、netCDF4）
- **质量门禁**：缺失值率<5%、数据范围合理性检查

### s03 方法配置与输入输出契约验证 ⚠️（标准工作流关键步骤）
- **操作**：
  1. 冻结模型版本、权重文件路径、配置参数
  2. 设置随机种子确保可复现性
  3. 执行最小干运行测试（dry run），验证输入输出格式
  4. 检查输入输出契约（input/output contract）
- **参数**：模型版本号、权重路径、随机种子值
- **工具**：配置管理工具、单元测试框架
- **质量门禁**：dry run成功、输出维度与预期一致

### s04 模型推理
- **操作**：加载模型、执行预报推理
- **工具**：深度学习框架（PyTorch/TensorFlow）
- **质量门禁**：推理时间合理性、输出非NaN/Inf

### s05 预报产品生成
- **操作**：概率预报、最大风速、风险等级划分
- **工具**：后处理脚本
- **质量门禁**：概率值在[0,1]区间、风险等级覆盖完整

### s06 独立验证
- **操作**：使用独立于训练/调参的数据集验证预报性能
- **验证指标**：POD（检测概率）、FAR（虚报率）、CSI（临界成功指数）
- **工具**：验证指标计算库
- **质量门禁**：验证数据集不参与任何模型开发过程

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 预报时效 | 0-60分钟 | [1] | 对流阵风临近预报典型时效 |
| 时间分辨率 | 5-10分钟 | [1] | 雷达数据更新频率 |
| 空间分辨率 | 1-3公里 | [1] | 雷达数据空间分辨率 |

## 边界与分流
- 若s03方法配置验证失败 → 回退至s02检查数据预处理
- 若模型推理输出异常 → 检查s03配置是否正确
- 若独立验证指标低于阈值 → 重新执行s03调整参数

## 质量检查
- 每个步骤完成后记录执行日志
- s03必须生成method_artifact_identity_report
- s06验证数据集必须有明确来源和时间范围

## 资源召回建议
- 任务规划阶段召回本卡片
- 配套召回：radar-data-acquisition-preprocessing、forecast-independent-validation

## 证据来源
[1] Xiao et al., Convective-gust nowcasting based on radar reflectivity and a deep learning algorithm, Geoscientific Model Development, 2023, DOI: 10.5194/gmd-16-3611-2023
[2] Pan et al., Advancing Convective Precipitation Nowcasting via 3D Polarimetric Radar Data and Physics‐Constrained Deep Learning Model, Geophysical Research Letters, 2026, DOI: 10.1029/2025gl120431
