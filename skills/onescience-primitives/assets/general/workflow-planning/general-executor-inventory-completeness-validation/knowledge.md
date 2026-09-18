# Executor Inventory 完整性校验流程

## 适用范围

**触发条件**：
- orchestrator 需要为任务选择executor技能
- 系统存在多个executor技能（>1个）
- 规划阶段需要评估所有可用executor的能力

**适用场景**：
- 多技能编排系统的能力台账构建
- 任务规划前的executor能力评估
- 防止因能力台账不完整导致的技能选择错误
- 确保所有可用executor都被考虑在规划过程中

**不适用场景**：
- 单executor系统（无需集合校验）
- 静态executor列表（无动态发现机制）
- 实时执行阶段（inventory校验属于规划阶段）

## 输入

**必需输入**：
- 所有executor技能的SKILL.md文件路径列表（all_executor_skills）
- 已读取的executor技能列表（read_executor_skills）

**预处理要求**：
- 通过glob或文件扫描获取所有executor技能的SKILL.md路径
- 记录已读取的executor技能列表

## 输出

**输出产物**：
- 校验结果报告，包含：
  - all_executor_skills集合
  - read_executor_skills集合
  - 差集（缺失的executor技能）
  - 校验通过/失败状态
  - 缺失技能的补读建议

**验证标准**：
- 校验结果准确反映集合差异
- 缺失技能列表完整
- 补读建议可执行

## 流程节点

### Step 1：收集所有executor技能路径
- **操作**：通过glob搜索所有executor技能的SKILL.md文件
- **参数**：搜索模式`skills/*/SKILL.md`，排除非executor技能
- **工具**：文件系统搜索、模式匹配
- **质量门禁**：找到所有executor技能，无遗漏

### Step 2：记录已读取的executor技能
- **操作**：记录已通过read工具读取的executor技能列表
- **参数**：agent-events.log中的read操作记录
- **工具**：日志分析、列表构建
- **质量门禁**：记录准确，无重复或遗漏

### Step 3：集合校验
- **操作**：比较set(all_executor_skills)和set(read_executor_skills)
- **参数**：两个集合
- **工具**：集合运算、差集计算
- **质量门禁**：校验逻辑正确，差集计算准确

### Step 4：生成校验报告
- **操作**：生成结构化校验报告
- **参数**：校验结果、缺失技能列表
- **工具**：报告生成、格式化
- **质量门禁**：报告格式规范，信息完整

### Step 5：补读缺失技能（如校验失败）
- **操作**：读取缺失的executor技能SKILL.md文件
- **参数**：缺失技能路径列表
- **工具**：文件读取、技能加载
- **质量门禁**：所有缺失技能都被读取，列表更新

### Step 6：重新校验（补读后）
- **操作**：重新执行集合校验，确认通过
- **参数**：更新后的read_executor_skills集合
- **工具**：集合运算
- **质量门禁**：校验通过，集合相等

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 校验时机 | 规划阶段 | [U1] | 必须在Global Plan生成前执行 |
| 校验方法 | 集合相等性检查 | [U1] | set(all) == set(read) |
| 校验失败处理 | 停止规划 | [U1] | 必须补齐缺失技能后才能继续 |
| 补读机制 | 自动触发 | [U1] | 校验失败时自动读取缺失技能 |
| 校验结果记录 | 写入global_plan.json | [U1] | executor_inventory_complete字段 |

### 校准数值（体系专属）

以下数值来自任务260（多源遥感南极冰架表面融化识别）体系，供量级校准；其他体系需以自身证据重新锚定：

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| all_executor_skills数量 | 14 | [U1] | 包含onescience-coder, onescience-data-analyzer等 |
| read_executor_skills数量 | 3 | [U1] | 仅读取了onescience-coder, onescience-data-analyzer, onescience-data-standardizer |
| 校验结果 | 失败 | [U1] | 3 ≠ 14，集合不相等 |
| inventory_complete标记 | true（错误） | [U1] | 标记为complete但实际不完整 |

## 边界与分流

**关键前提不成立时的改道方案**：

1. **无法获取所有executor技能列表** → 转向静态配置模式，使用预定义的executor列表
2. **已读取列表记录不准确** → 转向日志重放模式，重新解析agent-events.log
3. **校验逻辑本身有缺陷** → 转向人工审核模式，由用户确认校验结果
4. **补读操作失败** → 转向降级规划模式，仅使用已读取的executor技能

## 质量检查

**验证点**：
1. all_executor_skills列表完整性（所有executor技能都被发现）
2. read_executor_skills记录准确性（已读取技能正确记录）
3. 集合校验逻辑正确性（差集计算无误）
4. 校验结果与标记一致性（inventory_complete标记反映实际状态）

**阈值**：
- 校验准确率：100%
- 缺失技能识别率：100%
- 补读成功率：100%

**失败处理**：
- 校验失败 → 停止规划，补齐缺失技能
- 补读失败 → 记录错误，请求人工干预
- 标记不一致 → 修正标记，重新校验

## 回退策略

**失败时的替代方案**：
1. **自动校验机制失败** → 降级为人工校验（用户确认executor列表）
2. **文件系统访问受限** → 使用配置文件中的executor列表
3. **校验结果不确定** → 默认视为失败，要求补全

## 资源召回建议

**何时应召回本卡片**：
- orchestrator在规划阶段需要构建executor能力台账
- 发现executor_inventory_complete标记与实际读取数量不符
- 任务涉及多个executor技能的选择和调度

**配套资源**：
- `general-task-pre-execution-confirmation-workflow`：预确认流程
- `general-skill-selection-optimization`：技能选择优化
- `general-workflow-planning-validation`：工作流规划验证

## 补充证据（开源文档/用户自有）

[D1] "OneScience Orchestrator Skill Documentation", OneScience Team, current version, URL: https://github.com/anomalyco/opencode/blob/main/skills/onescience-orchestrator/SKILL.md（accessed 2026-09-17，orchestrator技能文档）

[U1] 任务260归因报告：global_plan.json中executor_inventory_complete=true但read_executor_skills仅3项而all_executor_skills有14项，agent-events.log显示glob找到所有SKILL.md后仅read了3个（用户自有, 经归因分析佐证）

## 证据来源

[1] 任务260归因报告，任务ID: 260，任务：多源遥感南极冰架表面融化识别，报告路径：E:\works\zhognkeshuguang\knowledge_oneskills\onescience-knowledge-driven-feedback\results\attr-w3\260\report.json

[2] "OneScience Orchestrator Skill Documentation", OneScience Team, 2026, URL: https://github.com/anomalyco/opencode/blob/main/skills/onescience-orchestrator/SKILL.md