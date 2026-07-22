# Execution Handoff Contract

执行技能（`type=executor`）只接收当前步骤的明确任务，不重新规划整个用户目标。

## Handoff 格式

```yaml
step_handoff:
  step_id: <步骤ID>
  execution_skill: <执行技能名称>
  step_goal: <本步骤目标>
  task_context:
    user_goal: <用户最终目标>
    constraints: <约束列表>
    relevant_artifacts: <相关产物>
  resource_bindings:
    - path: <资源路径>
      type: <资源类型>
      purpose: <用途>
  inputs: <执行所需输入，根据任务类型可为空或包含具体字段>
  required_outputs: <要求输出>
  completion_criteria: <完成标准>
```

## 执行技能返回格式

```yaml
execution_result:
  skill: <执行技能名称>
  status: <success | partial | failed | blocked>
  artifacts:
    <产物清单>
  observation:
    summary: <执行摘要>
    completed: <已完成内容>
    missing: <缺失项>
    risks: <风险>
    next_recommendation: <下一步建议>
```

## 常见执行技能的职责（仅用于 handoff 便利摘要，不是权威边界来源）

本节只用于帮助上游快速组织 handoff 字段，不是 orchestrator 判定 executor 职责边界、排他范围或明确不负责事项的权威来源。

- 最终 scope / exclusivity / non-responsibility 判断，必须回到对应 executor 的完整 `SKILL.md`。
- 若本节简写摘要与 executor 自身 `SKILL.md` 冲突，以 executor 自身 `SKILL.md` 为准。
- 技能名称、frontmatter `description` 和本节摘要都只能用于初筛，不得替代完整 `SKILL.md` 阅读来做最终任务拆分。

### onescience-coder
- 接收：step spec、资源路径、目标目录、运行时参数（数据源路径、输出路径等）
- 执行：生成或修改代码
- 返回：代码产物、静态检查结果、未验证风险
- **重要**：生成的代码必须从函数参数、命令行参数或配置文件读取路径，不得硬编码或从环境变量推断默认值

示例 handoff：
```yaml
step_handoff:
  step_id: "implement_data_processing"
  execution_skill: onescience-coder
  step_goal: "实现 ERA5 数据处理脚本"
  inputs:
    parameters:
      source_dir: "/public/onestore/ERA5"
      output_dir: "./processed_data"
      variables: ["temperature", "pressure"]
      time_range: ["2020-01-01", "2020-12-31"]
  required_outputs:
    - "数据处理脚本，从参数读取 source_dir 和 output_dir"
    - "生成的代码应支持命令行参数或配置文件传入路径"
```

生成代码示例：
```python
# 正确：从参数获取
def process_data(source_dir: str, output_dir: str, variables: List[str]):
    ...

# 错误：硬编码或环境变量推断
source_dir = os.environ.get("ONESCIENCE_DATASETS_DIR", "/public/onestore")
source_dir = os.path.join(source_dir, "ERA5")
```

### onescience-paper-repro
- 接收：论文资源路径
- 执行：解析论文、生成复现规格
- 返回：复现规格、方法抽取结果、coder 任务描述

### onescience-runtime
- 接收：可运行入口、配置、执行目标
- 执行：preflight、execute、status、logs、diagnose
- 返回：运行证据、失败分类

### onescience-installer
- 接收：环境缺口、目标后端、安装 profile
- 执行：安装、修复或验证环境
- 返回：安装结果、环境状态

## Observation 处理

- success：写入 artifacts，交给 orchestrator 基于最新 Task State 判断是否需要继续规划下一步
- partial：记录已完成部分、缺失项和残余风险；orchestrator 必须先回到 observation/planning，再重新选择一个新的 next_step
- failed：记录失败证据；orchestrator 必须先完成 observation，再决定 repair、replan 或 blocked，不能直接串行调用下一个 executor
- blocked：记录阻断原因和所需用户输入；只有阻断被消除后才允许继续

- 执行技能返回的结果只表示当前步骤的观察输入，不授权直接跳转到下一条 executor 链路。

