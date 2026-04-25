# Workflow Matrix

本文件用于给 `onescience-workflow` 提供更稳定的用户任务入口决策表。

## 顶层判断问题

先问自己：

1. 用户真正想完成什么科研工作？
2. 当前处在数据、模型、运行、评估还是全流程阶段？
3. 这是不是一个只需规划、不需执行的请求？

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
- “安装远程环境或准备提交脚本”

默认链路：

- 安装：`onescience-workflow -> onescience-role -> onescience-skill -> onescience-hardware -> onescience-installer`
- 运行：`onescience-workflow -> onescience-role -> onescience-skill -> onescience-hardware -> onescience-runtime`

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

- “接入、读取、DataPipe、dataset、预处理” -> `data-task`
- “改模型、训练、推理、配置、脚本” -> `model-task`
- “提交、运行、集群、slurm、远程环境、安装” -> `runtime-task`
- “评估、验证、对比、排查、debug” -> `evaluation-task`
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
