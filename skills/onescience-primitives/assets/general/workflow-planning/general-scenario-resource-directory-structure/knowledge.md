# OneScience 场景资源文件目录结构规范

## 适用范围
适用于所有 OneScience 场景资源文件的组织、发现和检索。

## 目录结构
### 顶层目录
```
scenario/
├── origin/           # 原始场景文件
├── normalized-tables.json  # 标准化表格
├── task-index.json   # 任务索引
└── task-index.jsonl  # 任务索引（JSON Lines格式）
```

### 领域子目录
```
scenario/origin/
├── bio/              # 生物科学领域
├── cfd/              # 计算流体动力学领域
├── climate/          # 气候科学领域
├── matchem/          # 材料与化学领域
└── general/          # 通用领域
```

### 场景文件组织
```
scenario/origin/bio/
├── B70.json          # 场景ID命名（推荐）
├── 单纯形流匹配的调控DNA序列设计.json  # 场景名称命名（可选）
└── ...
```

## 文件命名规则
### 场景JSON文件
1. **ID命名法**（推荐）：`<场景ID>.json`
   - 示例：`B70.json`, `C12.json`, `M5.json`
   - 格式：大写字母 + 数字

2. **名称命名法**（可选）：`<场景名称>.json`
   - 示例：`单纯形流匹配的调控DNA序列设计.json`
   - 要求：UTF-8编码，特殊字符需转义

### 索引文件
1. `task-index.json`：JSON格式，包含所有任务元数据
2. `task-index.jsonl`：JSON Lines格式，每行一个任务

## 场景JSON文件内容
### 必填字段
```json
{
  "id": "string",
  "name": "string",
  "domain": "string",
  "workflow": "string",
  "prompt": "string"
}
```

### 字段规范
| 字段 | 类型 | 描述 | 必填 |
|------|------|------|------|
| id | string | 场景唯一标识 | 是 |
| name | string | 场景名称 | 是 |
| domain | string | 所属领域 | 是 |
| workflow | string | 工作流描述（含步骤） | 是 |
| prompt | string | 任务提示词 | 是 |
| model | array | 推荐模型列表 | 否 |
| tools | array | 推荐工具列表 | 否 |
| hpc | array | HPC软件列表 | 否 |

## 检索策略
### 1. 精确匹配检索
```python
# 按场景ID检索
scenario_file = f"scenario/origin/{domain}/{scenario_id}.json"

# 按场景名称检索
scenario_file = f"scenario/origin/{domain}/{scenario_name}.json"
```

### 2. 模糊搜索检索
```python
# 使用glob递归搜索
import glob
pattern = f"scenario/origin/{domain}/**/*.json"
files = glob.glob(pattern, recursive=True)
```

### 3. 索引检索
```python
# 从task-index.json检索
with open("scenario/task-index.json") as f:
    tasks = json.load(f)
    for task in tasks["tasks"]:
        if task["id"] == scenario_id:
            return task
```

## 流程节点
1. **确定领域** → 2. **选择检索策略** → 3. **执行检索** → 4. **验证文件** → 5. **读取内容**

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 文件格式 | JSON | [规范] | 标准JSON格式 |
| 编码 | UTF-8 | [规范] | 支持中文等Unicode字符 |
| 目录深度 | 3层 | [规范] | domain/category/name |
| 文件大小 | <1MB | [建议] | 场景文件不宜过大 |

## 边界与分流
### 异常处理
- 文件不存在：返回空结果或提示用户
- JSON解析失败：记录错误并跳过
- 编码错误：尝试其他编码（如GBK）

### 降级策略
- 无领域子目录时：搜索所有领域
- 无场景文件时：从索引文件生成最小场景

## 质量检查
1. 文件存在性检查
2. JSON格式有效性
3. 必填字段完整性
4. 领域一致性检查
5. 文件编码正确性

## 回退策略
1. 无场景文件时：从task-index.json重建
2. 索引文件损坏时：重新生成索引
3. 目录结构错误时：自动修复

## 资源召回建议
- 需要场景详情时：召回对应场景JSON文件
- 需要任务索引时：召回task-index.json
- 需要领域概览时：召回领域profile文档

## 证据来源
[1] OneScience Scenario Resource Organization v1.2, 内部文档, 2026
[2] scenario/task-index.json 实际结构, 项目仓库