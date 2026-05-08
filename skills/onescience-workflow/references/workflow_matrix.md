# Workflow Matrix

本文件用于给 `onescience-workflow` 提供更稳定的用户任务入口决策表。

## 顶层判断问题

先问自己：

1. 用户真正想完成什么科研工作？
2. 当前处在数据、模型、运行、评估还是全流程阶段？
3. 这是不是一个只需规划、不需执行的请求？

## 统一入口请求

### `general-onescience-request`

适用信号：

- "使用 onescience 技能"
- "使用 onescience"
- "使用 oneskills"
- "启动 onescience"
- "启动 oneskills"
- "打开 onescience"
- "打开 oneskills"
- "进入 onescience"
- "进入 oneskills"
- "onescience 模式"
- "oneskills 模式"

含义：
用户希望使用 OneScience / OneSkills 体系完成科研任务，但尚未明确具体目标。

默认行为：

1. 识别为 `workflow_type=general_onescience_request`
2. 主动询问用户具体想完成什么科研任务
3. 提供常见工作流选项引导用户
4. 不要直接拉起完整执行链

引导话术示例：

```
您好！我已准备好协助您完成科研任务。请告诉我您具体想做什么，例如：

- 接入数据（如 ERA5、CMIP、海洋观测数据等）
- 改造模型结构或编写训练脚本
- 连接远程环境并提交运行
- 验证实验结果或排查日志异常
- 梳理完整科研流程

我会根据您的具体需求，选择合适的工具和流程来协助您。
```

默认链路：

`onescience-workflow`（停留在本 skill，等待用户明确目标后再下钻）

## 用户友好的六类工作流

### 1. `workflow-planning`

适用信号：

- “帮我梳理这个科研任务怎么做”
- “这个项目应该按什么流程推进”
- “不同人员该怎么分工”

默认链路：

`onescience-workflow -> onescience-role`

### 2. `data-task`

适用信号：

- “接入 ERA5 / CMIP / 海洋数据 / 遥感数据”
- “写 DataPipe / dataset / 预处理”
- “梳理变量、时空范围、读取入口”

默认链路：

`onescience-workflow -> onescience-role -> onescience-skill -> onescience-coder`

### 3. `model-task`

适用信号：

- “改模型结构”
- “补训练脚本 / 推理入口 / 配置”
- “把数据任务落成可训练代码”

默认链路：

`onescience-workflow -> onescience-role -> onescience-skill -> onescience-coder`

### 4. `runtime-task`

适用信号：

- “连远程环境并提交运行”
- “读取 onescience.json 并跑起来”
- “提交到 SCnet 跑一下”
- “安装远程环境或准备提交脚本”

默认链路：

- 安装：`onescience-workflow -> onescience-role -> onescience-skill -> onescience-hardware -> onescience-installer`
- 运行：`onescience-workflow -> onescience-role -> onescience-skill -> onescience-hardware -> onescience-runtime`
- SCnet / MCP 提交：`onescience-workflow -> onescience-role -> onescience-skill -> onescience-runtime`

如果上游远程环境进一步被归一化到某个 `backend_id`，还应在工作流交接中附带：

- `backend_id`
- `backend_status`
- `execution_readiness`

### 5. `evaluation-task`

适用信号：

- “验证实验结果”
- “对比指标”
- “排查日志 / loss / 运行异常”

默认链路：

- 仅分析：`onescience-workflow -> onescience-role -> onescience-skill -> onescience-debug`
- 缺远程事实：`onescience-workflow -> onescience-role -> onescience-skill -> onescience-hardware -> onescience-debug`

### 6. `end-to-end-task`

适用信号：

- “从数据接入到训练运行全做完”
- “帮我串起读取、建模、运行、验证”

默认链路：

`onescience-workflow -> onescience-role -> onescience-skill -> onescience-hardware -> onescience-coder -> onescience-runtime -> onescience-debug`

## 用户说法到工作流

- “使用 onescience 技能、使用 oneskills、启动 onescience / oneskills、打开 onescience / oneskills、进入 onescience / oneskills" -> `general-onescience-request`
- “接入、读取、DataPipe、dataset、预处理” -> `data-task`
- “改模型、训练、推理、配置、脚本” -> `model-task`
- “提交、运行、集群、slurm、SCnet、远程环境、安装” -> `runtime-task`
- “评估、验证、对比、排查、debug" -> `evaluation-task`
- “从头到尾、全流程、串起来、做完整闭环” -> `end-to-end-task`
- “梳理流程、拆任务、分工、怎么推进” -> `workflow-planning`

## 输出给角色层的标准交接

进入 `onescience-role` 前，至少整理：

- 用户目标摘要
- 检测到的领域画像
- 当前工作流类型
- 当前阶段最关心的交付
- 是否涉及远程环境
- 已识别与缺失的前置信息
- 如已识别：`backend_id`、`backend_status` 与 `execution_readiness`

## 常见误设计

### 错误 1：让用户先选内部角色

后果：

- 不符合用户真实表达方式
- 降低顶层入口可用性

### 错误 2：每个领域复制一套执行技能

后果：

- 技能数量膨胀
- 维护成本高
- 执行逻辑容易漂移

### 错误 3：顶层入口直接替代执行层

后果：

- 任务理解和具体执行混杂
- 无法稳定复用底层能力

### 错误 4：把 OneSkills 品牌入口当成具体执行技能

后果：

- 用户只是在请求进入 OneScience 体系时，被误路由到执行层
- 在目标未明确前拉起不必要的代码、运行或调试链路

正确做法：

- `oneskills` 是入口别名，不是新的执行 skill
- 只有用户明确点名 `onescience-coder`、`onescience-runtime` 等具体 skill 时，才直接进入对应 skill
