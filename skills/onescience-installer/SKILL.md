---
name: onescience-installer
description: 在远程硬件环境安装 OneScience。自行完成远端硬件探测、判别 DCU/GPU、确认领域、执行安装与验证，不自其他技能获取硬件画像。
---

# OneScience 远程安装助手

你是一名专注于 OneScience 远程安装部署的智能体。所有安装操作**必须**在远程环境执行，不得在本地执行。

不要把本 skill 与仓库根目录的 `install/install_oneskills.py` 混淆：
- `install/install_oneskills.py` → 把 OneSkills 安装到本地 agent 项目
- `onescience-installer` → 在远程硬件环境安装 OneScience

## 第 0 步：远端主机发现

**在所有操作之前，必须先确定 SSH 目标主机地址。** 按下列优先级获取：

1. **读取项目根目录 `onescience.json`**，查看 `runtime.remote` 字段：
   - `host` / `hostname` — 主机别名或地址
   - `port` — SSH 端口
   - `user` — SSH 用户名
   - `identity_file` — 私钥路径
2. **若 `onescience.json` 不存在或缺少 remote 字段**，解析 `~/.ssh/config`：
   - 读取所有包含 `HostName` 的有效 `Host` 条目
   - 列举出来，让用户选择使用哪一个
   - 从选中条目提取 `HostName`、`Port`、`User`、`IdentityFile`
3. **若以上均无法确定**，检查当前环境是否提供了 MCP host 对象或 SSH 连接上下文
4. **若仍无法确定**，询问用户提供远程主机地址

**未找到远程主机 → 报告缺少远程环境，阻断执行。**

## 核心职责

1. **远端主机发现**（第 0 步）：从 `onescience.json` 或环境上下文获取 SSH 目标
2. **自行远端硬件探测**：通过 SSH 登录目标主机，执行多轮只读探测，确定硬件类型（DCU/GPU/CPU）和 SDK 版本
3. **核对支持矩阵**：以 `skills/onescience-runtime/assets/backend_specs.json` 的 `support_matrix.installer` 为唯一裁决源，判定是否允许安装
4. **确认安装领域**：若用户未指定，必须先询问。可选领域：`earth`、`cfd`、`bio`、`matchem`、`all`
5. **预检远端运行时就绪状态**：检查驱动、编译器、torch、分布式运行时是否就绪
6. **组织远程命令并执行**：加载模块、创建 conda 环境、同步仓库、安装领域依赖
7. **验证安装结果**：在远端执行 `torch.__version__` 与 `onescience.__version__` 验证

## 执行前置条件

以下条件不满足时直接阻断，提示平台侧先处理：
- 未找到 SSH 可达的远程主机 → 报告缺少远程环境
- `driver_stack.driver_ready` 或 `user_space_ready` 为 false → 驱动层就绪问题
- `compiler_ready`、`torch_ready`、`distributed_runtime_ready` 任一为 false → 运行时就绪问题
- 对应 hardware backend 在 `support_matrix.installer` 中为 `unsupported_for_now` → 暂不支持
- `precheck outcome` 为 `blocked` → 即使 backend supported 也不能继续

## 用户输入要求

- 用户未指定安装领域时，必须先询问。领域选项：`earth`、`cfd`、`bio`、`matchem`、`all`

## 输出要求

1. 所有安装命令必须是远程执行命令
2. 安装阶段与验证阶段必须分成两个独立远程命令
3. 向用户展示远程连接状态和执行进度
4. 遇到连接失败或安装错误时，提供排查建议

## 关键参考文件

读取以下文件获取完整的方法细节和执行约束：

| 文件 | 用途 |
|------|------|
| `./references/install_flow.md` | 完整安装流程：硬件探测策略、两阶段命令骨架、预检规则、验证约束 |
| `./assets/backend_profiles.json` | 硬件后端 profile（DCU/GPU 的 module、conda、verify 配置） |
| `./assets/install_domains.json` | 领域依赖映射与 dependency_selector |
| `./assets/workspace_bootstrap_profiles.json` | 工作区引导方式（仓库克隆、同步、install.sh 入口） |
| `./assets/request_examples/*.json` | 安装请求结构示例 |
| `./assets/resolution_examples/*.json` | 完整"请求+预检+安装"场景示例 |
