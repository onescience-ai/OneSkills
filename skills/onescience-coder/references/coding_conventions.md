# OneScience 编码规范

## OneScience 包依赖规范

### 核心原则

**最小化依赖原则**：默认不依赖 onescience 包的安装，仅在构建科研工作流场景中，当 usage 明确使用 `from onescience import xx` 方式时，才允许依赖。

### 使用判断逻辑

编码时按以下逻辑判断：

**步骤 1：检查 usage 提供的使用方式**

**情况 A：usage 使用 `from onescience import xx` 方式**
- **构建科研工作流场景** → 严格遵照 usage，使用 `from onescience import xx`
- **其他所有场景** → 根据规格知识或源码知识自行实现，**不使用** `from onescience import xx`

**情况 B：usage 不使用 `from onescience import xx` 方式**
- **所有场景** → 按照 usage 中的要求使用

### 示例说明

```python
# 场景 1：usage 使用 from onescience import xx，当前是工作流场景
# ✅ 正确：严格遵照 usage
from onescience.models import SomeModel
model = SomeModel()

# 场景 2：usage 使用 from onescience import xx，当前是非工作流场景
# ❌ 禁止：直接导入
from onescience.models import SomeModel

# ✅ 正确：根据规格或源码自行实现
class SomeModel:
    """根据 onescience.models.SomeModel 的规格实现"""
    def __init__(self):
        # 根据规格文档或源码实现
        ...
```

### 实现要求

非工作流场景编码时：
- 查阅资源中的**规格知识**（接口定义、参数说明、行为描述）
- 参考资源中的**源码知识**（实现细节、算法逻辑）
- **独立实现**所需功能，不依赖 onescience 包

## 数据路径处理规范

### 强制要求

生成的代码**必须**通过以下方式获取数据路径和输出路径：

1. **函数参数**（优先）
2. **命令行参数**
3. **配置文件**

### 禁止做法

**严禁**使用以下方式：

```python
# ❌ 禁止：从环境变量推断或硬编码默认路径
source_dir = os.environ.get("ONESCIENCE_DATASETS_DIR", "/public/onestore")
source_dir = os.path.join(source_dir, "ERA5")

# ❌ 禁止：硬编码路径
source_dir = "/public/onestore/ERA5"
```

### 正确做法

```python
# ✅ 推荐：函数参数
def process_data(source_dir: str, output_dir: str, variables: List[str]):
    """
    Args:
        source_dir: 数据源目录路径
        output_dir: 输出目录路径
        variables: 处理的变量列表
    """
    data_path = os.path.join(source_dir, "data.nc")
    ...

# ✅ 推荐：命令行参数
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True, help="数据源目录")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    args = parser.parse_args()
    
    process_data(args.source_dir, args.output_dir)

# ✅ 可选：配置文件
config = yaml.safe_load(open("config.yaml"))
process_data(config["source_dir"], config["output_dir"])
```

## 原因说明

- 数据路径由上游技能（如 `onescience-data-builder`）解析并传入
- 环境变量和硬编码路径降低代码可移植性和可测试性
- 参数化设计使代码更灵活、更易维护
