---
name: data-engineer
description: 数据层技能，负责数据接入、处理、融合和 Benchmark 构建
---

# Skill: data-engineer

## 能力描述

本技能负责 AI4S Pipeline 的数据层任务，基于 OneScience 标准数据处理机制，提供完整的数据处理解决方案。支持 OneScience 内置数据集的直接使用，以及用户自定义数据的标准化接入。

## OneScience 数据处理标准

### 1. 统一数据集接口

所有数据集必须继承 `BaseDataset`，提供统一接口：

```python
from onescience.datapipes.core.base_dataset import BaseDataset

class MyDataset(BaseDataset):
    DOMAIN = "earth"  # earth, cfd, biology, materials, structural
    TASK = "forecasting"  # forecasting, classification, regression
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        # 返回样本字典，包含 input, target 等字段
        pass
    
    def __len__(self) -> int:
        pass
```

### 2. 统一配置系统

使用 `DatasetConfig` 进行统一配置管理：

```python
from onescience.datapipes.core.config import DatasetConfig, SourceConfig, DataConfig

config = DatasetConfig(
    name="my_dataset",
    domain="earth",
    source=SourceConfig(
        type="netcdf",
        path="/data/era5.nc",
        split="train"
    ),
    data=DataConfig(
        variables=["t2m", "u10", "v10"],
        features=["lat", "lon"]
    )
)
```

### 3. 数据集注册机制

使用 `DatasetRegistry` 注册和管理数据集：

```python
from onescience.datapipes.core.registry.dataset_registry import DatasetRegistry

@DatasetRegistry.register(
    name="era5",
    domain="earth",
    task="forecasting"
)
class ERA5Dataset(BaseDataset):
    pass
```

### 4. 数据集工厂

使用 `DatasetFactory` 创建数据集实例：

```python
from onescience.datapipes.core.registry.dataset_factory import DatasetFactory

# 方式1：使用kwargs
dataset = DatasetFactory.create(
    name="era5",
    path="/data/era5",
    split="train",
    variables=["t2m", "u10"]
)

# 方式2：使用配置文件
dataset = DatasetFactory.create("era5", config="config.yaml")
```

### 5. 数据转换流水线

使用 `TransformPipeline` 进行数据转换：

```python
from onescience.datapipes.datakit.transforms import (
    Compose, Normalize, ToTensor
)

transforms = Compose([
    Normalize(mean=0.5, std=1.0),
    ToTensor()
])
```

## 核心能力

### 1. 数据接入

支持多种数据格式的接入：

| 数据格式 | 支持情况 | 说明 |
|---------|---------|------|
| NetCDF | ✅ 完全支持 | 气象、海洋等科学数据 |
| HDF5 | ✅ 完全支持 | 大规模科学数据 |
| Zarr | ✅ 完全支持 | 云原生数据 |
| CSV | ✅ 完全支持 | 表格数据 |
| GeoTIFF | ✅ 完全支持 | 地理空间数据 |
| PDB | ✅ 完全支持 | 蛋白质结构数据 |
| LMDB | ✅ 完全支持 | 键值存储 |

### 2. 数据处理

提供完整数据处理功能：

| 处理类型 | 支持情况 | 说明 |
|---------|---------|------|
| 数据清洗 | ✅ 完全支持 | 缺失值处理、异常值检测 |
| 数据对齐 | ✅ 完全支持 | 空间对齐、时间对齐 |
| 数据重采样 | ✅ 完全支持 | 空间重采样、时间重采样 |
| 数据标准化 | ✅ 完全支持 | 归一化、标准化 |
| 数据增强 | ✅ 完全支持 | 数据扩增、变换 |

### 3. 多源融合

支持多源数据融合：

| 融合类型 | 支持情况 | 说明 |
|---------|---------|------|
| 全球-区域融合 | ✅ 完全支持 | 嵌套、特征注入 |
| 多模态融合 | ✅ 完全支持 | 特征拼接、交叉注意力 |
| 多物理场融合 | ✅ 完全支持 | 物理场耦合 |
| 多分辨率融合 | ✅ 完全支持 | 降尺度、升尺度 |

