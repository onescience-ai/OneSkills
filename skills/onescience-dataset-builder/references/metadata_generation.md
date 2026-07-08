# 数据集元数据生成规范

本文档定义数据集元数据的生成规范和格式。

## 元数据文件结构

```
dataset_path/
├── metadata/
│   ├── dataset_card.json       # 数据集描述卡片
│   ├── statistics.json         # 统计信息
│   ├── splits.json             # 划分详情
│   └── lineage.json            # 数据血缘
├── load_dataset.py             # 加载示例
└── README.md                   # 数据集说明
```

---

## 1. dataset_card.json

**目的**：提供数据集的全面描述，类似 Hugging Face 的 dataset card。

**格式**：

```json
{
  "name": "ERA5_Temperature_Dataset",
  "version": "1.0.0",
  "created_at": "2026-06-15T03:12:27Z",
  "description": "ERA5 reanalysis temperature data for weather prediction",
  "domain": "earth",
  "task_type": "regression",
  "format": "netcdf",
  "statistics": {
    "total_samples": 10000,
    "splits": {
      "train": 7000,
      "val": 1500,
      "test": 1500
    },
    "features": {
      "spatial_dims": {"lat": 181, "lon": 360},
      "temporal_range": ["2020-01-01", "2022-12-31"],
      "variables": ["t2m", "tp", "sp"]
    },
    "labels": {
      "type": "continuous",
      "range": [250.0, 320.0],
      "unit": "K"
    }
  },
  "source": {
    "input_data": "/public/share/sugonhpcapp01/onestore/onedatasets/ERA5",
    "processing_script": "./build_dataset.py",
    "onescience_version": "1.0.0"
  },
  "quality": {
    "missing_rate": 0.001,
    "outlier_count": 5,
    "validation_passed": true
  },
  "usage": {
    "loader_example": "load_dataset.py",
    "recommended_batch_size": 32,
    "notes": "Data is normalized to zero mean and unit variance"
  },
  "citation": "Hersbach et al., 2020",
  "license": "CC BY 4.0"
}
```

**生成函数**：

```python
def generate_dataset_card(
    dataset_path,
    dataset_profile,
    statistics,
    quality_results,
    source_info
):
    """生成 dataset_card.json"""
    from datetime import datetime
    import json
    from pathlib import Path
    
    card = {
        "name": Path(dataset_path).name,
        "version": "1.0.0",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "description": dataset_profile.get("description", ""),
        "domain": dataset_profile.get("domain", "general"),
        "task_type": dataset_profile.get("task_type", "unknown"),
        "format": dataset_profile.get("format", "unknown"),
        "statistics": statistics,
        "source": source_info,
        "quality": {
            "missing_rate": quality_results.get("missing_rate", 0),
            "outlier_count": quality_results.get("outlier_count", 0),
            "validation_passed": quality_results.get("status") == "passed"
        },
        "usage": {
            "loader_example": "load_dataset.py",
            "notes": dataset_profile.get("usage_notes", "")
        }
    }
    
    # 保存
    metadata_dir = Path(dataset_path) / "metadata"
    metadata_dir.mkdir(exist_ok=True)
    
    card_path = metadata_dir / "dataset_card.json"
    with open(card_path, "w") as f:
        json.dump(card, f, indent=2)
    
    return card_path
```

---

## 2. statistics.json

**目的**：详细的统计信息，用于数据分析和质量监控。

**格式**：

```json
{
  "sample_counts": {
    "total": 10000,
    "train": 7000,
    "val": 1500,
    "test": 1500
  },
  "features": {
    "numerical": {
      "t2m": {
        "mean": 285.5,
        "std": 12.3,
        "min": 250.0,
        "max": 320.0,
        "quantiles": {
          "0.25": 278.0,
          "0.50": 285.0,
          "0.75": 293.0
        },
        "missing_count": 10
      }
    },
    "categorical": {
      "region": {
        "unique_values": 5,
        "value_counts": {
          "north": 2000,
          "south": 1800,
          "east": 2100,
          "west": 2000,
          "central": 2100
        }
      }
    }
  },
  "labels": {
    "type": "continuous",
    "distribution": {
      "mean": 288.5,
      "std": 10.2,
      "range": [250.0, 320.0]
    }
  },
  "data_quality": {
    "missing_rate": 0.001,
    "duplicate_count": 0,
    "outlier_count": 5
  }
}
```

