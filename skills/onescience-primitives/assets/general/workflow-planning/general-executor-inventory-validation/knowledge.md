# Executor Inventory 完整性校验

## 适用范围

**触发条件**：orchestrator 规划阶段，executor inventory 构建完成后的校验环节。

**适用场景**：
- 所有涉及多 executor 技能的任务
- orchestrator 需要评估所有可用 executor 能力时
- proposal 融合和 Global Plan 生成前

**不适用场景**：
- 单 executor 技能任务（无需集合校验）
- executor 技能清单已确定不变的场景

## 输入

- **all_executor_skills**：系统中所有可用的 executor 技能清单（从 skills 目录发现）
- **read_executor_skills**：已读取 SKILL.md 的 executor 技能清单
- **executor_inventory_complete**：当前标记的完整性状态

## 输出

- **校验结果**：通过/失败
- **缺失技能清单**：未读取的 executor 技能列表（校验失败时）
- **补读任务**：需要读取的 SKILL.md 列表

## 流程节点

```
发现所有 executor 技能（glob 搜索）
    ↓
遍历读取每个 executor 的 SKILL.md
    ↓
[集合校验] set(all_executor_skills) == set(read_executor_skills)
    ↓
  ┌─ 通过 → 继续 proposal 融合和 Global Plan 生成
  │
  └─ 失败 → 停止后续规划
             ↓
           列出缺失技能
             ↓
           补齐缺失技能的读取
             ↓
           重新执行集合校验
```

**每步操作**：
1. 使用 glob 搜索所有 executor 技能的 SKILL.md 路径
2. 遍历读取每个 SKILL.md 内容
3. 执行集合校验：`set(all_executor_skills) == set(read_executor_skills)`
4. 校验通过：标记 `executor_inventory_complete=true` 并继续
5. 校验失败：列出缺失技能，补读后重新校验

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 校验公式 | `set(all) == set(read)` | orchestrator 规范 | 集合精确匹配 |
| 校验时机 | proposal 融合前 | orchestrator 规划阶段 | 不可跳过 |
| 失败行为 | 停止后续规划 | orchestrator 规范 | 必须补齐 |
| 标记字段 | `executor_inventory_complete` | global_plan.json | 校验通过才可设 true |

## 边界与分流

**校验通过**：继续 proposal 融合和 Global Plan 生成。

**校验失败**：停止后续规划，列出缺失技能并补读。

**部分读取**：不允许标记 `executor_inventory_complete=true`，必须全部读取。

**读取失败**：记录失败原因，继续尝试其他技能读取。

## 质量检查

| 检查点 | 验证方式 | 失败处理 |
|--------|----------|----------|
| 集合相等性 | `set(all) == set(read)` | 补齐缺失 |
| 标记一致性 | 检查 `executor_inventory_complete` 标记 | 修正标记 |
| 读取完整性 | 检查 read_executor_skills 数量 | 补读缺失 |

## 回退策略

- 校验失败：列出缺失技能，逐个补读
- 读取失败：记录失败原因，跳过该技能并继续
- 补读后仍失败：重复校验循环直到通过

## 资源召回建议

**何时召回本卡片**：
- orchestrator 规划阶段构建 executor inventory 时
- 需要校验 executor 技能覆盖完整性时
- 发现 `executor_inventory_complete` 标记与实际不一致时

**配套资源**：
- `general-pre-execution-confirmation-workflow`：预确认流程
- `general-executor-skill-invocation-contract`：executor 技能调用契约

## 证据来源

[1] OneScience Orchestrator SKILL.md 规范 - 集合校验要求
[2] 归因报告 Task 260 Issue 2 优化计划 - executor inventory 完整性校验知识描述

## 知识边界

- 本卡片定义集合校验的规范流程
- 校验范围限于 executor 技能（type=executor）
- 校验失败时必须停止后续规划，不可绕过