### 4. Benchmark 构建

提供 Benchmark 构建功能：

| 功能类型 | 支持情况 | 说明 |
|---------|---------|------|
| 数据集划分 | ✅ 完全支持 | 训练/验证/测试集划分 |
| 评估指标 | ✅ 完全支持 | 多种评估指标 |
| 对比实验 | ✅ 完全支持 | 多模型对比 |

## 使用方法

### 场景 1：使用 OneScience 内置数据集

**用户需求**：使用 ERA5 气象数据集进行训练。

**Prompt**：
```
基于OneScience标准数据处理机制，使用内置的ERA5数据集：
1. 使用DatasetFactory创建ERA5数据集
2. 配置数据路径和变量
3. 创建数据加载器
4. 保存至 data_loading.py
```

**输出**：数据加载代码

### 场景 2：接入用户自定义数据

**用户需求**：接入用户自己的气象数据。

**Prompt**：
```
基于OneScience标准数据处理机制，接入用户自定义数据：
1. 用户提供数据元数据信息（格式、字段、维度等）
2. 创建自定义数据集类
3. 注册到DatasetRegistry
4. 创建配置文件
5. 保存至 custom_dataset.py
```

**输出**：自定义数据集代码

### 场景 3：数据处理和转换

**用户需求**：对气象数据进行清洗和标准化。

**Prompt**：
```
基于OneScience标准数据处理机制，处理气象数据：
1. 使用TransformPipeline定义转换流水线
2. 实现数据清洗、标准化等转换
3. 应用转换到数据集
4. 保存至 data_transforms.py
```

**输出**：数据转换代码

### 场景 4：多源数据融合

**用户需求**：融合全球和区域气象数据。

**Prompt**：
```
基于OneScience标准数据处理机制，融合多源数据：
1. 使用DatasetFactory创建多个数据集
2. 实现空间和时间对齐
3. 实现特征融合模块
4. 保存至 multisource_fusion.py
```

**输出**：多源融合代码

## 核心规则

### 1. 数据集元数据规范（强制）

用户自定义数据必须提供以下元数据信息：

```python
# 用户数据元数据格式
class UserDataMetadata:
    def __init__(self):
        # 基本信息
        self.name = "my_dataset"
        self.domain = "earth"  # earth, cfd, biology, materials
        self.task = "forecasting"  # forecasting, classification, regression
        
        # 数据格式
        self.format = "NetCDF"  # NetCDF, HDF5, Zarr, CSV, etc.
        self.path = "/path/to/data"
        
        # 变量信息
        self.variables = [
            {
                "name": "t2m",
                "type": "float32",
                "dimensions": ["time", "lat", "lon"],
                "unit": "K",
                "description": "2米温度"
            },
            {
                "name": "u10",
                "type": "float32",
                "dimensions": ["time", "lat", "lon"],
                "unit": "m/s",
                "description": "10米u风分量"
            }
        ]
        
        # 维度信息
        self.dimensions = {
            "time": 1000,
            "lat": 721,
            "lon": 1440
        }
        
        # 时间信息
        self.time_info = {
            "start": "2020-01-01",
            "end": "2022-12-31",
            "step": "6h"  # 时间步长
        }
        
        # 空间信息
        self.spatial_info = {
            "lat_range": [-90, 90],
            "lon_range": [0, 360],
            "lat_step": 0.25,
            "lon_step": 0.25
        }
```

### 2. 数据接入流程规范（强制）

数据接入必须遵循以下流程：

```python
# 数据接入流程
def data_ingestion_pipeline(metadata: UserDataMetadata):
    # 1. 验证数据文件
    validate_data_files(metadata.path)
    
    # 2. 读取数据
    dataset = load_data(
        metadata.path,
        metadata.format,
        variables=metadata.variables
    )
    
    # 3. 验证数据完整性
    validate_data_integrity(dataset)
    
    # 4. 生成元数据
    metadata = generate_metadata(dataset)
    
    return dataset, metadata
```

