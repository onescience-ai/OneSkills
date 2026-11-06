# File Handoff Contract

文件交接模式是多技能任务中 orchestrator 与 executor 之间的数据传递机制；`autonomous_mode` 下强制使用。它通过文件系统传递 step_handoff 和 execution_result，使 executor 可在原生独立上下文或非持久化临时技能上下文中运行，避免 orchestrator 上下文膨胀。

## 核心原则

1. **上下文隔离**：executor 读取 handoff 文件获取任务；使用原生独立调用或只挂载当前技能的非持久化上下文，不继承无关技能正文。
2. **持久化中间产物**：handoff 文件和 result 文件作为中间产物，可审查、可回放。
3. **自动清理**：所有步骤完成后，handoff 目录归档到 `.onescience/archive/{task_id}/`。

## Handoff 文件格式

路径：`.onescience/handoff/step_{step_id}.yaml`

```yaml
step_id: "step-3"
attempt: 2
execution_skill: "onescience-coder"
step_goal: "实现 ResNet 模型定义"
execution_flags:
  autonomous_mode: true
  training_allowed: false
completion_scope: code_delivery
step_wallclock_budget_seconds: 1800
task_context:
  user_goal: "复现论文 2406.01465"
  constraints:
    - "使用 PyTorch 框架"
    - "支持 GPU 训练"
  relevant_artifacts:
    - path: ".paper2code_work/2406.01465/reproduction_spec.md"
      kind: "reproduction_spec"
      sha256: "<磁盘规格文件的 SHA-256>"
      description: "唯一论文复现规格，由目标 executor 按需读取并校验"
resource_bindings:
  - type: "model_card"
    path: "assets/matchem/models/deepmd"
    purpose: "模型架构参考"
inputs:
  paper_repro_handoff: true
  reproduction_spec_path: ".paper2code_work/2406.01465/reproduction_spec.md"
  reproduction_spec_sha256: "<磁盘全文的 SHA-256>"
  key_unresolved: []
  target_dir: "models/"
  target_file: "models/resnet.py"
  parameters:
    num_classes: 1000
    variant: "resnet50"
required_outputs:
  - "ResNet 模型类定义文件"
  - "支持论文中的三种配置变体 (resnet18/resnet50/resnet101)"
completion_criteria:
  - "模型类定义完整，可通过 import 导入"
  - "支持三种配置变体"
  - "代码可通过静态检查"
```

以上为结构示例；`training_allowed=false` 的代码交付任务不传训练 `tier_config`，不激活训练
层级。已授权训练时才按分层契约添加 tier_config。论文规格通过路径和 SHA-256 作为任务产物
交接，由目标 executor 在其技能执行上下文中读取并校验；不创建旧版 `coder_task_description.md`。
每次交接携带会话持续授权、禁止事项和输出根目录，不能只传任务标题。

## Result 文件格式

路径：`.onescience/handoff/step_{step_id}_result.yaml`

```yaml
step_id: "step-3"
attempt: 2
execution_skill: "onescience-coder"
status: "success"
failure_category: null
completion_scope: code_delivery
result_identity: not_a_result
artifacts:
  - path: "models/resnet.py"
    description: "ResNet 模型实现"
    lines: 156
observation:
  summary: "已完成 ResNet 模型定义，支持三种配置变体"
  completed:
    - "模型类定义"
    - "三种配置变体 (resnet18/resnet50/resnet101)"
    - "forward 方法实现"
  risks: []
  next_recommendation: "代码交付完成；本次禁止训练，运行/论文指标未验证"
events:
  - event_type: "repair_attempted"
    timestamp: "2026-08-12T10:30:01Z"
    description: "修复了 import 路径错误"
  - event_type: "retry_started"
    timestamp: "2026-08-12T10:31:00Z"
    description: "第 2 次重试"
```

status 取值：
- `success`：步骤完全完成
- `partial`：部分完成，有缺失项
- `failed`：执行失败
- `blocked`：遇到阻断，无法继续

