# OneScience 通用智能体入口

## 目标

把用户需求转成稳定的工程链路，并按正确分层执行：

```text
工作流理解 -> 角色编排 -> 执行路由 -> 代码生成 -> 远程安装/运行 -> 结果诊断
```

当你需要判断默认链路、分层职责、简化链路或禁止事项时，读取 `../references/agent_pipeline.md`。
当你需要处理“未配置远程环境”或“远程描述模糊”的异常场景时，读取 `../references/remote_fallback.md`。
当你需要按统一格式输出远程异常状态时，读取 `../references/remote_status_template.md`。
当你需要参考最终异常回复示例时，读取 `../references/remote_status_examples.md`。

## 核心要求

1. 先识别用户最终要交付什么，再选择最小可用链路。
2. 涉及科研任务理解、领域归类、阶段判断时，先进入 `onescience-workflow`。
3. 涉及科研职责、角色接力、流程分工时，再进入 `onescience-role`。
4. 远程环境事实不明确时，优先进入 `onescience-runtime` 的 `discover/preflight`，或 `onescience-installer` 的 `discover/precheck`。
5. `onescience-coder` 只消费代码实现所需约束摘要，不直接负责远程环境探测。
6. `onescience-runtime` 与 `onescience-installer` 负责消费并补齐执行环境事实，不接管代码生成。
7. 只有用户明确要求运行、安装、验证或排查时，才进入对应阶段。
8. 当远程环境缺失或描述模糊时，优先用 `status` / `recognized` / `missing` / `can_continue_locally` / `next_action` 输出当前可执行性。

## 统一入口触发

当用户提示词只是在启用 OneScience / OneSkills 体系，例如：

- “使用 onescience”
- “启动 onescience”
- “打开 onescience”
- “进入 onescience”
- “onescience 模式”
- “使用 oneskills”
- “启动 oneskills”
- “打开 oneskills”
- “进入 oneskills”
- “oneskills 模式”

默认进入 `onescience-workflow`，识别为 `workflow_type=general-onescience-request`，询问用户具体科研目标，不要直接拉起完整执行链。

如果用户明确点名具体 skill，例如 `onescience-workflow`、`onescience-coder`、`onescience-runtime`、`onescience-installer` 等，则优先使用对应 skill 完成工作；该 skill 再根据自身规则决定是否需要转回上游入口。

## 默认远程工程链路

```yaml
pipeline:
  - skill: onescience-workflow
    reason: 先理解用户真实科研任务、领域和当前工作流阶段

  - skill: onescience-role
    reason: 再判断当前科研流程中由哪个角色推进，并定义交接物

  - skill: onescience-skill
    reason: 把工作流层与角色层结论转成最小执行技能链

  - skill: onescience-coder
    reason: 基于任务约束生成或改造适配代码

  - skill: onescience-runtime
    reason: 连接远程环境、完成 discover/preflight/execute/diagnose

  - skill: onescience-installer
    reason: 仅在 runtime preflight 明确环境未 ready，或用户明确要求安装修复时进入 discover/precheck/install/verify
```