**生成函数**：

```python
def generate_statistics(dataset_path, data_format):
    """生成 statistics.json"""
    import pandas as pd
    import numpy as np
    
    stats = {
        "sample_counts": count_samples_all_splits(dataset_path),
        "features": {},
        "labels": {},
        "data_quality": {}
    }
    
    # 分析训练集特征
    if data_format == "csv":
        train_df = pd.read_csv(Path(dataset_path) / "train" / "data.csv")
        
        # 数值特征统计
        numerical_cols = train_df.select_dtypes(include=[np.number]).columns
        stats["features"]["numerical"] = {}
        for col in numerical_cols:
            stats["features"]["numerical"][col] = {
                "mean": float(train_df[col].mean()),
                "std": float(train_df[col].std()),
                "min": float(train_df[col].min()),
                "max": float(train_df[col].max()),
                "quantiles": {
                    "0.25": float(train_df[col].quantile(0.25)),
                    "0.50": float(train_df[col].quantile(0.50)),
                    "0.75": float(train_df[col].quantile(0.75))
                },
                "missing_count": int(train_df[col].isnull().sum())
            }
        
        # 分类特征统计
        categorical_cols = train_df.select_dtypes(include=["object", "category"]).columns
        stats["features"]["categorical"] = {}
        for col in categorical_cols:
            value_counts = train_df[col].value_counts().to_dict()
            stats["features"]["categorical"][col] = {
                "unique_values": int(train_df[col].nunique()),
                "value_counts": {str(k): int(v) for k, v in value_counts.items()}
            }
    
    # 保存
    metadata_dir = Path(dataset_path) / "metadata"
    metadata_dir.mkdir(exist_ok=True)
    
    stats_path = metadata_dir / "statistics.json"
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    
    return stats_path
```

---

## 3. splits.json

**目的**：记录数据划分的详细信息。

**格式**：

```json
{
  "strategy": "random",
  "seed": 42,
  "ratios": {
    "train": 0.7,
    "val": 0.15,
    "test": 0.15
  },
  "sample_ids": {
    "train": ["sample_0001", "sample_0003", "..."],
    "val": ["sample_0002", "sample_0005", "..."],
    "test": ["sample_0004", "sample_0006", "..."]
  },
  "stratification": {
    "enabled": true,
    "column": "label",
    "distribution": {
      "train": {"class_0": 3500, "class_1": 3500},
      "val": {"class_0": 750, "class_1": 750},
      "test": {"class_0": 750, "class_1": 750}
    }
  }
}
```

**生成函数**：

```python
def generate_splits_info(dataset_path, split_config):
    """生成 splits.json"""
    
    splits = {
        "strategy": split_config.get("strategy", "random"),
        "seed": split_config.get("seed"),
        "ratios": split_config.get("ratios", {}),
        "sample_ids": extract_sample_ids_per_split(dataset_path)
    }
    
    # 如果有分层信息
    if split_config.get("stratify"):
        splits["stratification"] = {
            "enabled": True,
            "column": split_config["stratify"],
            "distribution": compute_stratification_distribution(dataset_path)
        }
    
    # 保存
    metadata_dir = Path(dataset_path) / "metadata"
    metadata_dir.mkdir(exist_ok=True)
    
    splits_path = metadata_dir / "splits.json"
    with open(splits_path, "w") as f:
        json.dump(splits, f, indent=2)
    
    return splits_path
```

---

## 4. lineage.json

**目的**：记录数据血缘，确保可重现性。

**格式**：