### 3. 数据集注册规范（强制）

自定义数据集必须注册到 `DatasetRegistry`：

```python
# 数据集注册规范
@DatasetRegistry.register(
    name="my_dataset",
    domain="earth",
    task="forecasting",
    description="My custom dataset",
    required_params=["path", "variables"],
    optional_params=["split", "scaling"],
    data_formats=["NetCDF", "HDF5", "Zarr"]
)
class MyDataset(BaseDataset):
    pass
```

## 输出格式

### 数据集元数据模板

```python
"""
Data Engineer - 数据元数据

任务描述：{任务描述}
数据领域：{领域}
数据格式：{格式}
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path


@dataclass
class VariableInfo:
    """变量信息"""
    name: str
    type: str
    dimensions: List[str]
    unit: str
    description: str
    min: float = None
    max: float = None
    mean: float = None
    std: float = None


@dataclass
class DatasetMetadata:
    """数据集元数据"""
    # 基本信息
    name: str
    domain: str  # earth, cfd, biology, materials, structural
    task: str  # forecasting, classification, regression
    
    # 数据格式
    format: str  # NetCDF, HDF5, Zarr, CSV, etc.
    path: str
    version: str = "1.0.0"
    
    # 变量信息
    variables: List[VariableInfo]
    
    # 维度信息
    dimensions: Dict[str, int]
    
    # 时间信息
    time_info: Dict[str, Any]
    
    # 空间信息
    spatial_info: Dict[str, Any]
    
    # 统计信息
    statistics: Dict[str, Dict[str, float]]
    
    # 其他信息
    extra: Dict[str, Any] = None


def validate_metadata(metadata: DatasetMetadata) -> bool:
    """验证元数据完整性"""
    required_fields = ["name", "domain", "task", "format", "path", "variables"]
    for field in required_fields:
        if not hasattr(metadata, field) or getattr(metadata, field) is None:
            raise ValueError(f"Missing required field: {field}")
    return True


if __name__ == '__main__':
    # 使用示例
    metadata = DatasetMetadata(
        name="my_dataset",
        domain="earth",
        task="forecasting",
        format="NetCDF",
        path="/data/era5.nc",
        variables=[
            VariableInfo(
                name="t2m",
                type="float32",
                dimensions=["time", "lat", "lon"],
                unit="K",
                description="2米温度"
            )
        ],
        dimensions={"time": 1000, "lat": 721, "lon": 1440},
        time_info={
            "start": "2020-01-01",
            "end": "2022-12-31",
            "step": "6h"
        },
        spatial_info={
            "lat_range": [-90, 90],
            "lon_range": [0, 360]
        }
    )
    
    validate_metadata(metadata)
```

### 数据集代码模板

