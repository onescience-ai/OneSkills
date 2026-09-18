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
构建 executor 能力视图台账（每张卡提取以下字段）
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
3. 为每个 executor 技能构建能力视图台账，必须提取以下字段：

| 台账字段 | 说明 | 来源 |
|----------|------|------|
| skill_name | 技能名称 | SKILL.md name 字段 |
| source_of_truth | 真实来源（SKILL.md 路径） | 文件路径 |
| 输入要求 | 该技能接收的输入格式 | SKILL.md 输入契约 |
| 输出产物 | 该技能生成的输出格式 | SKILL.md 输出契约 |
| 负责事项 | 该技能职责范围 | SKILL.md 描述/职责 |
| 不负责事项 | 该技能明确排除的事项 | SKILL.md 边界/禁止 |
| 下游交接对象 | 完成后交接给哪个技能 | SKILL.md 输出契约 |
| 覆盖的原子动作 | 该技能能执行的最小操作单元 | SKILL.md 流程节点 |
| 前置条件 | 执行该技能的前提条件 | SKILL.md 触发条件 |
| 证据段落 | 支撑上述信息的原文引用 | SKILL.md 关键段落 |

4. 执行集合校验：`set(all_executor_skills) == set(read_executor_skills)`
5. 校验通过：标记 `executor_inventory_complete=true` 并继续
6. 校验失败：列出缺失技能，补读后重新校验

> **CFD_S046 失败模式**：global_plan.json 中 read_executor_skills=[] 且 executor_inventory_complete=false，agent-events.log 未见对 onescience-coder、onescience-data-standardizer 等 executor 技能的 SKILL.md 读取记录。orchestrator 在 executor 能力视图未完成校验前过早进入执行阶段，导致 Global Plan 在信息不完整的情况下被生成，后续步骤选择缺乏 executor 能力边界依据。

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

## 路径查找策略与回退机制

### 标准路径模板
executor 技能的 SKILL.md 标准路径为：
```
.opencode/skills/<executor_name>/SKILL.md
```
相对于项目根目录。

### 路径查找流程
1. **首选路径**：使用标准路径模板直接读取
2. **glob 搜索**：若首选路径失败，使用 glob 搜索 `**/skills/<executor_name>/SKILL.md`
3. **递归搜索**：若 glob 失败，在 `.opencode/skills/` 目录下递归搜索
4. **平台适配**：根据当前平台调整路径分隔符（Windows: `\`，Linux: `/`）

### 渐进式回退策略
当路径查找失败时，按以下顺序回退：
1. **检查技能名称拼写**：验证 executor_name 是否正确
2. **检查技能目录结构**：确认 `.opencode/skills/` 目录存在且包含目标技能
3. **使用 PowerShell 命令**：在 Windows 环境下使用 `Get-ChildItem` 命令搜索
4. **记录失败原因**：将失败原因写入 `missing_executor_skills` 列表
5. **继续其他技能读取**：不阻塞整体 inventory 构建

### 平台适配规则
- **Windows PowerShell**：使用 `Get-ChildItem -Recurse -Filter SKILL.md`
- **Linux bash**：使用 `find . -name SKILL.md -path "*/skills/*"`
- **跨平台检测**：在 intake 阶段检测 `$PSVersionTable` 或 `platform.system()`

### 失败处理
- **单个技能读取失败**：记录失败原因，继续其他技能读取
- **多个技能读取失败**：列出所有缺失技能，提供修复建议
- **全部技能读取失败**：停止任务，提示环境配置问题

## 证据来源

[1] OneScience Orchestrator SKILL.md 规范 - 集合校验要求
[2] 归因报告 Task 260 Issue 2 优化计划 - executor inventory 完整性校验知识描述
[U1] 归因报告 CFD_S092 任务分析，用户自有数据，2026-09-17（用户自有, 未经公开源验证）

## 知识边界

- 本卡片定义集合校验的规范流程
- 校验范围限于 executor 技能（type=executor）
- 校验失败时必须停止后续规划，不可绕过