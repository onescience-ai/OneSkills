# ERA5 数据集使用指南

## 目录

1. [OneScience 数据集注册](#onescience-数据集注册)
2. [数据集接入](#数据集接入)
3. [数据集使用示例](#数据集使用示例)
4. [自定义数据集](#自定义数据集)
5. [最佳实践](#最佳实践)

---

## OneScience 数据集注册

### 基础注册

```python
from onescience.datapipes.core import BaseDataset
from onescience.datapipes.core.registry import DatasetRegistry

@DatasetRegistry.register(
    name="era5",
    domain="earth",
    task="forecasting",
    description="ERA5 global atmospheric reanalysis data",
    required_params=["data_dir", "stats_dir", "channels"],
    optional_params=["train_ratio", "val_ratio", "test_ratio"],
    data_formats=["NetCDF", "HDF5"]
)
class ERA5Dataset(BaseDataset):
    """ERA5数据集"""
    
    DOMAIN = "earth"
    TASK = "forecasting"
    
    def __init__(self, data_dir, stats_dir, channels, mode='train', **kwargs):
        super().__init__(kwargs)
        self.data_dir = data_dir
        self.stats_dir = stats_dir
        self.channels = channels
        self.mode = mode
        
    def __getitem__(self, idx):
        # 实现数据获取逻辑
        pass
        
    def __len__(self):
        # 返回数据集大小
        pass
```

### 完整注册示例

```python
from onescience.datapipes.core import BaseDataset
from onescience.datapipes.core.registry import DatasetRegistry
from onescience.datapipes.core.config import DatasetConfig
import os
import h5py
import numpy as np
import torch
from torch.utils.data import Dataset

@DatasetRegistry.register(
    name="era5",
    domain="earth",
    task="forecasting",
    description="ERA5 global atmospheric reanalysis data from ECMWF",
    required_params=["data_dir", "stats_dir", "channels"],
    optional_params=[
        "mode", "input_steps", "output_steps", 
        "normalize", "patch_size"
    ],
    data_formats=["HDF5", "NetCDF"]
)
class ERA5Dataset(BaseDataset):
    """
    ERA5数据集类
    
    继承自BaseDataset，提供OneScience标准的数据集接口
    """
    
    # 元数据
    DOMAIN = "earth"
    TASK = "forecasting"
    REQUIRED_PARAMS = ["data_dir", "stats_dir", "channels"]
    OPTIONAL_PARAMS = ["mode", "input_steps", "output_steps", "normalize", "patch_size"]
    DATA_FORMATS = ["HDF5", "NetCDF"]
    
    def __init__(self, config: DatasetConfig):
        """
        初始化ERA5数据集
        
        Args:
            config: 数据集配置对象
        """
        super().__init__(config)
        
        # 从配置中获取参数
        self.data_dir = config.source.path
        self.stats_dir = config.source.stats_dir
        self.channels = config.data.variables
        self.mode = config.data.get("mode", "train")
        self.input_steps = config.data.get("input_steps", 2)
        self.output_steps = config.data.get("output_steps", 1)
        self.normalize = config.data.get("normalize", True)
        self.patch_size = config.data.get("patch_size", [1, 1])
        
        # 初始化数据
        self._init_metadata()
        self._init_normalization()
        self._init_split()
        self._init_files()
        
    def _init_metadata(self):
        """初始化元数据"""
        meta_path = os.path.join(self.data_dir, 'metadata.json')
        with open(meta_path, "r") as f:
            self.metadata = json.load(f)
            
        self.years = list(map(int, self.metadata["years"]))
        self.variables = self.metadata["variables"]
        
    def _init_normalization(self):
        """初始化归一化参数"""
        mu = np.load(os.path.join(self.stats_dir, "global_means.npy"))
        std = np.load(os.path.join(self.stats_dir, "global_stds.npy"))
        
        self.channel_indices = [self.variables.index(v) for v in self.channels]
        self.mu = mu[:, self.channel_indices, :, :]
        self.std = std[:, self.channel_indices, :, :]
        
    def _init_split(self):
        """初始化数据集划分"""
        # 实现数据集划分逻辑
        pass
        
    def _init_files(self):
        """初始化文件列表"""
        # 实现文件列表初始化
        pass
        
    def __getitem__(self, idx: int) -> dict:
        """
        获取单个样本
        
        Args:
            idx: 样本索引
            
        Returns:
            dict: 包含样本数据的字典
        """
        # 实现样本获取逻辑
        return {
            "input": input_data,
            "target": target_data,
            "metadata": {
                "time": time,
                "location": location
            }
        }
        
    def __len__(self) -> int:
        """返回数据集大小"""
        return self.total_samples
        
    def get_statistics(self) -> dict:
        """
        获取数据集统计信息
        
        Returns:
            dict: 统计信息字典
        """
        return {
            "mean": self.mu,
            "std": self.std,
            "min": self.min,
            "max": self.max
        }
```

---

## 数据集接入

### 方式1：使用内置数据集

```python
from onescience.datapipes import DatasetFactory

# 创建数据集配置
config = {
    "name": "era5",
    "domain": "earth",
    "task": "forecasting",
    "source": {
        "type": "NetCDF",
        "path": "/data/era5",
        "stats_dir": "/data/era5/stats"
    },
    "data": {
        "variables": ["t2m", "msl", "u10", "v10"],
        "input_steps": 2,
        "output_steps": 1,
        "normalize": True
    }
}

# 创建数据集
dataset = DatasetFactory.create_dataset(config)
```

### 方式2：使用Datapipe

```python
from onescience.datapipes.climate.era5 import ERA5Datapipe

# 创建参数配置
params = {
    "dataset": {
        "data_dir": "/data/era5",
        "stats_dir": "/data/era5/stats",
        "channels": ["t2m", "msl", "u10", "v10"],
        "time_res": 1,
        "train_ratio": 0.8,
        "val_ratio": 0.1,
        "test_ratio": 0.1,
        "img_size": [721, 1440],
        "batch_size": 4,
        "num_workers": 4,
    },
    "dataloader": {
        "batch_size": 4,
        "num_workers": 4,
    }
}

# 创建数据管道
datapipe = ERA5Datapipe(params, distributed=False)

# 获取数据加载器
train_loader, sampler = datapipe.train_dataloader()
val_loader, _ = datapipe.val_dataloader()
test_loader = datapipe.test_dataloader()
```

### 方式3：直接使用Dataset

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
        "val_ratio": 0.1,
        "test_ratio": 0.1,
    },
    mode="train",
    output_steps=1,
    input_steps=2,
    normalize=True
)

# 创建数据加载器
from torch.utils.data import DataLoader

train_loader = DataLoader(
    dataset,
    batch_size=4,
    shuffle=True,
    num_workers=4,
    pin_memory=True
)
```

---

## 数据集使用示例

### 示例1：基本使用

```python
import torch
from onescience.datapipes.climate.era5 import ERA5Dataset

# 创建数据集
dataset = ERA5Dataset(
    dataset={
        "data_dir": "/data/era5",
        "stats_dir": "/data/era5/stats",
        "channels": ["t2m", "msl", "u10", "v10"],
        "time_res": 1,
        "train_ratio": 0.8,
        "val_ratio": 0.1,
        "test_ratio": 0.1,
    },
    mode="train",
    output_steps=1,
    input_steps=2,
    normalize=True
)

# 获取样本
input_data, target_data, cos_zenith, step_idx, time_index = dataset[0]

print(f"Input shape: {input_data.shape}")  # [input_steps, C, H, W]
print(f"Target shape: {target_data.shape}")  # [output_steps, C, H, W]
print(f"Time index: {time_index}")
```

### 示例2：数据加载器

```python
from torch.utils.data import DataLoader
from onescience.datapipes.climate.era5 import ERA5Dataset

# 创建数据集
dataset = ERA5Dataset(
    dataset={
        "data_dir": "/data/era5",
        "stats_dir": "/data/era5/stats",
        "channels": ["t2m", "msl", "u10", "v10"],
        "time_res": 1,
        "train_ratio": 0.8,
        "val_ratio": 0.1,
        "test_ratio": 0.1,
    },
    mode="train",
    output_steps=1,
    input_steps=2,
    normalize=True
)

# 创建数据加载器
train_loader = DataLoader(
    dataset,
    batch_size=4,
    shuffle=True,
    num_workers=4,
    pin_memory=True,
    drop_last=True
)

# 遍历数据
for input_data, target_data, cos_zenith, step_idx, time_index in train_loader:
    print(f"Batch input shape: {input_data.shape}")
    print(f"Batch target shape: {target_data.shape}")
    
    # 用于模型训练
    # output = model(input_data)
    # loss = criterion(output, target_data)
    # loss.backward()
    
    break  # 仅演示
```

### 示例3：多变量使用

```python
from onescience.datapipes.climate.era5 import ERA5Dataset

# 定义变量组
variables = {
    "surface": ["t2m", "msl", "u10", "v10"],
    "lower_troposphere": ["t850", "u850", "v850", "q850"],
    "mid_troposphere": ["z500", "t500", "u500", "v500"],
    "upper_troposphere": ["t250", "u250", "v250"]
}

# 选择变量
selected_vars = (
    variables["surface"] + 
    variables["lower_troposphere"] + 
    variables["mid_troposphere"]
)

# 创建数据集
dataset = ERA5Dataset(
    dataset={
        "data_dir": "/data/era5",
        "stats_dir": "/data/era5/stats",
        "channels": selected_vars,
        "time_res": 1,
        "train_ratio": 0.8,
        "val_ratio": 0.1,
        "test_ratio": 0.1,
    },
    mode="train",
    output_steps=1,
    input_steps=2,
    normalize=True
)

print(f"Total variables: {len(selected_vars)}")
```

### 示例4：自定义时间步

```python
# 不同时间步配置
configs = [
    {"input_steps": 1, "output_steps": 1, "name": "1-step"},
    {"input_steps": 2, "output_steps": 1, "name": "2-step"},
    {"input_steps": 4, "output_steps": 2, "name": "4-step"},
    {"input_steps": 6, "output_steps": 3, "name": "6-step"},
]

for config in configs:
    dataset = ERA5Dataset(
        dataset={
            "data_dir": "/data/era5",
            "stats_dir": "/data/era5/stats",
            "channels": ["t2m", "msl", "u10", "v10"],
            "time_res": 1,
            "train_ratio": 0.8,
        },
        mode="train",
        output_steps=config["output_steps"],
        input_steps=config["input_steps"],
        normalize=True
    )
    
    print(f"{config['name']}: {len(dataset)} samples")
```

---

## 自定义数据集

### 自定义ERA5数据集

```python
from onescience.datapipes.core import BaseDataset
from onescience.datapipes.core.registry import DatasetRegistry
import h5py
import numpy as np
import torch
import os

@DatasetRegistry.register(
    name="custom_era5",
    domain="earth",
    task="forecasting",
    description="Custom ERA5 dataset with additional features",
    required_params=["data_dir", "stats_dir", "channels"],
    optional_params=["use_cos_zenith", "use_latlon"],
    data_formats=["HDF5"]
)
class CustomERA5Dataset(BaseDataset):
    """
    自定义ERA5数据集
    
    扩展功能：
    - 添加余弦天顶角
    - 添加经纬度信息
    """
    
    DOMAIN = "earth"
    TASK = "forecasting"
    
    def __init__(self, config):
        super().__init__(config)
        
        self.data_dir = config.source.path
        self.stats_dir = config.source.stats_dir
        self.channels = config.data.variables
        self.use_cos_zenith = config.data.get("use_cos_zenith", False)
        self.use_latlon = config.data.get("use_latlon", False)
        
        # 初始化
        self._init_data()
        
    def _init_data(self):
        """初始化数据"""
        # 加载元数据
        meta_path = os.path.join(self.data_dir, 'metadata.json')
        with open(meta_path, "r") as f:
            self.metadata = json.load(f)
            
        # 加载统计信息
        mu = np.load(os.path.join(self.stats_dir, "global_means.npy"))
        std = np.load(os.path.join(self.stats_dir, "global_stds.npy"))
        
        self.mu = torch.from_numpy(mu).float()
        self.std = torch.from_numpy(std).float()
        
        # 初始化经纬度网格
        if self.use_latlon:
            self._init_latlon()
            
    def _init_latlon(self):
        """初始化经纬度网格"""
        # 实现经纬度网格初始化
        pass
        
    def __getitem__(self, idx: int) -> dict:
        """
        获取样本
        
        Returns:
            dict: {
                "input": torch.Tensor,
                "target": torch.Tensor,
                "cos_zenith": torch.Tensor (可选),
                "latlon": torch.Tensor (可选),
                "metadata": dict
            }
        """
        # 加载数据
        data = self._load_data(idx)
        
        # 归一化
        input_data = (data["input"] - self.mu) / self.std
        target_data = (data["target"] - self.mu) / self.std
        
        # 构建输出
        output = {
            "input": input_data,
            "target": target_data,
            "metadata": data["metadata"]
        }
        
        # 添加可选字段
        if self.use_cos_zenith:
            output["cos_zenith"] = data["cos_zenith"]
            
        if self.use_latlon:
            output["latlon"] = self.latlon_grid
            
        return output
        
    def __len__(self) -> int:
        return self.total_samples
```

### 使用自定义数据集

```python
from onescience.datapipes import DatasetFactory

# 创建配置
config = {
    "name": "custom_era5",
    "domain": "earth",
    "task": "forecasting",
    "source": {
        "type": "HDF5",
        "path": "/data/era5",
        "stats_dir": "/data/era5/stats"
    },
    "data": {
        "variables": ["t2m", "msl", "u10", "v10"],
        "input_steps": 2,
        "output_steps": 1,
        "normalize": True,
        "use_cos_zenith": True,
        "use_latlon": True
    }
}

# 创建数据集
dataset = DatasetFactory.create_dataset(config)

# 使用数据集
from torch.utils.data import DataLoader

train_loader = DataLoader(
    dataset,
    batch_size=4,
    shuffle=True,
    num_workers=4
)
```

---

## 最佳实践

### 1. 数据验证

```python
def validate_dataset(dataset):
    """验证数据集"""
    # 检查数据集大小
    assert len(dataset) > 0, "Dataset is empty"
    
    # 检查样本格式
    sample = dataset[0]
    assert "input" in sample, "Sample must contain 'input'"
    assert "target" in sample, "Sample must contain 'target'"
    
    # 检查数据类型
    assert isinstance(sample["input"], torch.Tensor), "Input must be torch.Tensor"
    assert isinstance(sample["target"], torch.Tensor), "Target must be torch.Tensor"
    
    # 检查数据形状
    assert len(sample["input"].shape) == 4, "Input must be 4D tensor"
    assert len(sample["target"].shape) == 4, "Target must be 4D tensor"
    
    print("✅ Dataset validation passed")
```

### 2. 数据可视化

```python
import matplotlib.pyplot as plt

def visualize_sample(sample, var_idx=0):
    """可视化样本"""
    input_data = sample["input"]
    target_data = sample["target"]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # 输入数据
    axes[0, 0].imshow(input_data[0, var_idx].numpy())
    axes[0, 0].set_title(f"Input Step 0 - Variable {var_idx}")
    
    axes[0, 1].imshow(input_data[1, var_idx].numpy())
    axes[0, 1].set_title(f"Input Step 1 - Variable {var_idx}")
    
    # 目标数据
    axes[1, 0].imshow(target_data[0, var_idx].numpy())
    axes[1, 0].set_title(f"Target Step 0 - Variable {var_idx}")
    
    # 差异
    diff = target_data[0, var_idx] - input_data[-1, var_idx]
    axes[1, 1].imshow(diff.numpy(), cmap='RdBu')
    axes[1, 1].set_title("Difference")
    
    plt.tight_layout()
    plt.show()
```

### 3. 性能监控

```python
import time

def benchmark_dataloader(dataloader, num_batches=10):
    """基准测试数据加载器"""
    times = []
    
    for i, batch in enumerate(dataloader):
        if i >= num_batches:
            break
            
        start_time = time.time()
        # 模拟数据处理
        input_data, target_data = batch[:2]
        _ = input_data.numpy()  # 强制加载数据
        end_time = time.time()
        
        times.append(end_time - start_time)
        
    avg_time = np.mean(times)
    print(f"Average batch loading time: {avg_time:.4f} seconds")
    print(f"Samples per second: {dataloader.batch_size / avg_time:.2f}")
    
    return times
```

### 4. 内存管理

```python
import gc

def safe_dataloader(dataloader, max_memory_gb=16):
    """安全的数据加载器"""
    import psutil
    
    for batch in dataloader:
        # 检查内存使用
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            print("⚠️  High memory usage, cleaning up...")
            gc.collect()
            
        yield batch
```

### 5. 错误处理

```python
def safe_get_item(dataset, idx):
    """安全地获取数据集项"""
    try:
        return dataset[idx]
    except Exception as e:
        print(f"Error loading index {idx}: {e}")
        # 返回默认值或跳过
        return None
```

---

## 常见问题

### Q1: 数据加载太慢怎么办？

**A:** 
- 增加`num_workers`参数
- 使用`pin_memory=True`
- 启用数据缓存
- 减少`prefetch_factor`

### Q2: 内存不足怎么办？

**A:**
- 减小`batch_size`
- 减少`num_workers`
- 使用`persistent_workers=False`
- 启用内存映射

### Q3: 数据格式不支持怎么办？

**A:**
- 使用`xarray`转换为NetCDF
- 使用`h5py`转换为HDF5
- 实现自定义数据集类

### Q4: 如何调试数据加载？

**A:**
```python
# 单线程调试
dataloader = DataLoader(dataset, num_workers=0)

# 检查数据
for i, batch in enumerate(dataloader):
    print(f"Batch {i}: {batch[0].shape}")
    if i >= 5:
        break
```

---

## 参考资料

- [OneScience文档](https://onescience.readthedocs.io)
- [ERA5官方文档](https://confluence.ecmwf.int/display/CKB/ERA5)
- [PyTorch DataLoader](https://pytorch.org/docs/stable/data.html)
