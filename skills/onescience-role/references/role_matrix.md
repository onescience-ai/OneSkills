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
- `domain_route`
- `domain_task_family`
- `stage_intent`
- `planning_only`

字段分工：

- `domain_route`、`domain_task_family`、`stage_intent` 由 `onescience-workflow` 负责粗判。
- `onescience-role` 只基于这些字段继续细化角色链、任务桶和交接物。
- 如果上游字段缺失，role 可以做最小补判，但不要重新输出一套完整 workflow 入口分析。

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
- 远程资源相关进入 `onescience-skill -> onescience-runtime` 或 `onescience-installer`

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
- backend 状态说明（stable / planned / unsupported）

推荐下钻：

- 感知环境：优先 `onescience-skill -> onescience-runtime` 的 discover/preflight；安装场景进入 `onescience-installer`
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

- 优先 `onescience-skill -> onescience-runtime`

### 7. `paper-reproducer`（论文复现交接角色）

职责：

- 将论文复现任务组织为可交给执行层的阶段化交接物
- 明确论文来源、复现模式、框架偏好、领域路线、实现范围和阶段门槛
- 确认进入代码生成前必须先完成或复用合格的 `reproduction_spec.md` 与 `coder_task_description.md`

关注点：

- 论文核心贡献和复现范围的精确识别
- 实现细节的歧义审计（防幻觉）
- 复现规格与 coder 任务描述的结构化组织
- 下游代码生成边界和 OneScience 复用提示
- 与真实科学领域路线（earth / biology / materials / cfd 等）的组合，不用 `paper2code` 覆盖领域

典型输入：

- `paper_source`：arxiv ID/URL、本地 PDF、粘贴文本或已知论文名
- 运行模式（minimal / full / educational）
- 框架偏好（pytorch / jax / numpy）
- 上游 workflow 传递的 `task_method=paper2code` 或 `domain_task_family=paper-reproduction`
- 上游 workflow 传递的真实 `domain_route`

典型输出：

- 角色链与阶段化交接物
- `paper_source`、mode、framework、真实 `domain_route`
- 已存在或待生成的论文解析材料、`reproduction_spec.md`、`coder_task_description.md` 引用
- `execution_entry=onescience-paper-repro`

推荐下钻：

- `onescience-skill -> onescience-paper-repro -> onescience-coder`

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

### 7. 论文复现链

`research-lead -> paper-reproducer`

若论文主题已经落入明确科学领域，优先组合领域角色：

`research-lead -> domain-scientist -> model-engineer -> paper-reproducer`

适用场景：

- 将论文来源转化为代码生成交接物
- 论文复现前处理流水线（获取解析 → 复现信息抽取 → 歧义审计 → coder 任务描述）

强制约束：

- `paper-reproducer` 是 paper2code 的主责角色；`domain-scientist` 和 `model-engineer` 只能作为领域/模型语义辅助角色，不能把主链退化为纯 `research-lead -> model-engineer`
- 不要把论文复现解释成“获取官方代码”“下载官方仓库”或“克隆论文代码到本地”
- 不要把 handoff artifact 写成“论文官方代码仓库地址”“官方仓库版本”“GitHub 搜索关键词”
- 用户指定的输出目录只传递为 `output_dir`，表示下游新生成代码落点

推荐交接物：

- `research-lead -> 任何角色`：任务目标摘要、交付边界、优先级
- `domain-scientist -> data-engineer`：数据口径、变量定义、筛选规则
- `data-engineer -> model-engineer`：数据读取方案、输入输出形状、路径约束
- `platform-engineer -> model-engineer`：代码生成交接摘要
- `platform-engineer -> runtime / installer`：完整环境画像与执行约束
- `model-engineer -> platform-engineer`：代码入口、脚本路径、配置说明
- `platform-engineer -> evaluation-engineer`：作业 ID、日志路径、运行信息
- `research-lead -> paper-reproducer`：`paper_source`、mode、framework、用户意图
- `paper-reproducer -> onescience-paper-repro`：`paper_source`、mode、framework、真实 `domain_route`、`output_dir`、`implementation_code_used=false`、stage 顺序约束
- `domain-scientist -> model-engineer`：论文所属领域约束、模型/数据/评估语义、可复用 OneScience 卡片
- `paper-reproducer -> onescience-skill -> onescience-paper-repro -> onescience-coder`：论文来源、真实 `domain_route`、论文解析 artifact、复现规格、完整任务描述、模式标志

## 角色到执行层入口映射

- 仅做角色分析：停留在 `onescience-role`
- 需要进入技能路由：进入 `onescience-skill`
- 远程环境事实不清：优先让执行层先走 `onescience-runtime` 或 `onescience-installer`
- 已明确需要安装：执行层进入 `onescience-installer`
- 已明确需要提交运行：执行层进入 `onescience-runtime`
- 已明确需要测试排查：执行层优先进入 `onescience-runtime` 的 diagnose 路径

## 生物信息领域补充

当 `detected_domain` / `domain` 是 `biology`、`bioinformatics`、`biosciences`，或用户请求明显涉及生信任务时，先读取 `../bio_domain/SKILL.md` 再给出最终角色链。该子路由用于区分：

- OneScience 已有生信模型相关任务：模型推理、模型开发、模块替换、训练、微调、batch 协议、datapipe adapter
- 通用生信 workflow：RNA-seq、single-cell、variant calling、ATAC/ChIP/Hi-C、microbiome、proteomics、metabolomics 等
- 生信 tool/database：Biopython、Scanpy、RDKit、NCBI、PDB、ChEMBL、KEGG 等
- 生命科学邻域任务：clinical protocol、LIMS、Allotrope、实验仪器数据标准化、临床变异和生物标志物

模型相关任务的角色链通常应包含 `model-engineer`，并把源码依据限定在 OneScience 仓库和 `onescience-coder` 模型卡；通用 workflow/tool/database 任务不要误路由成 OneScience 模型改造。

若生信任务需要远程 GPU/DCU、SLURM 或 SCnet 运行，仍由执行层进入 `onescience-runtime` 的 `discover/preflight/execute/diagnose` 闭环；若 preflight 发现环境未 ready，再回退 `onescience-installer`。不要在 role 层承诺硬件可用或展开完整执行链。

## 与 workflow 的边界

`onescience-workflow` 回答：

- 用户目标是什么
- 属于哪个领域路线
- 当前是数据、模型、运行、安装、诊断还是全流程阶段
- 当前是否只做规划

`onescience-role` 回答：

- 当前由哪个科研角色主导
- 最小角色链是什么
- 领域任务桶或模型路线是什么
- 交给下游的 `handoff_artifacts` 是什么
- 未来执行入口是什么

不要让 role 反向覆盖 workflow 的 `workflow_type` 或 `domain_route`。如果 role 发现上游路由明显不足，只在输出中标记 `route_correction_hint` 或 `missing_upstream_context`，再给出最小可继续的角色层判断。
