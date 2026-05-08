# OneScience 通用智能体入口

## 目标

把用户需求转成稳定的工程链路，并按正确分层执行：

```text
工作流理解 -> 角色编排 -> 执行路由 -> 硬件感知 -> 代码生成 -> 远程运行 -> 结果排查
```

当你需要判断默认链路、分层职责、简化链路或禁止事项时，读取 `references/agent_pipeline.md`。
当你需要处理“未配置远程环境”或“远程描述模糊”的异常场景时，读取 `references/remote_fallback.md`。
当你需要按统一格式输出远程异常状态时，读取 `references/remote_status_template.md`。
当你需要参考最终异常回复示例时，读取 `references/remote_status_examples.md`。

## 核心要求

1. 先识别用户最终要交付什么，再选择最小可用链路。
2. 涉及科研任务理解、领域归类、阶段判断时，先进入 `onescience-workflow`。
3. 涉及科研职责、角色接力、流程分工时，再进入 `onescience-role`。
4. 远程环境事实不明确时，先进入 `onescience-hardware`。
5. `onescience-coder` 只消费代码生成交接摘要，不直接处理完整硬件画像。
6. `onescience-runtime` 与 `onescience-installer` 只消费完整硬件画像，不接管代码生成。
7. 只有用户明确要求运行、安装、验证或排查时，才进入对应阶段。
8. 当远程环境缺失或描述模糊时，优先用 `status` / `recognized` / `missing` / `can_continue_locally` / `next_action` 输出当前可执行性。

## 默认远程工程链路

```yaml
pipeline:
  - skill: onescience-workflow
    reason: 先理解用户真实科研任务、领域和当前工作流阶段

  - skill: onescience-role
    reason: 再判断当前科研流程中由哪个角色推进，并定义交接物

  - skill: onescience-skill
    reason: 把工作流层与角色层结论转成最小执行技能链

  - skill: onescience-hardware
    reason: 先感知 Host、设备类型、队列和环境约束

  - skill: onescience-coder
    reason: 基于代码生成交接摘要生成适配代码

  - skill: onescience-runtime
    reason: 连接远程环境、生成脚本并提交运行

  - skill: onescience-debug
    reason: 对日志、指标和结果进行排查
```
