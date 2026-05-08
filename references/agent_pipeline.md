# Agent Pipeline

本文件用于给通用智能体入口文件提供更稳定的分层编排说明。

## 顶层分层

当前架构分为三层：

1. 用户任务层：`onescience-workflow`
2. 角色决策层：`onescience-role`
3. 执行层：`onescience-skill` + 下游执行技能

用户任务层负责回答“用户现在到底想做什么”；角色层负责回答“当前应该由谁推进”；执行层负责回答“接下来具体用哪个 skill 落地”。

## 默认链路

远程工程类请求，默认按下面顺序推进：

`onescience-workflow -> onescience-role -> onescience-skill -> onescience-hardware -> onescience-coder -> onescience-runtime -> onescience-debug`

如果用户没有要求完整闭环，不要默认拉起全部阶段。

## 分层职责

### `onescience-workflow`

负责用户任务层编排：

- 理解科研人员自然语言需求
- 识别领域画像
- 选择最小工作流
- 把结果交给内部角色层

不要要求用户先理解内部角色或执行技能。

### `onescience-role`

负责角色决策层编排：

- 识别当前主导角色
- 选择最小角色链
- 明确角色交接物
- 指定下一步执行入口

不要把它直接写成技能流水线执行器。

### `onescience-skill`

负责执行层编排：

- 把角色层结论转成最小技能链
- 决定是否进入 hardware / coder / runtime / installer / debug
- 输出执行层下一跳

不要替代角色层做完整科研职责抽象。

### `onescience-hardware`

负责感知环境事实：

- Host
- DCU / GPU / CPU 类型
- 队列、module、conda、路径约束
- 输出完整硬件画像
- 提炼代码生成交接摘要

### `onescience-coder`

负责实现代码：

- 数据接入
- 模型与组件改造
- 配置与入口补齐
- 基于代码生成交接摘要做设备与路径适配

不要让它直接承担 Host、队列、module 探测。

### `onescience-runtime`

负责运行提交：

- 作为统一运行入口选择执行通道
- 在 `ssh_slurm` 通道里读取 `onescience.json` / `tpl.slurm` 并提交
- 在 `scnet_mcp` 通道里通过本地 SCnet MCP 上传、提交、查状态与下载日志
- 向 `onescience-debug` 返回统一的本地日志产物

### `onescience-debug`

负责验证排查：

- 识别测试路径
- 读取日志与结果
- 输出问题定位与下一步建议

### `onescience-installer`

负责环境安装：

- 读取完整硬件画像
- 确认安装领域
- 连接远程环境完成安装与验证

## 简化链路

- 用户只想梳理科研任务：`onescience-workflow`
- 纯角色分析或职责划分：`onescience-role`
- 角色层已明确，只需执行路由：`onescience-skill`
- 纯分析或纯编码：`onescience-coder`
- 已有代码，只想运行：`onescience-hardware -> onescience-runtime`
- 已有脚本，只想通过 SCnet 运行：`onescience-runtime`
- 已有结果，只想排查：`onescience-debug`
- 环境安装：`onescience-hardware -> onescience-installer`
- 面向远程环境实现：`onescience-hardware -> onescience-coder`

## 编排原则

1. 先看用户最终交付目标，再选最小链路
2. 先判断是否需要用户任务层；如果用户只是描述真实科研任务，优先从 `onescience-workflow` 进入
3. 再判断是否需要角色层；如果只是职责/流程问题则停留在 `onescience-role`
4. 远程环境事实不明确时，先走 `onescience-hardware`
5. 只有代码已经存在且用户要求运行时，才进入 `onescience-runtime`
6. 只有需要验证、测试、排查时，才进入 `onescience-debug`
7. 安装与运行提交分层处理，不混用 `onescience-installer` 与 `onescience-runtime`

## 禁止事项

- 不要跳过用户任务层就要求用户改写成内部术语
- 不要跳过角色层就把科研职责直接硬编码成技能链
- 不要跳过硬件感知直接生成远程适配代码
- 不要让 `onescience-hardware` 直接承担运行提交主职责
- 不要让 `onescience-runtime` 在没有代码时提交空任务
- 不要把显式 SCnet 请求强行改造成 `ssh_slurm` 通道
- 不要在没有执行证据时声称“已运行成功”
