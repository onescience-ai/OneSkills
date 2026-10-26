# 自主执行模式细则（从 SKILL.md 剥离）

> 本文为 `onescience-orchestrator` 的 SKILL.md「自主执行模式」一节的完整细则。
> 触发词与默认激活规则见 SKILL.md 正文；**设置 `autonomous_mode: true` 后、进入阶段三执行前必须先读取本文**。

## autonomous_mode 下的行为变化

1. **Global Plan 输出简化**：仍输出 Global Plan 给用户看，但末尾追加提示：
   ```
   > [自主执行模式已激活，将按计划自动执行全部步骤，中途不暂停确认。步骤超时预算已启用]
   ```
   然后立即在同一轮内继续执行第一步，不等待用户回复。

2. **handoff 注入标记**：在发给所有 executor 的 `step_handoff` 中追加以下字段：
   ```yaml
   step_handoff:
     # ... 原有字段 ...
     attempt: 1
     execution_flags:
       autonomous_mode: true
     step_wallclock_budget_seconds: 3600
   ```
   其中 `step_wallclock_budget_seconds` 根据该步骤的预估耗时设置（取预估时间的 3 倍，最小 600 秒，最大 7200 秒）。

3. **observation 处理加速**：若 executor 返回 `success` 且尚未完成全部步骤，直接选择下一个 `Next Step Spec` 并调用下一个 executor，不等待、不确认。

4. **自动执行停止条件**：只有遇到以下情况才停止：
   - 全部 `completion_criteria` 满足 → 输出最终结果并结束
   - executor 返回 `blocked` → 输出阻断原因，停止等待用户处理
   - executor 返回 `failed` 且根据 failure_category 策略处理失败（见下方"失败分类策略"）
   - 步骤墙钟超时（`step_timeout`）→ 记录 event，进入 blocked

5. **不可自动决策时的处理**：若 orchestrator 自身在 planning / selection 阶段遇到歧义（如多个 executor 都可执行但无法自动判定最优选择），优先选择匹配度最高的 executor 并记录低置信度标记；不得在 autonomous_mode 下向用户提问。

6. **决策分级策略**：autonomous_mode=true 时，遇到分叉决策按以下三级处理：

| 级别 | 判定条件 | 策略 | 示例 |
|---|---|---|---|
| level_1_reversible | 决策可回退、不影响最终目标 | `auto_choose_first`：直接选优先级最高的选项 | 先训练哪个模型、先读哪个文件 |
| level_2_scope_affecting | 影响范围但不改变核心目标 | `auto_with_log`：自动选择并记录决策日志到 `decision_policy.active_decisions` | 数据子集大小、epoch 数调整 |
| level_3_goal_altering | 涉及核心目标变化或外部资源硬阻塞 | `block_and_escalate`：暂停执行，写入 `.onescience/task_state.json` 的 blocked 状态，附带决策选项和 fallback；若 wallclock 超过 `decision_policy.level_3_fallback_timeout_seconds` 无人响应，自动使用 fallback 选项 | 数据替代方案选择、不可达外部资源 |

Block 时的写入格式：
```json
{
  "blocked_reason": "decision_required",
  "decision_level": "level_3_goal_altering",
  "decision_prompt": "<描述当前阻塞的决策点>",
  "options": [
    {"label": "...", "description": "...", "is_fallback": false},
    {"label": "...", "description": "...", "is_fallback": true}
  ],
  "fallback_timeout_seconds": 300,
  "fallback_option_index": 1
}
```

7. **OpenCode Todo 同步**：autonomous_mode=true 时，orchestrator 必须在以下关键节点调用 `todowrite` 将任务执行进度同步到 OpenCode 界面，确保用户可实时感知当前执行状态：

   | 时机 | todowrite 操作 |
   |---|---|
   | Global Plan 输出后 | 将所有计划步骤写入 todo 列表（status: pending） |
   | 每个 executor 调用前 | 将当前步骤标记为 in_progress，同步 active_step 信息 |
   | 每个 executor 成功返回后 | 将完成步骤标记为 completed |
   | 步骤失败进入 blocked | 标记当前步骤为 pending，在 content 中追加 blocked 原因 |
   | 任务全部完成 | 标记所有步骤为 completed |

   todowrite content 示例：
   ```json
   {
     "content": "步骤1：论文解析 → paper-repro",
     "status": "completed",
     "priority": "high"
   }
   ```

   **注意**：todowrite 仅用于界面进度展示，Task State 仍是 orchestrator 内部唯一事实源，不要用 todowrite 替代 task_state.json 的读写。

   **容错规则**：todowrite 调用失败（工具不可用、超时、参数错误等）**不得阻断自动化执行**。失败时仅记录一条 `event_type=warning` 到 `Task State.events`（如 `todowrite_sync_failed`），然后继续后续步骤。界面 todo 列表缺失不影响任务实质性推进。

