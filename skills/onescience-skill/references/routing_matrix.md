# Routing Matrix

本文件用于给 `onescience-skill` 提供更稳定的路由决策表。

## 先判断是否属于工作流层

如果用户主要在问下面这些问题，先转给 `onescience-workflow`：

- “我要完成一个科研任务，应该怎么推进”
- “这是数据问题、模型问题还是运行问题”
- “我这个需求属于哪个工作流”
- “不同领域人员会怎么描述这个任务”

这类问题先做用户工作流决策，再进入角色层或执行层。

## 先判断是否属于角色层

如果用户主要在问下面这些问题，先转给 `onescience-role`：

- “当前应该由哪个科研角色推进”
- “整个科学计算流程应该怎么按角色拆分”
- “角色之间应该如何交接”
- “应该先抽取哪些岗位/角色”

这类问题先做角色层决策，再进入执行层。

## 最小技能链优先级

先问自己：用户最终要交付什么？

1. 只是识别远程 Host、队列、模块、路径约束  
   -> `onescience-hardware`
2. 只是实现或修改代码  
   -> `onescience-coder`
3. 只是运行、提交、生成脚本  
   -> `onescience-runtime`
4. 只是安装远程环境  
   -> `onescience-installer`
5. 只是验证、测试、排查  
   -> `onescience-debug`

如果一个请求同时命中多个阶段，优先选择覆盖目标所需的最短链路，而不是默认拉起全流程。

## 组合链路

### 1. 面向远程环境实现

适用信号：

- “按某个 DCU / GPU / SLURM 环境适配代码”
- “先识别 Host / 队列，再生成训练或推理代码”

技能链：

`onescience-hardware -> onescience-coder`

传递规则：

- 给 `onescience-coder`：只传“代码生成交接摘要”
- 不把完整硬件画像直接塞给 `onescience-coder`

### 2. 实现并运行

适用信号：

- “写完代码后直接跑起来”
- “补齐训练入口并提交到 slurm”

技能链：

`onescience-hardware -> onescience-coder -> onescience-runtime`

传递规则：

- 给 `onescience-coder`：代码生成交接摘要
- 给 `onescience-runtime`：完整硬件画像 + `onescience.json` + `tpl.slurm`

### 3. 已有代码，只做运行

适用信号：

- “当前工程已有脚本，直接提交”
- “读取 onescience.json 并运行”

技能链：

`onescience-hardware -> onescience-runtime`

### 4. 安装远程环境

适用信号：

- “在 DCU 环境安装 OneScience”
- “初始化远程依赖”

技能链：

`onescience-hardware -> onescience-installer`

### 5. 运行后排查

适用信号：

- “作业报错，帮我看日志”
- “loss 异常，帮我排查”

默认技能链：

- 若已有运行产物：`onescience-debug`
- 若仍缺远程环境事实：`onescience-hardware -> onescience-debug`
- 若还没真正提交测试或运行：`onescience-hardware -> onescience-runtime -> onescience-debug`

## 关键词到技能

- “角色、岗位、职责、交接、谁来做、科研流程分工” -> `onescience-role`
- “科研任务、工作流、领域、阶段、我想做什么、怎么推进” -> `onescience-workflow`
- “实现、改造、接入、生成代码” -> `onescience-coder`
- “提交、运行、slurm、作业、集群” -> `onescience-runtime`
- “测试、验证、排查、debug、loss 异常” -> `onescience-debug`
- “ssh、Host、队列、DCU、GPU、module、conda、硬件约束” -> `onescience-hardware`
- “安装、环境、依赖、初始化” -> `onescience-installer`

关键词只作为线索，不要机械匹配；仍应以用户真正的交付目标为准。

## 缺失项处理

- 缺少远程环境事实：先走 `onescience-hardware`
- 缺少 `onescience.json` / `tpl.slurm`：仅阻塞运行链路，不阻塞纯代码链路
- 缺少源码上下文：先说明要读哪些目录或文件
- 只有代码生成需求：不要强行补 `runtime`

## 常见误路由

### 错误 1：纯代码任务也拉起运行链

后果：

- 无意义增加上下文
- 让 `coder` 和 `runtime` 职责混杂

### 错误 2：工作流理解问题直接硬路由到执行层

后果：

- 用户任务表达和内部执行结构混在一起
- 顶层入口不够自然

### 错误 3：角色规划问题直接硬路由到执行层

后果：

- 角色职责和执行职责混在一起
- 很容易把顶层科研流程直接写死成工具调用顺序

### 错误 4：跳过 hardware 直接写远程适配代码

后果：

- 环境约束来源不清
- 容易把 Host、队列、路径写死

### 错误 5：把 installer 当 runtime 用

后果：

- 安装与提交职责混淆
- 环境初始化和作业运行边界不清
