# 数据处理脚本生成工作流

本文档定义 dataset-builder 在阶段1（生成脚本）的完整工作流程。

## 输入

- `step_spec`：包含构建目标、输入数据提示、输出路径、处理需求
- `processing_plan`：来自 data-profile 的数据画像和处理步骤
- `resource_bindings`（可选）：orchestrator 绑定的资源

## 工作流程

### 1. 解析输入数据路径

按照 `data_path_resolution.md` 定义的流程解析输入数据路径：

1. 如果用户显式指定 `input_data_hint`，直接使用
2. 否则：
   - 读取 `onescience.json` 获取 `ONESCIENCE_DATASETS_DIR`
   - 列出该目录下所有可用数据集
   - 根据用户需求匹配最相关的数据集路径
3. 无法匹配时返回错误，提示用户显式指定

详见 `data_path_resolution.md` 的完整实现。

### 2. 分析处理需求

从 `processing_plan` 中提取：
- **数据画像**：领域、模态、格式、维度、变量
- **处理步骤**：清洗、转换、对齐、特征提取、划分等
- **质量检查**：需要执行的检查项
- **输出规格**：格式、结构、元数据要求

### 3. 分析数据处理代码和关键接口

**在生成脚本前，必须先分析已有的数据处理代码，了解关键接口。**

```python
# 伪代码流程
if resource_bindings contains code_templates:
    # 1. 读取代码模板或示例代码
    code_files = read_resource_code_files(resource_bindings)
    
    # 2. 分析关键接口
    interfaces = analyze_key_interfaces(code_files)
    # interfaces 包含:
    # - 数据加载函数: load_era5_data(path, variables, time_range)
    # - 数据处理函数: preprocess_data(data, config)
    # - 数据保存函数: save_dataset(data, output_path, format)
    
    # 3. 提取接口签名和用法示例
    for interface in interfaces:
        extract_signature(interface)
        extract_usage_example(interface)
else:
    # 如果没有代码资源，使用通用模式
    interfaces = infer_generic_interfaces(dataset_profile)
```

### 4. 生成调用已有接口的脚本

根据分析的接口生成脚本，**调用已有函数而非重新实现**：

```python
#!/usr/bin/env python3
"""
数据集构建脚本
自动生成 by onescience-dataset-builder
"""

import os
import sys
from pathlib import Path

# 添加数据处理代码路径到 sys.path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# 导入已有的数据处理模块（从代码分析中获取）
from <module_name> import load_data, preprocess_data, save_dataset

# 数据路径
INPUT_DATA_PATH = os.getenv("INPUT_DATA_PATH", "<默认路径>")
OUTPUT_DATA_PATH = os.getenv("OUTPUT_DATA_PATH", "<默认路径>")

def main():
    print(f"输入数据: {INPUT_DATA_PATH}")
    print(f"输出路径: {OUTPUT_DATA_PATH}")
    
    # 调用已有接口加载数据
    data = load_data(
        path=INPUT_DATA_PATH,
        # 参数从 processing_plan 中提取
        variables=["t2m", "tp"],
        time_range=["2020-01-01", "2022-12-31"]
    )
    
    # 调用已有接口处理数据
    processed_data = preprocess_data(
        data=data,
        config={
            "crop_region": {"lat": [20, 50], "lon": [100, 130]},
            "resample": "1D"
        }
    )
    
    # 调用已有接口保存
    save_dataset(
        data=processed_data,
        output_path=OUTPUT_DATA_PATH,
        format="netcdf"
    )
    
    print("数据集构建完成")

if __name__ == "__main__":
    main()
```

### 5. 脚本生成策略

**优先级：代码分析 > 领域模板 > 通用实现**

1. **基于代码分析**（优先）：
   - 从 `resource_bindings` 读取已有代码
   - 分析关键接口和用法
   - 生成调用这些接口的脚本

2. **基于领域模板**（次选）：
   - 如果有领域特定模板（earth、biology等）
   - 使用模板并填充参数

3. **通用实现**（兜底）：
   - 使用标准库（pandas、xarray等）
   - 生成基础的加载-处理-保存流程

**参数化**：
- 输入输出路径通过环境变量传递
- 处理参数从 `processing_plan` 提取

### 6. 保存脚本

**保存位置**：数据处理代码所在目录（从 `resource_bindings` 获取或使用当前工作目录）

```python
# 确定保存路径
if resource_bindings:
    # 从 resource_bindings 中获取数据处理代码路径
    code_path = get_code_path_from_resources(resource_bindings)
    script_dir = Path(code_path).parent
else:
    # 使用当前工作目录
    script_dir = Path.cwd()

# 保存脚本
script_path = script_dir / "build_dataset.py"
write_file(script_path, script_content)
chmod(script_path, 0o755)  # 添加执行权限
```

### 7. 生成脚本执行说明

在脚本顶部添加注释说明如何执行：

```python
"""
执行方式:
  export INPUT_DATA_PATH=/path/to/input
  export OUTPUT_DATA_PATH=/path/to/output
  python build_dataset.py

或通过 onescience-runtime 提交到集群
"""
```

### 8. 返回交接物给 orchestrator

```yaml
execution_result:
  skill: onescience-dataset-builder
  status: success
  artifacts:
    script_path: ./build_dataset.py
    input_data_path: /public/share/.../onedatasets/ERA5
    output_data_path: ./output/era5_processed
  observation:
    summary: 已生成数据集构建脚本
    completed:
      - 数据路径解析完成
      - 分析了已有数据处理代码，识别关键接口
      - 生成调用接口的脚本
    data_source_info:
      resolved: true
      onescience_datasets_dir: /public/share/.../onedatasets/
      final_input_path: /public/share/.../onedatasets/ERA5
    next_recommendation: 调用 onescience-runtime 执行脚本
```

## 错误处理

- **数据路径无法解析**：返回 failed，在 observation 中说明原因
- **处理步骤不明确**：返回 partial，标记需要用户补充的信息
- **缺少必要资源**：返回 failed，列出缺失的资源

## 注意事项

- 生成的脚本应该是**自包含**的，包含所有必要的导入和函数定义
- 脚本应该有清晰的日志输出，便于 runtime 监控执行进度
- 脚本执行失败时应返回非零退出码
- 避免硬编码路径，使用环境变量或命令行参数
