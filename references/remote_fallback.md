# Remote Fallback

本文件用于统一说明：当用户未配置远程环境、只给出模糊远程描述，或远程上下文不完整时，应该如何降级、阻断与提示。

如果需要直接套用标准回复结构，读取 `./remote_status_template.md`。
如果需要参考最终成品示例，读取 `./remote_status_examples.md`。

## 核心原则

1. 能降级就降级，不要把远程缺失当成所有任务的总失败
2. 只有远程必需阶段才会被远程环境缺失阻断
3. 缺什么就报什么，不要猜测 Host、队列、module 或 conda 环境
4. 对模糊远程描述，先做归一化识别；能补齐就补齐，补不齐再最小追问

## 什么时候可以继续

### 纯代码任务

如果用户只是要求实现、改造、生成代码，即使没有远程环境，也可以继续：

- 走 `onescience-coder`
- 不强行进入 `onescience-runtime`
- 不强行进入 `onescience-installer`

### 远程信息不完整，但任务暂时不需要远程执行

如果用户只是提到“后面可能要跑到集群”“可能要适配某个 DCU 环境”，但当前交付仍是代码：

- 优先走 `onescience-hardware -> onescience-coder`
- 若无法确认远程事实，允许只生成保守代码方案
- 明确说明哪些远程参数将在运行阶段再确认

## 什么时候必须阻断

以下任务如果没有可用远程环境事实，应直接阻断远程阶段：

- `onescience-runtime`
- `onescience-installer`
- 依赖远程执行的 `onescience-debug`

常见阻断缺口包括：

- Host 未知
- 队列 / 分区未知
- module / conda 约束未知
- `onescience.json` / `tpl.slurm` 缺失（运行任务）
- SCnet 区域 / 队列不可识别（`scnet_mcp` 运行任务）

## 模糊远程描述的处理

如果用户只给出模糊描述，例如：

- “昆山 DCU”
- “某个 GPU 机”
- “超算环境”

处理顺序：

1. 把它当作环境线索，而不是完整配置
2. 先交给 `onescience-hardware` 读取 `~/.ssh/config` 并做轻量只读探测
3. 若只有一个合理候选，可继续
4. 若有多个候选或仍然不清楚，则只追问最小缺失信息

## 建议状态

统一用下面几类状态表达当前可执行性：

- `ok`：信息完整，可以继续当前链路
- `partial_context`：已识别部分远程信息，但还缺关键字段
- `need_clarification`：远程描述过于模糊，需要用户补最小信息
- `blocked`：当前阶段必须依赖远程信息，但缺失导致无法继续

## 建议输出格式

至少给出：

- `status`
- `recognized`
- `missing`
- `can_continue_locally`
- `next_action`

其中：

- `recognized`：已识别出的 Host / 平台 / 队列 / 路径等线索
- `missing`：当前阶段真正缺失的字段
- `can_continue_locally`：是否还能停留在本地或代码阶段继续
- `next_action`：下一步进入 `coder` / `hardware` / `runtime` / `installer` / `debug`

## 常见场景

### 场景 1：没有任何远程配置，但用户只想写代码

- `status`: `ok`
- `can_continue_locally`: `true`
- `next_action`: `onescience-coder`

### 场景 2：没有远程配置，但用户要求直接提交作业

- `status`: `blocked`
- `can_continue_locally`: `false`
- `next_action`: `onescience-hardware`

### 场景 3：只知道“某个 DCU 集群”，但没给 Host

- `status`: `need_clarification`
- `can_continue_locally`: 视任务而定
- `next_action`: `onescience-hardware`

### 场景 4：已有 Host，但缺少 `onescience.json`

- 对纯代码任务：继续
- 对运行任务：`blocked`

### 场景 5：明确要求提交到 SCnet，但缺少区域或队列

- 若当前环境可调用 SCnet MCP：允许继续，由 `onescience-runtime` 的 `scnet_mcp` 通道自行发现
- 若当前环境无法调用 SCnet MCP：`blocked`

## 禁止事项

- 不要把远程环境缺失扩大成所有链路失败
- 不要在缺少远程事实时伪造 Host、队列或路径
- 不要因为“后面可能远程运行”而阻塞当前纯代码任务
- 不要自动在多个 Host 候选中静默选择一个
