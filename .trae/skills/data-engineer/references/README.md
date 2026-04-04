# ERA5 数据集参考文档

## 概述

本目录包含ERA5数据集的元数据、处理指南和使用示例，用于OneScience数据处理技能。

## 文件说明

### 1. ERA5_DATASET_METADATA.md

**内容**: ERA5数据集元数据

**主要章节**:
- 数据集概述（基本信息、时间范围、空间分辨率等）
- 完整气象变量列表（按高度层分类）
- 数据维度信息（空间、时间、数据格式）
- 统计信息（均值、标准差等）
- 数据访问方法（ECMWF、Copernicus CDS）
- 数据使用注意事项
- 文件结构说明

**适用场景**:
- 了解ERA5数据集的基本信息
- 选择合适的气象变量
- 了解数据格式和维度
- 获取数据统计参数

---

### 2. ERA5_DATA_PROCESSING.md

**内容**: ERA5数据处理配置指南

**主要章节**:
- 基本配置（路径、变量、时间、空间）
- 数据处理流程配置（清洗、对齐、重采样、标准化）
- 训练数据集配置
- 数据加载配置
- 完整配置示例
- Python代码示例（加载、处理、可视化、统计）
- 常用数据处理操作（选择变量、重采样、标准化、切片）
- 数据集划分方法
- 错误处理
- 性能优化

**适用场景**:
- 配置ERA5数据处理流程
- 了解数据处理步骤
- 编写数据处理代码
- 解决数据处理问题

---

### 3. ERA5_DATASET_USAGE.md

**内容**: ERA5数据集使用指南

**主要章节**:
- OneScience数据集注册
- 数据集接入方法（3种方式）
- 数据集使用示例（4个示例）
- 自定义数据集
- 最佳实践（5个实践）
- 常见问题解答
- 参考资料

**适用场景**:
- 在OneScience中注册ERA5数据集
- 选择合适的数据接入方式
- 编写数据集使用代码
- 创建自定义数据集

---

## 快速开始

### 1. 查看ERA5数据集元数据

```bash
# 查看元数据文档
cat ERA5_DATASET_METADATA.md | less
```

**主要信息**:
- 9个常用气象变量（t2m, msl, u10, v10, t850, u850, v850, z500, q850）
- 时间范围：1959年至今
- 空间分辨率：0.25° × 0.25°
- 时间分辨率：1小时

---

### 2. 分析ERA5数据集

```bash
# 运行分析脚本
python analyze_era5_variables.py /path/to/era5/data
```

**功能**:
- 加载ERA5数据
- 分析所有气象变量
- 生成变量统计信息
- 绘制变量分布图
- 保存分析结果

---

### 3. 使用OneScience数据集

```python
from onescience.datapipes.climate.era5 import ERA5Dataset

# 创建数据集
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

# 创建数据加载器
from torch.utils.data import DataLoader

train_loader = DataLoader(dataset, batch_size=4, shuffle=True)
```

---

## 气象变量列表

### 地表变量

| 变量名 | 全称 | 单位 | 描述 |
|--------|------|------|------|
| `t2m` | 2米温度 | K | 距地面2米处的空气温度 |
| `msl` | 海平面气压 | Pa | 海平面气压 |
| `u10` | 10米u风分量 | m/s | 距地面10米处的东向风速 |
| `v10` | 10米v风分量 | m/s | 距地面10米处的北向风速 |
| `d2m` | 2米露点温度 | K | 距地面2米处的露点温度 |

### 850 hPa层变量（低层大气）

| 变量名 | 全称 | 单位 | 描述 |
|--------|------|------|------|
| `t850` | 850 hPa温度 | K | 850 hPa层温度 |
| `u850` | 850 hPa u风 | m/s | 850 hPa层东向风速 |
| `v850` | 850 hPa v风 | m/s | 850 hPa层北向风速 |
| `q850` | 850 hPa比湿 | kg/kg | 850 hPa层比湿 |

### 500 hPa层变量（中层大气）

| 变量名 | 全称 | 单位 | 描述 |
|--------|------|------|------|
| `z500` | 500 hPa位势高度 | m²/s² | 500 hPa层位势高度 |
| `t500` | 500 hPa温度 | K | 500 hPa层温度 |
| `u500` | 500 hPa u风 | m/s | 500 hPa层东向风速 |
| `v500` | 500 hPa v风 | m/s | 500 hPa层北向风速 |

### 完整变量列表

详细变量列表请参考 [ERA5_DATASET_METADATA.md](ERA5_DATASET_METADATA.md)

---

## 数据处理流程

### 1. 数据接入

```python
from onescience.datapipes.climate.era5 import ERA5Datapipe

datapipe = ERA5Datapipe(params, distributed=False)
train_loader, sampler = datapipe.train_dataloader()
```

### 2. 数据清洗

- 缺失值处理
- 异常值检测
- 数据对齐

### 3. 数据重采样

- 时间重采样（1小时 → 6小时）
- 空间重采样（降采样）

### 4. 数据标准化

- Z-score标准化
- Min-Max标准化

---

## 常用命令

```bash
# 查看ERA5数据集元数据
cat ERA5_DATASET_METADATA.md

# 运行变量分析脚本
python analyze_era5_variables.py /path/to/era5/data

# 查看数据处理配置
cat ERA5_DATA_PROCESSING.md

# 查看数据集使用示例
cat ERA5_DATASET_USAGE.md
```

---

## 参考资料

- [ERA5官方文档](https://confluence.ecmwf.int/display/CKB/ERA5)
- [Copernicus CDS](https://cds.climate.copernicus.eu/)
- [OneScience文档](https://onescience.readthedocs.io)
- [xarray文档](https://xarray.pydata.org/)

---

## 更新历史

- **2024-01-15**: 初始版本
- **2024-06-20**: 添加更多变量和统计信息
- **2025-01-10**: 更新数据访问方法

---

## 联系方式

如有问题，请参考：
1. ERA5官方文档
2. OneScience文档
3. 相关论文和文献