```python
"""
Data Engineer - 数据集

任务描述：{任务描述}
数据领域：{领域}
数据格式：{格式}
"""

import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import numpy as np
import torch
import xarray as xr
from torch.utils.data import Dataset

from onescience.datapipes.core.base_dataset import BaseDataset
from onescience.datapipes.core.config import DatasetConfig
from onescience.datapipes.core.registry.dataset_registry import DatasetRegistry


logger = logging.getLogger(__name__)


@DatasetRegistry.register(
    name="my_dataset",
    domain="earth",
    task="forecasting",
    description="My custom dataset",
    required_params=["path", "variables"],
    optional_params=["split", "scaling"],
    data_formats=["NetCDF", "HDF5", "Zarr"]
)
class MyDataset(BaseDataset):
    """
    自定义数据集类
    
    功能：
    - 数据加载
    - 数据预处理
    - 样本采样
    """
    
    DOMAIN = "earth"
    TASK = "forecasting"
    REQUIRED_PARAMS = ["path", "variables"]
    OPTIONAL_PARAMS = ["split", "scaling"]
    DATA_FORMATS = ["NetCDF", "HDF5", "Zarr"]
    
    def __init__(self, config: Union[DatasetConfig, Dict[str, Any]]):
        super().__init__(config)
        
        # 初始化数据路径
        self._init_paths()
        
        # 加载元数据
        self._load_metadata()
        
        # 初始化数据
        self._init_data()
        
        # 初始化转换流水线
        self._init_transforms()
    
    def _init_paths(self):
        """初始化数据路径"""
        self.data_path = Path(self.config.source.path)
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data path not found: {self.data_path}")
        
        logger.info(f"Data path: {self.data_path}")
    
    def _load_metadata(self):
        """加载元数据"""
        # 加载变量列表
        if self.config.data.variables:
            self.variables = self.config.data.variables
        
        # 加载气压层级
        if hasattr(self.config.data, 'levels'):
            self.levels = self.config.data.extra.get('levels', [])
        
        # 加载统计信息
        self.statistics = self._load_statistics()
    
    def _init_data(self):
        """初始化数据"""
        # 加载数据集
        self.dataset = self._load_dataset()
        
        # 获取数据长度
        self.length = len(self.dataset)
    
    def _init_transforms(self):
        """初始化转换流水线"""
        from onescience.datapipes.datakit.transforms import Compose
        
        transforms = []
        if self.config.transforms:
            for transform_config in self.config.transforms:
                transform = self._create_transform(transform_config)
                transforms.append(transform)
        
        self.transform = Compose(transforms) if transforms else None
    
    def _load_dataset(self) -> xr.Dataset:
        """加载数据集"""
        if self.config.source.type == "NetCDF":
            dataset = xr.open_dataset(self.data_path)
        elif self.config.source.type == "HDF5":
            dataset = self._load_hdf5()
        elif self.config.source.type == "Zarr":
            dataset = xr.open_zarr(self.data_path)
        else:
            raise ValueError(f"Unsupported format: {self.config.source.type}")
        
        return dataset
    
    def _create_transform(self, config: Dict[str, Any]):
        """创建转换"""
        from onescience.datapipes.core.registry.transform_registry import get_transform
        
        transform_type = config.get('type')
        transform_params = config.get('params', {})
        
        transform_cls = get_transform(transform_type)
        if transform_cls is None:
            raise ValueError(f"Unknown transform type: {transform_type}")
        
        return transform_cls(**transform_params)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """获取样本"""
        # 加载样本
        sample = self._load_sample(idx)
        
        # 应用转换
        if self.transform is not None:
            sample = self.transform(sample)
        
        return sample
    
    def __len__(self) -> int:
        """返回数据集大小"""
        return self.length
    
    def _load_sample(self, idx: int) -> Dict[str, Any]:
        """加载单个样本"""
        # 实现样本加载逻辑
        pass
    
    def _load_statistics(self) -> Dict[str, Dict[str, float]]:
        """加载统计信息"""
        # 实现统计信息加载逻辑
        return {}


if __name__ == '__main__':
    # 使用示例
    from onescience.datapipes.core.registry.dataset_factory import DatasetFactory
    
    # 创建数据集
    dataset = DatasetFactory.create(
        name="my_dataset",
        path="/data/era5.nc",
        split="train",
        variables=["t2m", "u10", "v10"]
    )
    
    # 获取样本
    sample = dataset[0]
    print(f"Sample keys: {sample.keys()}")
```

### 数据加载代码模板

