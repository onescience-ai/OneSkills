# OpenCode Integration Notes

本文件提供 `OneSkills` 在 `OpenCode` 类技能代理环境中的最小接入说明。

它不替代 `integrations/generic-agent.md`，而是补充 `OpenCode` 场景下的推荐加载方式。

## 推荐加载方式

建议同时提供：

- `skills/`
- `integrations/generic-agent.md`
- `integrations/opencode/README.md`

其中：

- `skills/` 负责核心能力
- `integrations/generic-agent.md` 负责通用分层约束
- 本文件负责 `OpenCode` 场景下的补充说明

## 推荐行为

1. 如果用户只是说“使用/启动/打开/进入 onescience”或“使用/启动/打开/进入 oneskills”，以及“onescience 模式”“oneskills 模式”，默认进入 `onescience-workflow`，识别为 `general-onescience-request`，先询问具体科研目标，不要直接进入执行层。

2. 如果用户明确点名具体 skill，例如 `onescience-coder`、`onescience-runtime`、`onescience-debug`，则直接使用对应 skill；该 skill 再按自身规则判断是否需要回到 `onescience-workflow`。

3. 默认先走：

```text
onescience-workflow -> onescience-role -> onescience-skill
```

4. 只有任务明确涉及远程 host、GPU/DCU、队列、module、conda 或 slurm 约束时，才进入 `onescience-hardware`。

5. 用户未明确要求运行、安装或调试时，不要自动进入：

- `onescience-runtime`
- `onescience-installer`
- `onescience-debug`

6. 远程环境缺失时，优先给出缺失项并继续本地代码链，不要直接判定整条任务 blocked。

7. 输出中优先使用仓库相对路径，不要硬编码特定 IDE 或 agent 私有目录。
