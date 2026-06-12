# Workflow Matrix

本文件用于给 `onescience-workflow` 提供更稳定的用户任务入口决策表。

## 顶层判断问题

先问自己：

1. 用户真正想完成什么科研工作？
2. 当前处在数据、模型、运行、评估还是全流程阶段？
3. 这是不是一个只需规划、不需执行的请求？

## 当前下一跳与规划阶段规则

当用户明确说“先不要写代码”“只告诉我技能路线”“先只看路线”“先做规划”“先看怎么走”，或当前请求尚未授权实现、运行、提交、安装时，优先识别为规划阶段。

此时即使命中了 `data-task`、`model-task`、`runtime-task`、`evaluation-task` 或 `end-to-end-task` 的关键词，也不要展开默认完整链路。输出只应包含最小路由信息：

- 当前所在层：`onescience-workflow`
- 当前下一跳：通常是 `onescience-role`
- 如需说明后续方向，最多给出一个 `future_execution_entry`

在规划阶段：

- 不要把 `onescience-skill` 写成当前 pipeline 阶段
- 不要把 `onescience-coder`、`onescience-runtime` 或 `onescience-installer` 写成当前 `next_skill`
- 不要创造不存在的 skill，例如 `onescience-test`
- 如果识别到 `detected_domain=earth`，交接摘要应要求后续优先进入 `onescience-role` 的 `earth` 路径

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

规划阶段：

- 当前下一跳只写 `onescience-role`
- 未来执行入口最多写 `onescience-coder`
- 不要提前展开 `onescience-runtime` 或安装/验证链路

### 3. `model-task`

适用信号：

- “改模型结构”
- “补训练脚本 / 推理入口 / 配置”
- “把数据任务落成可训练代码”

默认链路：

`onescience-workflow -> onescience-role -> onescience-skill -> onescience-coder`

规划阶段：

- 当前下一跳只写 `onescience-role`
- 未来执行入口最多写 `onescience-coder`
- 不要提前展开运行、诊断或安装链路

### 4. `runtime-task`

适用信号：

- “连远程环境并提交运行”
- “读取 onescience.json 并跑起来”
- “提交到 SCnet 跑一下”
- “安装远程环境或准备提交脚本”

默认链路：

- 安装：`onescience-workflow -> onescience-role -> onescience-skill -> onescience-installer`
- 运行：`onescience-workflow -> onescience-role -> onescience-skill -> onescience-runtime`
- SCnet / MCP 提交：`onescience-workflow -> onescience-role -> onescience-skill -> onescience-runtime`

规划阶段：

- 当前下一跳只写 `onescience-role`
- 若用户只是说后续可能运行或提交，只在 `workflow_handoff` 里保留运行约束
- 不要把 `onescience-runtime` 当成当前 `next_skill`，除非用户明确要求现在运行、提交、查状态或下载日志

补充说明：

- `onescience-runtime` 公开承担 `discover -> preflight -> execute -> diagnose`
- `onescience-installer` 公开承担安装与修复，并共享同一套 `execution_profile`

如果上游远程环境已经由 runtime / installer 的实际接入通道确认，并进一步归一化到某个 `backend_id`，还应在工作流交接中附带：

- `backend_id`
- `backend_status`
- `execution_readiness`

其中：

- `stable_backend` 可按标准 runtime 链继续推进
- `planned_backend` 也可继续进入 runtime，但必须在交接中显式保留“planned”语义
- `unsupported_for_now` 才应在执行阶段阻断并转向说明或安装链路

### 5. `evaluation-task`

适用信号：

- “验证实验结果”
- “对比指标”
- “排查日志 / loss / 运行异常”

注意：

- 如果用户说的是“对比多个模型训练效果”，但尚未生成训练代码、尚未运行实验、也没有已有日志或指标结果，应优先归入 `model-task` 或 `end-to-end-task`；只有已有结果、日志或指标需要分析时，才归入 `evaluation-task`。

默认链路：

- 仅分析：`onescience-workflow -> onescience-role -> onescience-skill -> onescience-runtime`
- 缺远程事实：`onescience-workflow -> onescience-role -> onescience-skill -> onescience-runtime`

规划阶段：

- 当前下一跳只写 `onescience-role`
- 若用户只是询问路线，不要提前进入 `onescience-runtime`

