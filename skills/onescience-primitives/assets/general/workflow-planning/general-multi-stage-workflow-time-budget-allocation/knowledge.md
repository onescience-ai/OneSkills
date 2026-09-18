# 多阶段科研工作流时间预算分配

## 适用范围

面向包含数据接入、预处理、训练、推理、评估等多阶段的科研工作流编排场景，解决规划阶段耗时过长挤压执行预算、各步骤缺乏独立超时保护、execution-manifest.json缺失导致预检失败等问题。适用于5步及以上的工作流任务。

**不适用场景**：
- 单步骤或2步以内的简单任务（无需精细预算分配）
- 纯推理无训练的工作流（步骤较少，预算压力低）

## 输入

- 工作流步骤列表（含executor分配）
- 总超时预算（秒或步骤数）
- 各步骤的预估复杂度

## 输出

- 时间预算分配方案（规划/执行比例）
- 各步骤独立超时阈值
- execution-manifest.json（含步骤状态和依赖关系）

## 流程节点

### Step 1：规划阶段预算设定
- **操作**：为Global Plan生成阶段设定预算上限（时间或步骤数）
- **参数**：规划预算≤总预算的20%，或≤30s绝对时间
- **工具**：计时器+阈值检查
- **质量门禁**：Global Plan在预算内生成

### Step 2：execution-manifest.json创建
- **操作**：Global Plan生成后立即创建execution-manifest.json，记录所有步骤ID、executor、依赖关系、初始状态=pending
- **参数**：不依赖具体步骤执行，仅依赖Global Plan
- **工具**：JSON文件写入
- **质量门禁**：manifest包含所有规划步骤，状态均为pending

### Step 3：各步骤独立超时分配
- **操作**：为每个步骤分配独立超时预算（不共享总预算）
- **参数**：单步骤超时=总预算/步骤数×1.5（留缓冲），或固定值如120s
- **工具**：步骤级计时器
- **质量门禁**：任一步骤超时不影响其他步骤的预算

### Step 4：步骤间依赖检查
- **操作**：检查当前步骤的前置依赖是否满足（manifest中状态=completed）
- **参数**：依赖不满足时跳过当前步骤并标记skipped
- **工具**：manifest状态查询
- **质量门禁**：无循环依赖，所有依赖关系在manifest中明确记录

### Step 5：超时后fallback路径
- **操作**：步骤超时时，记录失败原因，尝试fallback路径（如使用合成数据、跳过非关键步骤）
- **参数**：fallback条件=超时或错误次数>阈值
- **工具**：错误计数器+fallback逻辑
- **质量门禁**：超时步骤有明确的fallback记录

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 规划阶段预算占比 | ≤20%总预算 | [1] | 规划耗时过长会挤压执行时间 |
| 执行阶段预算占比 | ≥80%总预算 | [1] | 核心价值在执行而非规划 |
| execution-manifest创建时机 | Global Plan生成后立即 | [1] | 不依赖步骤执行，避免缺失 |
| 单步骤超时=总预算/步骤数×1.5 | 缓冲系数1.5 | [D1] | 允许单步骤超时但不超总预算 |
| 步骤级独立超时 | 是（非共享） | [1] | 避免单步骤超时影响全局 |
| 规划阶段并行度 | 尽量并行 | [D1] | 使用concurrent.futures并行读取 |

### 校准数值（体系专属）

以下数值来自某5步CFD工作流任务（data-standardizer→data-standardizer→trainer→infer→data-analyzer），供量级校准；其他任务需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 规划阶段实际耗时 | ~60%总预算 | [1] | 严重超标，应<20% |
| 执行阶段实际耗时 | ~40%总预算 | [1] | 仅完成s01，s02-s05未执行 |
| 步骤数 | 5步 | [1] | data-standardizer×2+trainer+infer+data-analyzer |
| s01代码错误修复耗时 | 100+步骤 | [1] | 4次连续错误修复 |
| execution-manifest状态 | 未生成 | [1] | 导致预检blocked |

## 边界与分流

- **规划阶段超时**：降级为最小化Global Plan（仅列出步骤ID，不读取executor详情）
- **单步骤超时**：标记该步骤为failed，继续执行后续独立步骤（非阻塞依赖）
- **execution-manifest.json缺失**：预检阶段直接返回blocked，不进入执行
- **所有步骤超时**：记录完整超时报告，建议用户增加预算或简化任务

## 质量检查

- 规划阶段耗时≤总预算的20%
- execution-manifest.json在Global Plan生成后≤5步内创建
- 每个步骤有独立的超时阈值和实际耗时记录
- 超时步骤有fallback路径记录
- manifest中步骤状态与实际执行一致

## 回退策略

- 规划超时：使用最小化plan（仅步骤ID列表）
- 步骤超时：跳过该步骤，标记failed，继续后续步骤
- manifest缺失：预检返回blocked，建议重新执行

## 资源召回建议

当任务编排涉及≥3个步骤的工作流时召回本卡片。配套资源：onescience-orchestrator的Global Plan生成和execution-manifest创建阶段。

## 补充证据（开源文档）

[D1] "concurrent.futures - Asynchronous execution of callables", Python 3.14 documentation, https://docs.python.org/3/library/concurrent.futures.html（accessed 2026-09-17，交叉验证）

## 证据来源

[1] CFD_S006归因报告：workflow_steps_s02_through_s05_not_executed issue，规划阶段消耗约60%超时预算，执行阶段仅完成s01；execution-manifest.json始终未创建，预检因缺失该文件失败
