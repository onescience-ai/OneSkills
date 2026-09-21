# 遥感制图产品的标准输出格式规范

## 适用范围
适用于遥感制图产品的输出格式与元数据规范。30米农田范围图等遥感产品应以 GeoTIFF 或 Cloud Optimized GeoTIFF (COG) 格式输出，包含完整的空间参考和质量标志元数据。

## 输入
- 分类结果：numpy 数组或栅格数据。
- 空间参考信息：CRS、仿射变换、nodata 值。

## 输出
- GeoTIFF/COG 文件：包含分类结果和空间元数据。
- 元数据文件：`quality_metadata.json`，包含 CRS、变换矩阵、nodata、不确定性信息。

## 流程节点
1. 数据转换为栅格 → 2. 空间元数据嵌入 → 3. 质量标志编码 → 4. 输出文件生成

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| output_format | GeoTIFF/COG | [论文1] | 遥感产品标准交付格式 |
| crs | EPSG投影代码 | [论文1] | 坐标参考系统 |
| transform | 仿射变换矩阵 | [论文1] | 像素到地理坐标的转换 |
| nodata_value | -9999 或 255 | [论文1] | 无效值标记 |
| uncertainty_band | 可选波段 | [论文1] | 置信度或不确定性信息 |
| pyramid | 多分辨率金字塔 | [论文1] | 加速可视化 |

## 边界与分流
- 当输出格式不满足规范时：使用 rasterio 或 gdal 库转换为 GeoTIFF。
- 当元数据不完整时：补充 CRS、变换矩阵、nodata 字段。

## 质量检查
- 检查输出目录中是否存在 `.tif` 文件。
- 验证 `quality_metadata.json` 中是否包含 `nodata_value` 和 `transform` 字段。

## 回退策略
- 如果无法生成 GeoTIFF，至少生成 CSV 并记录格式降级原因。

## 资源召回建议
- 当任务涉及遥感产品输出时召回本卡片。
- 配套资源：数据真实性验收标准、预处理工作流、独立验证标准。

## 证据来源
[1] Advances of Remote Sensing in Land Cover and Land Use Mapping, Remote Sensing, 2023, DOI: 10.3390/rs15030195