```json
{
  "input_sources": [
    {
      "path": "/public/share/sugonhpcapp01/onestore/onedatasets/ERA5",
      "type": "netcdf",
      "accessed_at": "2026-06-15T03:00:00Z",
      "version": "5.1"
    }
  ],
  "processing_steps": [
    {
      "step": 1,
      "operation": "spatial_crop",
      "script": "./build_dataset.py",
      "function": "crop_region",
      "parameters": {
        "lat_range": [20, 50],
        "lon_range": [100, 130]
      }
    },
    {
      "step": 2,
      "operation": "temporal_resample",
      "function": "resample_daily",
      "parameters": {
        "freq": "1D"
      }
    }
  ],
  "environment": {
    "python_version": "3.11.0",
    "dependencies": {
      "xarray": "2024.1.0",
      "pandas": "2.2.0",
      "numpy": "1.26.0"
    },
    "conda_env": "onescience311"
  },
  "reproducibility": {
    "command": "python build_dataset.py --input $INPUT_DATA_PATH --output $OUTPUT_DATA_PATH",
    "config_file": "dataset_config.yaml"
  }
}
```

---

## 5. load_dataset.py

**目的**：提供即用的数据加载示例代码。

**生成函数**：

```python
def generate_loader_example(dataset_path, data_format, dataset_profile):
    """生成 load_dataset.py"""
    
    if data_format == "csv":
        code = '''#!/usr/bin/env python3
"""数据集加载示例"""

import pandas as pd
from pathlib import Path

def load_dataset(dataset_path):
    """加载数据集"""
    train = pd.read_csv(Path(dataset_path) / "train" / "data.csv")
    val = pd.read_csv(Path(dataset_path) / "val" / "data.csv")
    test = pd.read_csv(Path(dataset_path) / "test" / "data.csv")
    
    print(f"Train: {len(train)} samples")
    print(f"Val: {len(val)} samples")
    print(f"Test: {len(test)} samples")
    
    return train, val, test

if __name__ == "__main__":
    train, val, test = load_dataset(".")
'''
    
    elif data_format == "netcdf":
        code = '''#!/usr/bin/env python3
"""数据集加载示例"""

import xarray as xr
from pathlib import Path

def load_dataset(dataset_path):
    """加载数据集"""
    train = xr.open_dataset(Path(dataset_path) / "train" / "data.nc")
    val = xr.open_dataset(Path(dataset_path) / "val" / "data.nc")
    test = xr.open_dataset(Path(dataset_path) / "test" / "data.nc")
    
    print(f"Train: {train.sizes}")
    print(f"Val: {val.sizes}")
    print(f"Test: {test.sizes}")
    
    return train, val, test

if __name__ == "__main__":
    train, val, test = load_dataset(".")
'''
    
    loader_path = Path(dataset_path) / "load_dataset.py"
    with open(loader_path, "w") as f:
        f.write(code)
    
    # 添加执行权限
    loader_path.chmod(0o755)
    
    return loader_path
```

---

## 元数据生成完整流程

```python
def generate_all_metadata(dataset_path, context):
    """生成所有元数据文件"""
    
    metadata_paths = {}
    
    # 1. dataset_card.json
    metadata_paths["card"] = generate_dataset_card(
        dataset_path,
        context["dataset_profile"],
        context["statistics"],
        context["quality_results"],
        context["source_info"]
    )
    
    # 2. statistics.json
    metadata_paths["statistics"] = generate_statistics(
        dataset_path,
        context["data_format"]
    )
    
    # 3. splits.json
    metadata_paths["splits"] = generate_splits_info(
        dataset_path,
        context["split_config"]
    )
    
    # 4. lineage.json
    metadata_paths["lineage"] = generate_lineage(
        dataset_path,
        context["processing_plan"]
    )
    
    # 5. load_dataset.py
    metadata_paths["loader"] = generate_loader_example(
        dataset_path,
        context["data_format"],
        context["dataset_profile"]
    )
    
    # 6. README.md (可选)
    if context.get("generate_readme"):
        metadata_paths["readme"] = generate_readme(dataset_path, context)
    
    return metadata_paths
```

## 注意事项

- 所有元数据文件使用 UTF-8 编码
- JSON 文件使用2空格缩进，便于阅读
- 数值类型应转换为 Python 原生类型（避免 numpy 类型）
- 时间戳使用 ISO 8601 格式（UTC时区）
- 文件路径使用绝对路径或相对于数据集根目录的相对路径
