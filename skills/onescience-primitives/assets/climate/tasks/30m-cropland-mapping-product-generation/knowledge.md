# 30米农田范围与面积制图产品生成任务

## 适用范围

**适用场景**：
- 需要将分类结果转换为标准格式的遥感产品
- 需要生成符合GeoTIFF/COG规范的输出文件
- 需要包含完整的空间元数据和质量标志信息

**不适用场景**：
- 不需要标准格式输出的简单分析
- 不需要空间参考的表格数据

## 输入契约

**模型与输入来源**：CPU 随机森林路线使用由同一特征定义和监督标签拟合的模型，模型文件由 joblib 保存，概率列对应模型的 `classes_`。该路线没有外部预训练权重依赖。影像输入为 `/public/share/sugonhpcapp01/onestore/rsi/onestore/onedatasets/landsat-8-c2-l2-044033-2021-sacramento-30m-window/`，标签输入为 `/public/share/sugonhpcapp01/onestore/rsi/onestore/onedatasets/usda-cdl-2021-sacramento-30m-training-window/cropland-2021.tif`，二者属于 Sacramento 2021 年、EPSG:5070 的共同网格；其分类结果属于该地域和年份。

**必需输入**：
- 分类结果（农田概率图、二值范围图）
- 空间参考信息（CRS、仿射变换）
- 无效值定义（nodata_value）

**可选输入**：
- 置信度波段
- 质量标志信息
- 派生产品清单

## 操作步骤

### 步骤1：GeoTIFF/COG格式转换

**分块生成**：概率、二值分类、QA 和有效观测次数共享输入网格。正类概率通过 `classes_` 中的类别位置确定，二值分类来自相同概率及农田阈值；无效像元独立于农田/非农田类别。分块写入时单块数据量为 `块高 × 块宽 × 波段数 × 每元素字节数`。
将numpy数组或栅格数据转换为GeoTIFF格式，支持Cloud Optimized GeoTIFF (COG)布局。

**工具**：rasterio、GDAL

**关键参数**：
- 坐标参考系统（CRS）：如EPSG:4326（WGS84）
- 仿射变换矩阵：定义像素到地理坐标的映射
- 无效值标记：nodata_value
- 压缩方式：如DEFLATE、LZW

### 步骤2：空间元数据完整性

**空间参考来源**：Sacramento 示例继承所列输入的 EPSG:5070、30 m 分辨率和仿射变换。印度行政区源文件 `/public/share/sugonhpcapp01/onestore/rsi/onestore/onedatasets/geoboundaries-ind-adm1-1811400/geoBoundaries-IND-ADM1.geojson` 的坐标为 CRS84，经 `shapeISO=IN-PB` 对应 Punjab；其源坐标系与栅格输出网格是不同的空间对象，重投影关系由实际源信息决定。
确保输出文件包含完整的空间元数据信息。

**必需元数据**：
- CRS（坐标参考系统）
- 仿射变换矩阵（GeoTransform）
- 无效值标记（nodata_value）
- 分辨率（resolution）
- 边界框（bounding box）

**可选元数据**：
- 金字塔层级（pyramid levels）
- 置信度波段
- 质量标志信息

### 步骤3：质量标志与不确定性信息
生成并编码质量标志和不确定性信息。

**质量标志类型**：
- 云掩膜标志
- 阴影掩膜标志
- 数据质量等级
- 分类置信度

**编码方式**：
- 使用位运算编码多个质量标志
- 提供质量标志解码说明

### 步骤4：产品元数据生成
生成完整的产品元数据文件。

**元数据内容**：
- 产品名称和版本
- 数据来源和处理历史
- 空间范围和时间范围
- 分类系统说明
- 精度评估结果
- 使用限制和引用方式

## 输出产物

**主要输出**：
- GeoTIFF/COG格式的农田范围图
- 产品元数据文件（quality_metadata.json）
- 文件清单和校验信息

**元数据要求**：
- 所有空间元数据完整且可读
- 质量标志信息可解码
- 文件校验信息（MD5、SHA256）

## 质量门禁

- 输出文件能够重新打开且变量和元数据完整
- 结果单位、坐标、有效时间和物理范围已核验
- 派生产品均有明确公式、源变量和质量标志
- 输出坐标、分辨率、无效值和置信信息完整

## 回退策略

- 空间参考缺失时，坐标系由可核实的源元数据确定；只有来源确为 WGS84 时采用 WGS84，来源不明的坐标系保持未知
- 当无效值定义不明确时：使用标准无效值（如-9999），并在元数据中说明
- 当置信度波段不可用时：只生成基本产品，不生成置信度信息

## 资源召回建议

**计算资源**：CPU RF 使用 scikit-learn，模型保存与加载使用 joblib，GeoTIFF 读写使用 rasterio/GDAL。Sacramento 256×256 两季数据、32 条训练记录、4 棵深度上限为 4 的树，在单线程完成拟合和产品生成时峰值主存为 289.41 MiB，初始配置可采用 1 CPU 核、1 GiB 主存，GPU 数量及显存需求均为 0。该观测包含特征处理和推理，不是单独写图的内存最低值。更大区域的主存由分块、特征数、模型树节点及并发数决定；28 维 float32 的 1024×1024 和 2048×2048 特征块分别占 112 MiB 和 448 MiB，另有模型与读写缓存开销。

- 当需要生成GeoTIFF/COG格式产品时召回本卡片
- 当需要确保空间元数据完整性时召回本卡片
- 当需要生成质量标志信息时召回本卡片

## 证据来源

**来源资料信息**：

```json
{
  "harvested": true,
  "harvest_source": "onescience-knowledge-harvester",
  "harvest_query": "遥感制图产品的标准输出格式规范（GeoTIFF/COG）、空间元数据完整性要求（CRS、变换矩阵、nodata、pyramid）、质量标志与不确定性信息的标准编码方式",
  "evidence_papers": [
    {
      "title": "30 m 5-yearly land cover maps of Qilian Mountain Area (QMA_LC30) from 1990 to 2020",
      "doi": "10.1038/s41597-024-03976-9",
      "year": 2024
    }
  ]
}
```

[1] Yang A, Zhong B, Wang X, et al. 30 m 5-yearly land cover maps of Qilian Mountain Area (QMA_LC30) from 1990 to 2020. Sci Data. 2024;11(1):1339. DOI: 10.1038/s41597-024-03976-9
