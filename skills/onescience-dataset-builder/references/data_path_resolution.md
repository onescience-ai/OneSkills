# 数据路径解析规范

本文档定义如何从 `onescience.json` 和用户输入中解析数据集路径。

## 路径解析优先级

1. **用户显式指定** (`step_spec.input_data_hint`)
2. **onescience.json 配置** (`runtime.script.env_vars.ONESCIENCE_DATASETS_DIR`)
3. **推断失败** → 返回错误，要求用户明确指定

## 读取 onescience.json

### 文件位置

项目根目录的 `onescience.json`，由 orchestrator 在初始化时生成。

### 读取步骤

```python
import json
from pathlib import Path

def read_onescience_config():
    """读取 onescience.json 配置"""
    config_path = Path.cwd() / "onescience.json"
    
    if not config_path.exists():
        raise FileNotFoundError(
            "未找到 onescience.json，请确保 orchestrator 已初始化项目"
        )
    
    with open(config_path) as f:
        config = json.load(f)
    
    return config

def get_datasets_dir(config):
    """提取 ONESCIENCE_DATASETS_DIR"""
    try:
        env_vars = config["runtime"]["script"]["env_vars"]
        datasets_dir = env_vars.get("ONESCIENCE_DATASETS_DIR")
        
        if not datasets_dir:
            raise KeyError("ONESCIENCE_DATASETS_DIR 未配置")
        
        return datasets_dir
    except KeyError as e:
        raise ValueError(f"onescience.json 配置不完整: {e}")
```

### 示例配置

```json
{
  "runtime": {
    "script": {
      "env_vars": {
        "ONESCIENCE_DATASETS_DIR": "/public/share/sugonhpcapp01/onestore/onedatasets/",
        "ONESCIENCE_MODELS_DIR": "/public/share/sugonhpcapp01/onestore/onemodels/"
      }
    }
  }
}
```

## 列出可用数据集路径

从 ONESCIENCE_DATASETS_DIR 读取所有可用的数据集路径。

### 实现方法

```python
def list_available_datasets(datasets_dir):
    """列出数据目录下的所有数据集"""
    import os
    from pathlib import Path
    
    datasets_dir_path = Path(datasets_dir)
    
    if not datasets_dir_path.exists():
        raise FileNotFoundError(f"数据目录不存在: {datasets_dir}")
    
    # 列出所有子目录（每个子目录视为一个数据集）
    available_datasets = []
    for item in datasets_dir_path.iterdir():
        if item.is_dir():
            available_datasets.append({
                "name": item.name,
                "path": str(item),
                "size": get_dir_size(item) if item.exists() else 0
            })
    
    return available_datasets

def get_dir_size(path):
    """获取目录大小（可选，用于排序）"""
    total = 0
    try:
        for entry in path.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
    except:
        pass
    return total
```

## 匹配最相关的数据集

根据用户需求和数据集特征，选择最相关的数据集路径。

### 匹配策略

```python
def match_dataset(user_requirement, available_datasets, dataset_profile):
    """根据需求匹配最相关的数据集"""
    
    # 1. 提取关键词
    combined_text = f"{user_requirement} {dataset_profile.get('description', '')} {dataset_profile.get('domain', '')}".lower()
    
    # 2. 对每个可用数据集计算匹配分数
    scored_datasets = []
    for dataset in available_datasets:
        dataset_name_lower = dataset["name"].lower()
        score = 0
        
        # 精确匹配（权重最高）
        if dataset_name_lower in combined_text or combined_text in dataset_name_lower:
            score += 10
        
        # 部分匹配
        keywords = combined_text.split()
        for keyword in keywords:
            if keyword in dataset_name_lower:
                score += 1
        
        scored_datasets.append({
            **dataset,
            "score": score
        })
    
    # 3. 按分数排序
    scored_datasets.sort(key=lambda x: x["score"], reverse=True)
    
    # 4. 返回最高分的数据集
    if scored_datasets and scored_datasets[0]["score"] > 0:
        return scored_datasets[0]
    else:
        return None
```

## 完整的路径解析流程

```python
def resolve_input_data_path(step_spec, processing_plan, config):
    """完整的路径解析流程"""
    
    # 1. 用户显式指定
    if step_spec.get("input_data_hint"):
        return step_spec["input_data_hint"]
    
    # 2. 从配置读取基础路径
    datasets_dir = get_datasets_dir(config)
    
    # 3. 列出所有可用数据集
    available_datasets = list_available_datasets(datasets_dir)
    
    if not available_datasets:
        raise ValueError(f"数据目录为空: {datasets_dir}")
    
    # 4. 匹配最相关的数据集
    dataset_profile = processing_plan.get("dataset_profile", {})
    user_requirement = step_spec.get("task_goal", "")
    
    matched_dataset = match_dataset(user_requirement, available_datasets, dataset_profile)
    
    if not matched_dataset:
        # 无法匹配，列出所有可用数据集供参考
        available_names = [d["name"] for d in available_datasets]
        raise ValueError(
            f"无法匹配相关数据集。可用数据集: {', '.join(available_names)}。"
            f"请在 step_spec.input_data_hint 中显式指定输入数据路径。"
        )
    
    # 5. 返回匹配的数据集路径
    return matched_dataset["path"]
```

## 路径验证

### 本地路径

```python
from pathlib import Path

def validate_local_path(path):
    """验证本地路径是否存在"""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"数据路径不存在: {path}")
    if not p.is_dir():
        raise NotADirectoryError(f"数据路径不是目录: {path}")
    return True
```

### 远程路径

远程路径（如集群上的路径）无法在本地验证，跳过验证，在生成的脚本中添加检查：

```python
# 生成的脚本中添加
import os
if not os.path.exists(INPUT_DATA_PATH):
    raise FileNotFoundError(f"输入数据不存在: {INPUT_DATA_PATH}")
```

## 输出路径

输出路径通常由用户指定或使用默认值：

```python
def resolve_output_path(step_spec):
    """解析输出路径"""
    if "output_path" in step_spec:
        return step_spec["output_path"]
    
    # 默认输出到当前目录
    return "./output/dataset"
```

## 完整示例

```python
# 场景1: 用户显式指定
step_spec = {
    "input_data_hint": "/data/my_custom_data",
    "output_path": "./processed_data"
}
# 结果: 使用用户指定的路径

# 场景2: 从配置推断
step_spec = {
    "task_goal": "构建 ERA5 气象数据集"
}
processing_plan = {
    "dataset_profile": {
        "domain": "earth",
        "description": "ERA5 reanalysis data"
    }
}
# 结果: /public/share/.../onedatasets/ERA5

# 场景3: 无法推断
step_spec = {
    "task_goal": "构建数据集"
}
processing_plan = {
    "dataset_profile": {
        "domain": "general"
    }
}
# 结果: 抛出异常，要求用户指定
```

## 注意事项

- 路径应使用绝对路径，避免相对路径的歧义
- 远程路径（如 `/public/share/...`）标记为远程，跳过本地验证
- 生成的脚本中应包含路径检查逻辑
- 在 observation 中记录最终解析的路径，便于调试
