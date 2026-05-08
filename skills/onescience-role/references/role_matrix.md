# Role Matrix

本文件用于给 `onescience-role` 提供更稳定的角色层决策依据。

## 抽象原则

1. `role` 负责职责与决策
2. `skill` 负责执行与实现
3. `artifact` 负责交接与下钻
4. 角色层只选择最小角色链，不直接替代执行层

## 上游约定

角色层的理想上游是 `onescience-workflow`。

如果上游已经给出工作流摘要，优先消费这些字段：

- `user_intent`
- `detected_domain`
- `workflow_type`
- `workflow_handoff`

## 六类核心角色

### 1. `research-lead`

职责：

- 定义研究目标与最终交付
- 决定当前阶段由谁主导
- 控制是否进入执行层

关注点：

- 问题边界
- 交付优先级
- 最小可行链路

典型输入：

- 用户目标
- 项目背景
- 结果预期

典型输出：

- 当前主导角色
- 最小角色链
- 阶段性交接要求

推荐下钻：

- 默认先进入 `onescience-skill`

### 2. `domain-scientist`

职责：

- 明确科学问题、数据语义与物理约束
- 判断变量、时空尺度、任务口径是否正确

关注点：

- 数据含义
- 指标定义
- 科学假设

典型输入：

- 研究目标
- 数据集描述
- 领域先验

典型输出：

- 任务口径说明
- 变量/标签定义
- 数据筛选约束

推荐下钻：

- 数据准备进入 `onescience-skill -> onescience-coder`
- 远程资源相关进入 `onescience-skill -> onescience-hardware`

### 3. `data-engineer`

职责：

- 组织数据接入、清洗、采样与 DataPipe 结构
- 明确数据路径、格式与读取入口

关注点：

- 数据入口
- 路径约束
- 批处理与吞吐

典型输入：

- 数据任务口径
- 数据源位置
- 存储与格式约束

典型输出：

- 数据读取方案
- DataPipe / dataset 入口
- 数据侧交接摘要

推荐下钻：

- `onescience-skill -> onescience-coder`

### 4. `model-engineer`

职责：

- 负责模型、训练脚本、配置与推理入口实现
- 把数据侧要求落到可运行代码

关注点：

- 模型结构
- 训练/推理入口
- 配置与设备适配

典型输入：

- 数据侧交接摘要
- 完整硬件画像中的代码相关约束
- 用户实现目标

典型输出：

- 代码改动点
- 配置入口
- 运行入口说明

推荐下钻：

- `onescience-skill -> onescience-coder`

### 5. `platform-engineer`

职责：

- 处理远程环境、连接、安装、脚本生成与作业提交
- 把本地代码交付到远程运行环境

关注点：

- Host / 队列 / 模块环境
- 远程路径
- 作业脚本与提交状态

典型输入：

- 完整硬件画像
- 代码入口
- `onescience.json`
- `tpl.slurm`

典型输出：

- 运行前置检查结果
- 安装结果或提交结果
- 作业 ID / 日志入口

推荐下钻：

- 感知环境：`onescience-skill -> onescience-hardware`
- 安装环境：`onescience-skill -> onescience-installer`
- 提交运行：`onescience-skill -> onescience-runtime`

### 6. `evaluation-engineer`

职责：

- 设计验证路径并读取日志、指标、产物做排查
- 判断问题在数据、模型还是运行阶段

关注点：

- 测试路径
- 指标稳定性
- 日志与异常定位

典型输入：

- 运行产物
- 日志
- 指标结果

典型输出：

- 测试/验证链路
- 问题定位
- 下一步修复建议

推荐下钻：

- `onescience-skill -> onescience-debug`

## 常见角色链

### 1. 纯角色规划

`research-lead`

适用场景：

- 只是梳理流程
- 只是分配职责
- 只是判断谁该继续推进

### 2. 数据接入链

`research-lead -> domain-scientist -> data-engineer`

适用场景：

- 新数据集接入
- 明确变量与读取方案

### 3. 代码实现链

`research-lead -> domain-scientist -> data-engineer -> model-engineer`

适用场景：

- 从数据语义到代码实现的完整编码任务

### 4. 远程运行链

`research-lead -> model-engineer -> platform-engineer`

适用场景：

- 代码已明确，下一步是连接远程环境并提交

### 5. 结果排查链

`research-lead -> platform-engineer -> evaluation-engineer`

适用场景：

- 已有日志、作业或结果，需要定位问题

### 6. 全流程链

`research-lead -> domain-scientist -> data-engineer -> model-engineer -> platform-engineer -> evaluation-engineer`

适用场景：

- 从问题定义到最终验证的完整科研工程闭环

## 推荐交接物

- `research-lead -> 任何角色`：任务目标摘要、交付边界、优先级
- `domain-scientist -> data-engineer`：数据口径、变量定义、筛选规则
- `data-engineer -> model-engineer`：数据读取方案、输入输出形状、路径约束
- `platform-engineer -> model-engineer`：代码生成交接摘要
- `platform-engineer -> runtime / installer / debug`：完整硬件画像
- `model-engineer -> platform-engineer`：代码入口、脚本路径、配置说明
- `platform-engineer -> evaluation-engineer`：作业 ID、日志路径、运行信息

## 角色到执行层入口映射

- 仅做角色分析：停留在 `onescience-role`
- 需要进入技能路由：进入 `onescience-skill`
- 远程环境事实不清：优先让执行层先走 `onescience-hardware`
- 已明确需要安装：执行层进入 `onescience-installer`
- 已明确需要提交运行：执行层进入 `onescience-runtime`
- 已明确需要测试排查：执行层进入 `onescience-debug`
