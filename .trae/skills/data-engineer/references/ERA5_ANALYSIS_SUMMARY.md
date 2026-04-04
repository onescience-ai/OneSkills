# ERA5 数据集分析完成总结

## 任务完成情况

✅ 已完成以下任务：

1. **创建ERA5数据集元数据文档** (`ERA5_DATASET_METADATA.md`)
   - 数据集基本信息
   - 完整气象变量列表（按高度层分类）
   - 数据维度和坐标信息
   - 统计信息
   - 数据访问方法
   - 文件结构说明

2. **创建ERA5数据处理配置文档** (`ERA5_DATA_PROCESSING.md`)
   - 基本配置
   - 数据处理流程配置
   - 训练数据集配置
   - Python代码示例
   - 常用数据处理操作
   - 错误处理和性能优化

3. **创建ERA5数据集使用指南** (`ERA5_DATASET_USAGE.md`)
   - OneScience数据集注册
   - 数据集接入方法
   - 数据集使用示例
   - 自定义数据集
   - 最佳实践

4. **创建分析脚本** (`analyze_era5_variables.py`)
   - 读取ERA5数据集
   - 分析所有气象变量
   - 生成变量统计信息
   - 绘制变量分布图
   - 保存分析结果

5. **创建参考文档README** (`README.md`)
   - 快速开始指南
   - 气象变量列表
   - 数据处理流程
   - 常用命令

## ERA5数据集核心信息

### 基本信息

- **数据提供方**: European Centre for Medium-Range Weather Forecasts (ECMWF)
- **版本**: 5th generation (ERA5)
- **时间范围**: 1959年至今
- **时间分辨率**: 1小时（原始数据）
- **空间分辨率**: 0.25° × 0.25°（约31km × 31km）
- **空间范围**: 全球（纬度：90°S - 90°N，经度：0° - 360°）

### 常用气象变量（9个）

#### 地表变量
1. `t2m` - 2米温度
2. `msl` - 海平面气压
3. `u10` - 10米u风分量
4. `v10` - 10米v风分量
5. `d2m` - 2米露点温度

#### 850 hPa层变量（低层大气）
6. `t850` - 850 hPa温度
7. `u850` - 850 hPa u风
8. `v850` - 850 hPa v风
9. `q850` - 850 hPa比湿

#### 500 hPa层变量（中层大气）
10. `z500` - 500 hPa位势高度
11. `t500` - 500 hPa温度
12. `u500` - 500 hPa u风
13. `v500` - 500 hPa v风

### 完整变量列表

ERA5数据集包含超过200个气象变量，涵盖：
- 地表变量（温度、气压、风速等）
- 多层大气变量（不同气压层的温度、风速、湿度等）
- 辐射变量（短波、长波辐射）
- 水汽变量（比湿、总水汽等）
- 其他变量（植被、土壤湿度等）

## 文件结构

```
/root/myapp/.trae/skills/data-engineer/
├── SKILL.md                           # data-engineer技能定义
└── references/                        # 数据参考文档目录
    ├── README.md                      # 参考文档总览
    ├── ERA5_DATASET_METADATA.md       # ERA5数据集元数据
    ├── ERA5_DATA_PROCESSING.md        # ERA5数据处理配置
    └── ERA5_DATASET_USAGE.md          # ERA5数据集使用指南

/root/myapp/
└── analyze_era5_variables.py          # ERA5变量分析脚本
```

## 使用方法

### 1. 查看ERA5数据集元数据

```bash
cat /root/myapp/.trae/skills/data-engineer/references/ERA5_DATASET_METADATA.md
```

### 2. 运行变量分析脚本

```bash
python /root/myapp/analyze_era5_variables.py /path/to/era5/data
```

### 3. 使用OneScience数据集

```python
from onescience.datapipes.climate.era5 import ERA5Dataset

dataset = ERA5Dataset(
    dataset={
        "data_dir": "/data/era5",
        "stats_dir": "/data/era5/stats",
        "channels": ["t2m", "msl", "u10", "v10"],
        "time_res": 1,
        "train_ratio": 0.8,
    },
    mode="train",
    output_steps=1,
    input_steps=2,
    normalize=True
)
```

## 数据处理流程

### 1. 数据接入
- 支持NetCDF、HDF5格式
- 自动检测数据格式
- 验证数据完整性

### 2. 数据清洗
- 缺失值处理
- 异常值检测
- 数据对齐

### 3. 数据重采样
- 时间重采样
- 空间重采样

### 4. 数据标准化
- Z-score标准化
- Min-Max标准化

## 参考资料

- [ERA5官方文档](https://confluence.ecmwf.int/display/CKB/ERA5)
- [Copernicus CDS](https://cds.climate.copernicus.eu/)

## 下一步

1. 如果有实际的ERA5数据文件，可以运行分析脚本进行详细分析
2. 根据具体需求选择合适的气象变量
3. 配置数据处理流程
4. 创建训练数据集

## 注意事项

1. ERA5数据量较大（约200TB），建议使用子集进行分析
2. 数据访问需要ECMWF账户或通过Copernicus CDS
3. 使用时需遵守CC BY 4.0许可协议
4. 注意数据版本和更新时间
