# Agent Pipeline

本文件给通用智能体入口提供更稳定的执行编排说明。

## 顶层分层

当前建议保持三层：

1. 用户任务层：`onescience-workflow`
2. 角色决策层：`onescience-role`
3. 执行层：`onescience-skill` + 下游执行技能

## 执行层

执行层公开技能为：

- `onescience-runtime`
- `onescience-installer`

其中：

- 环境识别能力由 `runtime/installer` 内部 `discover` 阶段承担
- 运行后基础诊断能力由 `runtime` 内部 `diagnose` 阶段承担

## 默认链路

远程工程类请求，推荐默认按下面顺序推进：

`onescience-workflow -> onescience-role -> onescience-skill -> onescience-coder -> onescience-runtime`

当 runtime preflight 发现环境未 ready 时，再进入：

`onescience-installer -> onescience-runtime`

如果用户没有要求完整闭环，不要默认拉起全部阶段。

## 执行技能职责

### `onescience-runtime`

负责统一运行闭环：

- `discover`
- `preflight`
- `execute`
- `diagnose`

它回答：

- 这是什么环境
- 能不能直接跑
- 该怎么跑
- 跑到什么状态
- 基础失败原因是什么

### `onescience-installer`

负责环境安装与修复：

- 识别环境缺口
- 组织安装命令
- 验证环境是否 ready

它回答：

- 该装什么
- 能不能装
- 装完是否可运行

## 简化链路

- 用户只想梳理科研任务：`onescience-workflow`
- 纯角色分析或职责划分：`onescience-role`
- 角色层已明确，只需执行路由：`onescience-skill`
- 纯分析或纯编码：`onescience-coder`
- 已有代码，只想运行：`onescience-runtime`
- 环境未就绪，需要补装：`onescience-installer`
- 已有脚本，只想通过 SCnet 平台运行：`onescience-runtime`

## 编排原则

1. 先看用户最终交付目标，再选最小链路。
2. 远程执行优先进入 `onescience-runtime`，由其做环境发现与运行前预检。
3. 只有当 runtime 明确判定“环境未 ready”时，才回退到 `onescience-installer`。
4. 不要把安装与运行提交混成一个 skill。
5. 不要在没有执行证据时声称“已运行成功”。

## 禁止事项

- 不要让 `onescience-installer` 接管作业提交
- 不要让 `onescience-runtime` 在缺失环境依赖时偷偷补装
- 不要把显式远程运行请求强行拆成多个公开技能再让用户理解内部阶段
- 不要让 `onescience-runtime` 在没有代码时提交空任务
