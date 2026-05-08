# Codex CLI Integration Notes

本文件提供 `OneSkills` 在 `Codex CLI` 中的专属使用建议。

它不是新的核心 skill，也不替代 `integrations/generic-agent.md`；它只补充 `Codex CLI` 这类代码代理环境下更常见的行为约束。

## 推荐加载方式

当前推荐由安装器一次性完成两层：

- 项目内 `./.codex/oneskills/skills/`、`./.codex/oneskills/references/`、`./.codex/oneskills/integrations/`
- 用户级 `~/.codex/skills/onescience-*` bridge skills

其中：

- 项目内安装负责真实 skill 内容与共享 references
- 用户级 bridge 负责让当前 Codex 能发现这些 skills
- `integrations/generic-agent.md` 与本文件负责补充通用约束和 Codex 专属行为约束

## Codex CLI 下的推荐行为

### 0. 统一入口词先进入 workflow

如果用户只是说“使用/启动/打开/进入 onescience”或“使用/启动/打开/进入 oneskills”，以及“onescience 模式”“oneskills 模式”，默认进入 `onescience-workflow`，识别为 `general-onescience-request`，先询问具体科研目标，不要直接进入执行层。

如果用户明确点名具体 skill，例如 `onescience-coder`、`onescience-runtime`、`onescience-debug`，则直接使用对应 skill；该 skill 再按自身规则判断是否需要回到 `onescience-workflow`。

### 1. 先走主链，不要跳层

对科研任务，默认优先走：

`onescience-workflow -> onescience-role -> onescience-skill`

不要因为 `Codex CLI` 擅长直接改文件，就跳过任务理解层和角色层。

### 2. 编码前先判断是否需要硬件感知

如果任务涉及以下内容，先进入 `onescience-hardware`：

- 远程 Host
- GPU / DCU
- 队列 / 分区
- module / conda
- slurm 运行约束

如果只是纯本地代码生成或代码改造，则不要强行进入硬件链路。

### 3. 远程缺失时不要过早中断

在 `Codex CLI` 中，用户常常希望先完成本地代码准备，再补远程信息。

因此当远程环境：

- 未配置
- 描述模糊
- 尚未确认

推荐优先：

- 输出统一远程状态
- 明确缺什么
- 继续本地代码链

只有当用户明确要提交运行、安装环境或远程排查时，才把远程信息当成阻塞项。

### 4. 不要把运行动作当前置默认行为

`Codex CLI` 很容易直接进入“改完就跑”的模式，但在 `OneSkills` 中应保持：

- 代码生成 ≠ 自动运行
- 远程安装 ≠ 自动提交
- 调试排查 ≠ 所有任务默认步骤

只有在用户明确要求：

- 运行
- 安装
- 测试
- 排查

时，再进入下游执行链。

### 5. 保持路径与上下文通用

不要在输出中硬编码：

- `.trae/...`
- 某个特定 IDE 目录
- 某个特定 agent 的专属路径

应优先使用：

- 仓库相对路径
- 通用 `skills/` 路径
- `onescience.json` / `tpl.slurm` 这类运行约定

## 推荐提示方式

适合在 `Codex CLI` 中使用的入口提示例如：

```text
使用 oneskills
```

```text
使用 onescience-workflow，先判断这个科研任务属于哪条工作流，再进入最小技能链
```

```text
使用 onescience-skill，基于当前工作流和角色结论，选择最小执行链，不要直接进入 runtime
```

```text
使用 onescience-hardware，先判断远程环境是否足够明确；如果不明确，给出缺失项并允许继续本地代码阶段
```

## 一句话原则

在 `Codex CLI` 中，`OneSkills` 的核心目标不是“更快执行”，而是“按正确分层更稳定执行”。