```python
"""
Data Engineer - 数据加载

任务描述：{任务描述}
数据集名称：{数据集名称}
"""

from typing import Optional
from omegaconf import DictConfig

from onescience.datapipes.core.registry.dataset_factory import DatasetFactory, create_dataset
from onescience.datapipes.core.base_dataloader import create_dataloader


def create_dataset_and_dataloader(
    dataset_name: str,
    config: Optional[DictConfig] = None,
    **kwargs
):
    """
    创建数据集和数据加载器
    
    Parameters
    ----------
    dataset_name : str
        数据集名称
    config : Optional[DictConfig]
        配置对象
    **kwargs
        额外参数
        
    Returns
    -------
    tuple
        (train_loader, val_loader, test_loader)
    """
    # 创建数据集
    train_dataset = create_dataset(
        dataset_name,
        config=config,
        split="train",
        **kwargs
    )
    
    val_dataset = create_dataset(
        dataset_name,
        config=config,
        split="val",
        **kwargs
    )
    
    test_dataset = create_dataset(
        dataset_name,
        config=config,
        split="test",
        **kwargs
    )
    
    # 创建数据加载器
    train_loader = create_dataloader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True
    )
    
    val_loader = create_dataloader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False
    )
    
    test_loader = create_dataloader(
        test_dataset,
        batch_size=config.batch_size,
        shuffle=False
    )
    
    return train_loader, val_loader, test_loader


if __name__ == '__main__':
    # 使用示例
    train_loader, val_loader, test_loader = create_dataset_and_dataloader(
        dataset_name="era5",
        config="config.yaml",
        variables=["t2m", "u10", "v10"]
    )
    
    # 遍历数据
    for batch in train_loader:
        input_data = batch["input"]
        target_data = batch["target"]
        print(f"Input shape: {input_data.shape}")
        print(f"Target shape: {target_data.shape}")
```

## OneScience 内置数据集

### 地球科学数据集

| 数据集名称 | 领域 | 任务 | 格式 | 说明 |
|-----------|------|------|------|------|
| era5 | earth | forecasting | NetCDF | ERA5 气象数据 |
| gfs | earth | forecasting | NetCDF | GFS 气象数据 |
| ocn | earth | forecasting | NetCDF | 海洋数据 |
| cmip6 | earth | forecasting | NetCDF | CMIP6 气候数据 |

### 计算流体力学数据集

| 数据集名称 | 领域 | 任务 | 格式 | 说明 |
|-----------|------|------|------|------|
| vortex_shedding | cfd | forecasting | HDF5 | 涡脱落数据 |
| stokes | cfd | regression | HDF5 | Stokes 流数据 |
| drivaernet | cfd | forecasting | HDF5 | 汽车气动数据 |

### 生物学数据集

| 数据集名称 | 领域 | 任务 | 格式 | 说明 |
|-----------|------|------|------|------|
| protein | biology | classification | PDB | 蛋白质结构数据 |
| multimer | biology | classification | PDB | 蛋白质复合物数据 |
| genome | biology | regression | HDF5 | 基因组数据 |

### 材料科学数据集

| 数据集名称 | 领域 | 任务 | 格式 | 说明 |
|-----------|------|------|------|------|
| fairchem | materials | regression | LMDB | 材料性质预测 |
| qm9 | materials | regression | HDF5 | QM9 分子数据 |

## 使用示例

### 示例 1：使用内置数据集

```python
from onescience.datapipes.core.registry.dataset_factory import DatasetFactory

# 创建数据集
dataset = DatasetFactory.create(
    name="era5",
    path="/data/era5.nc",
    split="train",
    variables=["t2m", "u10", "v10"]
)

# 获取样本
sample = dataset[0]
```

### 示例 2：接入自定义数据

```python
# 1. 提供数据元数据
metadata = {
    "name": "my_dataset",
    "domain": "earth",
    "task": "forecasting",
    "format": "NetCDF",
    "path": "/data/my_data.nc",
    "variables": [
        {"name": "t2m", "type": "float32", "dimensions": ["time", "lat", "lon"]},
        {"name": "u10", "type": "float32", "dimensions": ["time", "lat", "lon"]}
    ],
    "dimensions": {"time": 1000, "lat": 721, "lon": 1440},
    "time_info": {"start": "2020-01-01", "end": "2022-12-31", "step": "6h"}
}

# 2. 创建自定义数据集
# (参考上面的数据集代码模板)

# 3. 注册数据集
# (参考上面的注册规范)

# 4. 使用数据集
dataset = DatasetFactory.create("my_dataset", path="/data/my_data.nc")
```

### 示例 3：数据转换

```python
from onescience.datapipes.datakit.transforms import Compose, Normalize, ToTensor

# 定义转换流水线
transforms = Compose([
    Normalize(mean=0.5, std=1.0),
    ToTensor()
])

# 应用转换
config = DatasetConfig(
    name="my_dataset",
    transforms=transforms
)

dataset = DatasetFactory.create("my_dataset", config=config)
```