### 6. `end-to-end-task`

适用信号：

- "从数据接入到训练运行全做完"
- "帮我串起读取、建模、运行、验证"

默认链路：

`onescience-workflow -> onescience-role -> onescience-skill -> onescience-coder -> onescience-runtime`

规划阶段：

- 当前下一跳只写 `onescience-role`
- 只要求 role 层先拆阶段
- 不要一次性展开完整执行 pipeline

### 7. `paper2code-task`

适用信号：

- "复现这篇论文"
- "实现这篇论文 / implement this paper"
- 粘贴 arxiv 链接或论文 ID（如 `https://arxiv.org/abs/2106.09685` 或 `2106.09685`）
- 粘贴论文关键内容
- "根据论文生成代码"
- 只给论文标题，例如 "复现 FENGWU: PUSHING THE SKILLFUL GLOBAL MEDIUM-RANGE WEATHER FORECAST BEYOND 10 DAYS LEAD"
- "paper to code"
- "论文代码复现"

含义：
用户希望将一篇学术论文（通常来自 arxiv、PDF、本地文件、标题或粘贴内容）转化为可运行的 OneScience 复现代码。这是一个端到端的结构化流程：论文获取与解析 → 复现信息抽取 → 歧义审计 → 生成审计用 `reproduction_spec.md` 与自包含 `coder_task_description.md` → 由 `onescience-coder` 只消费 `coder_task_description.md` 生成代码。

优先级：

- 只要出现上述论文复现信号，本任务必须归入 `paper2code-task`，即使同时出现模型名、训练/推理、保存目录、代码保存等词。
- 不要把 `user_intent` 改写为“获取官方代码”“下载官方仓库”“克隆论文代码”。
- 不要把 `workflow_type` 写成 `model-task`；普通 `model-task` 只适用于用户明确要求改造/训练/推理已有本地模型代码，而不是从论文重新生成实现。
- `代码保存至 X` 只表示生成代码落点，不表示到 X 克隆或解压已有仓库。

默认行为：

1. 识别为 `workflow_type=paper2code_task`
2. 从用户输入中提取 `paper_source`（支持 arxiv ID/URL、本地 PDF、粘贴文本、已知论文名；若只给论文标题，先解析论文/arxiv 来源，若能提取 arxiv ID 则保留为 `arxiv_id`）
3. 从用户输入中提取运行模式（minimal / full / educational，默认 minimal）
4. 从用户输入中提取框架偏好（pytorch / jax / numpy，默认 pytorch）
5. 设置 `workflow_type=paper2code_task`、`task_method=paper2code`、`domain_task_family=paper-reproduction`
6. 尽量识别真实科学领域并写入 `domain_route`（如 `earth`、`biology`、`materials`、`cfd`；无法判断时用 `general-science`）
7. 产出完整交接摘要，交给 `onescience-role` 做进一步的阶段拆解与角色链规划

默认链路：

`onescience-workflow -> onescience-role -> onescience-skill -> onescience-paper-repro -> onescience-coder`

规划阶段：

- 当前下一跳只写 `onescience-role`
- 角色层会按论文复现前处理流水线（Paper Acquisition → Reproduction Extraction → Ambiguity Audit → Coder Task Description）做进一步拆解
- 未来执行入口默认为 `onescience-paper-repro`，随后由它交接 `onescience-coder`

特殊说明：

- 论文复现任务可能涉及网络请求（下载 PDF、获取 arxiv 元数据），也可能来自本地 PDF、粘贴文本或已知论文名；workflow 交接摘要中应统一使用 `paper_source`
- 如果用户没有提供任何可解析论文来源，且无法从本地模型卡或 Catalog 中确认已知论文，workflow 层应引导用户提供，不要直接进入角色层
- Mode 和 Framework 参数影响最终代码生成的范围与风格，应在交接中显式传递
- 用户指定的保存目录是本轮生成复现代码的落点，不是官方或第三方已实现代码仓库的 clone / copy 目标
- Workflow 阶段禁止使用 GitHub/GitLab/Bitbucket/code repository 查询来处理 paper2code；只能解析论文/arxiv/PDF/粘贴文本等论文来源
- 不要把"找到官方代码仓库并下载"判断为 `paper2code-task` 完成；这属于错误执行路径

