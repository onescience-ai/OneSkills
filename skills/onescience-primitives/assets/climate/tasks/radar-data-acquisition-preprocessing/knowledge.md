# 雷达数据获取与预处理

## 适用范围
适用于气象雷达反射率数据、ERA5再分析数据等气象数据的获取、格式转换和预处理任务。

## 输入
- 数据源配置（API端点或本地路径）
- 目标区域范围（经纬度边界）
- 时间范围（起止时间戳）

## 输出
- 标准化NetCDF4格式文件
- 数据质量报告（缺失值率、异常值统计）

## 流程节点
1. **数据源识别** → 确定可用数据源（UK Radar Composite、ERA5、本地雷达站）
2. **数据获取** → 通过API下载或本地文件读取
3. **质量控制** → 去除异常值、处理缺失值、检查数据范围
4. **格式转换** → 统一为NetCDF4格式、标准化变量单位
5. **坐标对齐** → 统一坐标系、空间插值
6. **时间归一化** → 统一时间戳格式、处理时区差异

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据格式 | NetCDF4 | [1] | 气象数据标准格式 |
| 反射率单位 | dBZ | [2] | 雷达反射率标准单位 |
| 时间分辨率 | 5-10分钟 | [1] | 雷达数据更新频率 |

## 边界与分流
- 若数据源不可用 → 启用降级策略（使用替代数据源或模拟数据标注）
- 若数据质量不合格 → 记录质量报告并标记异常时段

## 质量检查
- 缺失值率<5%
- 反射率范围：-30至70 dBZ
- 时间连续性检查

## 回退策略
- 数据获取失败时使用本地缓存数据
- 格式转换失败时记录错误并跳过该时段

## 资源召回建议
- 数据处理任务阶段召回本卡片
- 配套召回：convective-gust-nowcasting-workflow

## 证据来源
[1] Franch et al., TAASRAD19, a high-resolution weather radar reflectivity dataset for precipitation nowcasting, Scientific Data, 2020, DOI: 10.1038/s41597-020-0574-8
[2] Lee et al., Standardized radar wind profiler dataset via integrated raw data processing in Korea, Scientific Data, 2026, DOI: 10.1038/s41597-026-07277-1
