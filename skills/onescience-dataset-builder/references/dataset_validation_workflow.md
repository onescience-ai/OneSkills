# 数据集验证工作流

本文档定义 dataset-builder 在阶段2（验证结果）的完整工作流程。

## 输入

- `step_spec.dataset_path`：runtime 执行后生成的数据集路径
- `step_spec.expected_format`：预期的数据格式
- `processing_plan.quality_checks`：需要执行的质量检查清单
- `processing_plan.leakage_checks`：数据泄漏检测项

## 工作流程

### 1. 验证数据集存在性

```python
from pathlib import Path

def validate_dataset_exists(dataset_path):
    """检查数据集是否存在"""
    path = Path(dataset_path)
    
    if not path.exists():
        return {
            "exists": False,
            "error": f"数据集路径不存在: {dataset_path}"
        }
    
    # 检查是否为目录
    if not path.is_dir():
        return {
            "exists": False,
            "error": f"数据集路径不是目录: {dataset_path}"
        }
    
    # 检查是否为空目录
    if not list(path.iterdir()):
        return {
            "exists": True,
            "warning": "数据集目录为空"
        }
    
    return {"exists": True}
```

### 2. 验证数据集格式

根据 `expected_format` 检查文件结构和格式：

```python
def validate_format(dataset_path, expected_format):
    """验证数据集格式"""
    issues = []
    
    # 检查标准目录结构
    expected_dirs = ["train", "val", "test"]
    for dir_name in expected_dirs:
        dir_path = Path(dataset_path) / dir_name
        if not dir_path.exists():
            issues.append(f"缺少 {dir_name} 目录")
    
    # 检查文件格式
    if expected_format == "csv":
        # 检查 CSV 文件存在
        pass
    elif expected_format == "netcdf":
        # 检查 NetCDF 文件存在
        pass
    elif expected_format == "image":
        # 检查图片文件
        pass
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }
```

### 3. 执行质量检查

根据 `processing_plan.quality_checks` 执行检查：

```python
def execute_quality_checks(dataset_path, quality_checks):
    """执行质量检查清单"""
    results = {
        "passed": [],
        "failed": [],
        "warnings": []
    }
    
    for check in quality_checks:
        check_type = check.get("type")
        
        if check_type == "completeness":
            result = check_completeness(dataset_path, check)
        elif check_type == "format":
            result = check_format(dataset_path, check)
        elif check_type == "statistics":
            result = check_statistics(dataset_path, check)
        elif check_type == "domain_specific":
            result = check_domain_specific(dataset_path, check)
        else:
            result = {"status": "skipped", "reason": f"未知检查类型: {check_type}"}
        
        if result["status"] == "passed":
            results["passed"].append(check)
        elif result["status"] == "failed":
            results["failed"].append({**check, "error": result.get("error")})
        elif result["status"] == "warning":
            results["warnings"].append({**check, "message": result.get("message")})
    
    return results
```

详见 `quality_checks.md`。

### 4. 收集数据集统计信息

```python
def collect_statistics(dataset_path):
    """收集数据集统计信息"""
    stats = {}
    
    # 样本数统计
    stats["total_samples"] = count_samples(dataset_path)
    stats["splits"] = {
        "train": count_samples(Path(dataset_path) / "train"),
        "val": count_samples(Path(dataset_path) / "val"),
        "test": count_samples(Path(dataset_path) / "test")
    }
    
    # 特征统计（如适用）
    if has_features(dataset_path):
        stats["features"] = analyze_features(dataset_path)
    
    # 标签分布（如适用）
    if has_labels(dataset_path):
        stats["label_distribution"] = analyze_label_distribution(dataset_path)
    
    return stats
```

### 5. 生成数据集元数据

调用 `metadata_generation.md` 中定义的函数生成：
- `dataset_card.json`：数据集描述卡片
- `statistics.json`：统计信息
- `splits.json`：划分信息

```python
from datetime import datetime

def generate_dataset_card(dataset_path, processing_plan, statistics):
    """生成 dataset_card.json"""
    card = {
        "name": Path(dataset_path).name,
        "version": "1.0.0",
        "created_at": datetime.utcnow().isoformat(),
        "description": processing_plan.get("dataset_profile", {}).get("description", ""),
        "domain": processing_plan.get("dataset_profile", {}).get("domain", ""),
        "format": processing_plan.get("dataset_profile", {}).get("format", ""),
        "statistics": statistics,
        "splits": statistics.get("splits", {}),
        "source": {
            "input_data": processing_plan.get("input_data_path"),
            "processing_script": processing_plan.get("script_path")
        },
        "usage": {
            "loader_example": "load_dataset.py"
        }
    }
    
    card_path = Path(dataset_path) / "dataset_card.json"
    with open(card_path, "w") as f:
        json.dump(card, f, indent=2)
    
    return card_path
```