禁止查询示例：

- `FengWu ... GitHub code`
- `official code repository`
- `site:github.com <paper name>`
- `OpenEarthLab FengWu model code`

禁止字段示例：

- `user_intent=获取官方代码并保存至 temp_will_del/cases/fengwu`
- `workflow_type=model-task`
- `workflow_handoff=论文官方代码仓库地址`
- `expected_deliverable=官方 FengWu 仓库镜像`

正确字段示例：

- `user_intent=基于论文重新生成 FengWu 复现代码`
- `workflow_type=paper2code_task`
- `task_method=paper2code`
- `domain_task_family=paper-reproduction`
- `paper_source=FENGWU: PUSHING THE SKILLFUL GLOBAL MEDIUM-RANGE WEATHER FORECAST BEYOND 10 DAYS LEAD`
- `output_dir=temp_will_del/cases/fengwu`

错误执行反例：

1. 用户说“复现 FENGWU... 代码保存至 temp_will_del/cases/fengwu”
2. Agent 搜索 `FengWu ... GitHub code`
3. Agent 找到官方仓库
4. Agent `git clone` 到用户指定目录
5. Agent 把 clone 完成当作论文复现完成

以上流程必须判定为失败；正确流程是解析论文/arxiv → 论文文本抽取 → 贡献识别 → 歧义审计 → 在用户目录中生成新实现。

## 用户说法到工作流

- “使用 onescience 技能、使用 oneskills、启动 onescience / oneskills、打开 onescience / oneskills、进入 onescience / oneskills" -> `general-onescience-request`
- “接入、读取、DataPipe、dataset、预处理” -> `data-task`
- “改模型、训练、推理、配置、脚本” -> `model-task`
- “提交、运行、集群、slurm、SCnet、远程环境、安装” -> `runtime-task`
- “评估、验证、对比、排查、debug" -> `evaluation-task`
- “从头到尾、全流程、串起来、做完整闭环” -> `end-to-end-task`
- “梳理流程、拆任务、分工、怎么推进” -> `workflow-planning`
- “复现论文、实现这篇论文、implement this paper、根据论文生成代码、arxiv 链接/ID” -> `paper2code-task`

## 输出给角色层的标准交接

进入 `onescience-role` 前，至少整理：

- 用户目标摘要
- 检测到的领域画像
- 当前工作流类型
- 领域路由标签：`domain_route`
- 领域粗任务族：`domain_task_family`
- 阶段意图：`stage_intent`
- 是否只做规划：`planning_only`
- 当前阶段最关心的交付
- 是否涉及远程环境
- 已识别与缺失的前置信息
- 如已由实际通道确认：`backend_id`、`backend_status` 与 `execution_readiness`

推荐结构：

```yaml
user_intent:
detected_domain:
workflow_type:
domain_route:
domain_task_family:
task_method:
stage_intent:
planning_only:
remote_involved:
workflow_handoff:
paper_source:
next_skill: onescience-role
future_execution_entry:
```

字段边界：

- `domain_route` 只表达进入哪个科学领域路线，例如 `earth`、`cfd`、`biology`、`materials`、`general-science`，不要用 `paper2code` 覆盖真实领域。
- `domain_task_family` 只表达粗粒度任务族，例如 `data-interface`、`model-development`、`paper-reproduction`、`inference`、`runtime`、`install`、`diagnose`、`end-to-end`。
- `task_method` 表示横向任务方法，例如 `paper2code`；它可以和任意真实 `domain_route` 组合。
- `stage_intent` 只表达当前用户授权到哪一阶段，例如 `planning`、`implementation`、`runtime`、`install`、`diagnose`、`evaluation`。
- `planning_only=true` 时，`next_skill` 仍可为 `onescience-role`，但不要把 `onescience-skill`、`onescience-coder`、`onescience-runtime` 或 `onescience-installer` 写成当前已调用链路。
- `workflow` 不输出角色链、不选择具体 coder 资产、不做模型兼容性表；这些由 `onescience-role` 基于 handoff 继续完成。

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
- 只有用户明确点名 `onescience-coder`、`onescience-runtime`、`onescience-installer` 等具体 skill 时，才直接进入对应 skill