## 最佳实践

### 1. 数据接入最佳实践

```python
# 数据接入最佳实践
def data_ingestion_best_practices(metadata: UserDataMetadata):
    # 1. 验证数据文件
    validate_data_files(metadata.path)
    
    # 2. 读取数据
    dataset = load_data(metadata.path, metadata.format)
    
    # 3. 验证数据完整性
    validate_data_integrity(dataset)
    
    # 4. 生成元数据
    metadata = generate_metadata(dataset)
    
    # 5. 注册数据集
    DatasetRegistry.register(
        name=metadata.name,
        domain=metadata.domain,
        task=metadata.task
    )
    
    return dataset, metadata
```

### 2. 数据处理最佳实践

```python
# 数据处理最佳实践
def data_processing_best_practices(dataset: BaseDataset, transforms: Compose):
    # 1. 定义转换流水线
    transforms = Compose([
        Normalize(mean=0.5, std=1.0),
        ToTensor()
    ])
    
    # 2. 应用转换
    dataset.transform = transforms
    
    # 3. 验证处理结果
    validate_processed_data(dataset)
    
    return dataset
```

### 3. 数据集注册最佳实践

```python
# 数据集注册最佳实践
@DatasetRegistry.register(
    name="my_dataset",
    domain="earth",
    task="forecasting",
    description="My custom dataset",
    required_params=["path", "variables"],
    optional_params=["split", "scaling"],
    data_formats=["NetCDF", "HDF5", "Zarr"]
)
class MyDataset(BaseDataset):
    # 实现必需的方法
    pass
```

## 错误处理

### 常见错误 1：数据格式不支持

**错误**：数据格式不支持

**解决**：添加格式支持

```python
# 添加格式支持
def load_data(data_path: str, format: str) -> xr.Dataset:
    if format == "NetCDF":
        dataset = xr.open_dataset(data_path)
    elif format == "HDF5":
        dataset = load_hdf5(data_path)
    elif format == "Zarr":
        dataset = xr.open_zarr(data_path)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    return dataset
```

### 常见错误 2：数据对齐失败

**错误**：数据对齐失败

**解决**：使用多种对齐策略

```python
# 多种对齐策略
def spatial_alignment(data_sources: List[torch.Tensor]) -> torch.Tensor:
    # 策略 1：双线性插值
    try:
        aligned_data = bilinear_interpolation(data_sources)
        return aligned_data
    except Exception as e:
        print(f"Bilinear interpolation failed: {e}")
    
    # 策略 2：最近邻插值
    try:
        aligned_data = nearest_neighbor_interpolation(data_sources)
        return aligned_data
    except Exception as e:
        print(f"Nearest neighbor interpolation failed: {e}")
    
    raise AlignmentError("All alignment strategies failed")
```

### 常见错误 3：数据集注册失败

**错误**：数据集注册失败

**解决**：检查注册参数

```python
# 检查注册参数
def check_registration(name: str, domain: str, task: str):
    if not name:
        raise ValueError("Dataset name must be specified")
    
    if domain not in ["earth", "cfd", "biology", "materials", "structural"]:
        raise ValueError(f"Invalid domain: {domain}")
    
    if task not in ["forecasting", "classification", "regression"]:
        raise ValueError(f"Invalid task: {task}")
```

## 总结

本技能提供了基于 OneScience 标准的数据处理解决方案：

- ✅ **内置数据集**：支持 OneScience 内置数据集直接使用
- ✅ **自定义数据接入**：标准化的自定义数据接入流程
- ✅ **元数据规范**：完整的元数据规范和验证
- ✅ **数据处理**：完整的数据处理流程
- ✅ **数据集注册**：统一的数据集注册机制
- ✅ **数据集工厂**：统一的数据集创建接口
- ✅ **错误处理**：完善的错误处理机制
- ✅ **最佳实践**：遵循 OneScience 最佳实践

通过本技能，用户可以快速完成数据层任务，无论是使用内置数据集还是接入自定义数据。