详见 `metadata_generation.md`。

### 6. 生成加载示例

```python
def generate_loader_example(dataset_path, data_format):
    """生成 load_dataset.py 示例代码"""
    
    if data_format == "csv":
        code = """
import pandas as pd
from pathlib import Path

def load_dataset(dataset_path):
    train = pd.read_csv(Path(dataset_path) / "train" / "data.csv")
    val = pd.read_csv(Path(dataset_path) / "val" / "data.csv")
    test = pd.read_csv(Path(dataset_path) / "test" / "data.csv")
    return train, val, test
"""
    elif data_format == "netcdf":
        code = """
import xarray as xr
from pathlib import Path

def load_dataset(dataset_path):
    train = xr.open_dataset(Path(dataset_path) / "train" / "data.nc")
    val = xr.open_dataset(Path(dataset_path) / "val" / "data.nc")
    test = xr.open_dataset(Path(dataset_path) / "test" / "data.nc")
    return train, val, test
"""
    else:
        code = "# 请根据实际数据格式编写加载代码\n"
    
    loader_path = Path(dataset_path) / "load_dataset.py"
    with open(loader_path, "w") as f:
        f.write(code)
    
    return loader_path
```

### 7. 返回验证结果给 orchestrator

```python
def build_validation_result(checks_results, statistics, metadata_paths):
    """构建验证结果（符合 orchestrator 契约）"""
    
    # 判断整体状态
    if checks_results["quality_checks"]["failed"]:
        status = "failed"
    elif checks_results["quality_checks"]["warnings"]:
        status = "partial"
    else:
        status = "success"
    
    return {
        "skill": "onescience-dataset-builder",
        "status": status,
        "artifacts": {
            "dataset_card": str(metadata_paths["card"]),
            "statistics": str(metadata_paths["statistics"]),
            "splits": str(metadata_paths["splits"]),
            "loader_example": str(metadata_paths["loader"])
        },
        "observation": {
            "summary": "数据集验证完成",
            "completed": [
                "完整性检查",
                "格式验证",
                "统计分析",
                "元数据生成"
            ],
            "validation_results": {
                "format_valid": checks_results["format"]["valid"],
                "completeness": statistics["sample_counts"]["splits"],
                "quality_issues": checks_results["quality_checks"]["failed"]
            },
            "warnings": checks_results["quality_checks"]["warnings"],
            "risks": [],
            "next_recommendation": "数据集已验证，可用于训练" if status == "success" else "修复质量问题后重新验证"
        }
    }
```

## 验证失败处理

### 数据集不存在

```yaml
execution_result:
  skill: onescience-dataset-builder
  status: failed
  artifacts: {}
  observation:
    summary: 数据集验证失败
    completed: []
    validation_results:
      dataset_exists: false
    warnings: []
    risks: ["数据集路径不存在，runtime 执行可能失败"]
    next_recommendation: "检查 runtime 执行日志，确认数据集输出路径"
```

### 格式验证失败

```yaml
execution_result:
  skill: onescience-dataset-builder
  status: failed
  artifacts: {}
  observation:
    summary: 格式验证失败
    completed: ["完整性检查"]
    validation_results:
      format_valid: false
      quality_issues:
        - "缺少 train 目录"
        - "缺少 val 目录"
    warnings: []
    risks: ["数据集结构不完整，无法用于训练"]
    next_recommendation: "检查数据处理脚本是否正确生成了 train/val/test 目录"
```

### 质量检查失败

```yaml
execution_result:
  skill: onescience-dataset-builder
  status: partial
  artifacts:
    dataset_card: ./output/metadata/dataset_card.json
    statistics: ./output/metadata/statistics.json
  observation:
    summary: 数据集验证部分通过，存在质量问题
    completed: ["完整性检查", "格式验证", "统计分析"]
    validation_results:
      format_valid: true
      completeness: {train: 7000, val: 1500, test: 1500}
      quality_issues:
        - "缺失率 12% 超过阈值 5%"
    warnings: ["发现 5 个异常值"]
    risks: ["数据缺失率较高，可能影响模型训练"]
    next_recommendation: "清洗数据降低缺失率，或接受当前质量继续训练"
```

## 注意事项

- 所有元数据文件应保存在 `dataset_path/metadata/` 目录下（如果不存在则创建）
- 验证失败时应提供清晰的错误信息和修复建议
- 统计信息应包含足够的细节以便调试
- 加载示例应该是可直接运行的代码