## Orchestrator 侧的读写流程

### 写入 handoff

```
1. 选择 Next Step Spec
2. 将 step_handoff（含 attempt、step_wallclock_budget_seconds 字段）序列化为 YAML
3. 创建 .onescience/handoff/ 目录（如不存在）
4. 先写入临时文件 .onescience/handoff/step_{step_id}.yaml.tmp
5. 确保内容完整写入（flush/fsync）
6. 原子重命名：将 .tmp 文件 rename 为 .onescience/handoff/step_{step_id}.yaml
```

### 写入 task_state.json

```
1. 将当前完整 Task State（含 events、global_plan_version、observations 等全部字段）序列化为 JSON
2. 先写入临时文件 .onescience/task_state.json.tmp
3. 确保内容完整写入（flush/fsync）
4. 原子重命名：将 .tmp 文件 rename 为 .onescience/task_state.json
```

### 读取 result

```
1. Wait for executor 完成
2. 读取 .onescience/handoff/step_{step_id}_result.yaml
3. Parse execution_result（含 attempt、failure_category、events 字段）
4. 只将状态、result_identity、artifacts、observation 和 events 写入 Task State；完整日志和大文本保留在文件产物中
5. 原子写入 .onescience/task_state.json
```

### 归档

```
1. 所有步骤完成后
2. 创建 .onescience/archive/{task_id}/ 目录
3. 移动所有 handoff 文件和 result 文件到归档目录
4. 删除 .onescience/handoff/ 目录
```

## Executor 侧的读写流程

### 读取 handoff

执行器在启动时应：

1. 检查 `.onescience/handoff/` 目录是否存在对应的 `step_{step_id}.yaml`
2. 若存在，从文件读取 `step_handoff`
3. 若不存在，使用上下文传入的 `step_handoff`

### 写入 result

执行完毕后：

1. 将 `execution_result`（含 attempt、failure_category、events 字段）序列化为 YAML
2. 先写入临时文件 `.onescience/handoff/step_{step_id}_result.yaml.tmp`
3. 确保内容完整写入（flush/fsync）
4. 原子重命名：将 .tmp 文件 rename 为 `.onescience/handoff/step_{step_id}_result.yaml`
5. 同时在上下文输出中返回 `execution_result` 摘要（供 orchestrator 快速判断），不返回技能正文、references 或完整执行转录

## 目录结构

```
.onescience/
├── task_state.json                    ← 当前 Task State
├── handoff/                           ← 当前步骤交接文件
│   ├── step_1.yaml
│   ├── step_1_result.yaml
│   ├── step_2.yaml
│   ├── step_2_result.yaml
│   └── ...
└── archive/                           ← 已完成任务的归档
    └── paper-repro-2406.01465/
        ├── task_state_final.json
        ├── step_1.yaml
        ├── step_1_result.yaml
        └── ...
```

## 与上下文 handoff 的关系

原生智能体 / skill 调用或非持久化技能挂载负责激活执行上下文，文件 handoff 负责传递步骤数据：

- **多技能任务**：默认使用文件 handoff；`autonomous_mode=true` 时强制使用
- **单技能单步骤任务**：可直接把结构化 `step_handoff` 传入当前技能执行上下文
- **已有 handoff 文件**：executor 优先读取文件，不再把同一大文本复制进调用上下文

## 幂等性与重试安全

- 每个 handoff 文件和 result 文件通过 `step_id + attempt` 组合唯一标识一次执行。
- orchestrator 在重新执行同一 `step_id` 时必须递增 `attempt`。
- executor 检查 `.onescience/handoff/step_{step_id}_result.yaml` 时：若 `result.attempt == handoff.attempt`，该步骤已执行完成，可直接复用结果，不重复执行。
- 原子写入（`.tmp → rename`）确保即使在写入中途进程崩溃，也只会留下 `.tmp` 文件，不会产生损坏的正式文件。