7a. **失败分类策略**：autonomous_mode=true 时，收到 executor 返回 `failed` 后根据 `execution_result.failure_category` 执行差异化策略：

| failure_category | 策略 | 重试上限 | 示例 |
|---|---|---|---|
| `transient` | `retry_with_backoff`：记录 event `repair_attempted`，递增 `attempt`，指数退避后重试 | 2 次 | 网络波动 |
| `code` | `delegate_to_coder`：委托 onescience-coder 修复代码后重试 | 2 次 | 冒烟测试失败 |
| `environment` | `delegate_to_installer`：委托 onescience-installer 修复环境后重试 | 2 次 | conda 依赖缺失 |
| `data` | `retry_re_fetch`：重新获取数据后重试 | 1 次 | 数据校验失败 |
| `scientific` | `block_and_escalate`：立即暂停，标记为需要人工研判 | — | 论文方法不可复现 |
| `dependency` | `block_and_escalate`：立即暂停 | — | 外部 API 不可达 |
| `platform` | `block_and_retry_once`：记录 event 后阻塞，重试 1 次 | 1 次 | executor 无响应 |
| `unknown` | `block_with_diagnosis`：进入诊断，根据诊断结果再判定 | — | 无法自动分类 |

- 每次执行失败/修复/重试均写入 `events` 和 `observations`。
- 超过重试上限 → 进入 `blocked` 状态。
- `scientific` 和 `dependency` 类别不自动重试，直接 blocked。

7b. **步骤超时保护**：autonomous_mode=true 时，每次调用 executor 前设置步骤墙钟预算：

- 从 `active_step.step_wallclock_budget_seconds` 获取预算，并记录 `step_started_at`。
- executor 返回时检查 wallclock 是否超过 `step_wallclock_budget_seconds`：
  - 未超过 → 正常流程。
  - 超过 → 标记 `status: step_timeout`，写入 event（`event_type=step_timed_out`），进入 blocked。
- blocked 恢复后重新执行时，attempt 递增，预算 = `original_budget * budget_multiplier_on_retry`。

7c. **Event 记录**：autonomous_mode=true 时，orchestrator 必须在以下时机写入 event 到 `Task State.events`：
  - 调用 executor 前 → `step_started`
  - 收到结果后 → `step_completed` / `step_failed` / `blocked` / `step_timed_out`
  - 进入修复 → `repair_attempted`
  - 开始重试 → `retry_started`
  - 诊断完成 → `diagnosis_completed`
  - tier 升级/回退 → `tier_escalated` / `tier_fallback`
  - 计划修改 → `plan_revised`
  - 每次 observation 写入后 → `observation_recorded`

7d. **Plan Version 递增**：每次对 `global_plan` 做结构性修改时（非简单状态更新），递增 `global_plan_version`，并追加一条 `global_plan_revision_history`。

8. **探索预算**：autonomous_mode 下的数据探索类步骤受硬性预算约束。orchestrator 在初始化时写入 `Task State.exploration_budget`，并在每次探索动作执行前后更新 `used` 和 `wallclock_seconds_used`。

预算定义（与 `references/task_state_contract.md` 中的 schema 一致）：

| 预算类别 | 最大尝试 | 最大耗时 | 耗尽后策略 |
|---|---|---|---|
| data_acquisition | 3 次 | 600s（10 分钟） | report_blocker_and_proceed_with_fallback |
| speed_measurement | 2 次 | 无单独限制 | use_last_measured_value |
| structure_probing | 2 次 | 120s（2 分钟） | skip_and_mark_unavailable |

预算检查规则：
- 每次执行探索动作前检查：对应类别的 `used < max_attempts` 且 `wallclock_seconds_used < max_wallclock_seconds`
- 若任一条件不满足 → 跳过探索，直接按 `on_exhausted` 策略处理
- 测速类操作（`curl -r ... -o /dev/null`、`timeout ... curl` 等）只允许执行 `speed_measurement.max_attempts` 次不同测速策略的测试；同一策略的重复执行视为同一次尝试
