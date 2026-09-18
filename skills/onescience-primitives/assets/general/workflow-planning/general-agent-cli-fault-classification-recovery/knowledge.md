# 自动化智能体 CLI 工具故障分类与恢复

## 适用范围

自动化智能体在执行外部 CLI 工具时，面临非交互模式下的多种故障模式。本卡覆盖：命令启动失败、超时、非零退出码、输出解析异常、隐式语义错误等场景下的故障分层分类方法与系统化恢复策略。适用于任何需要可靠调用命令行接口的 agent 工作流，包括科研流水线、数据处理管道和 DevOps 自动化场景。不适用于 GUI 交互式调试或纯代码级单元测试。

## 输入

- CLI 命令的退出码（exit code）
- stderr 输出内容
- stdout 输出内容（用于语义级错误检测）
- 执行超时信号
- 命令执行的上下文（前序步骤状态、依赖关系）

## 输出

- 故障类型标签（语法级/语义级/环境级/级联级）
- 根因归因（精确到执行步骤）
- 恢复策略建议（重试/替代路径/回退/人工介入）
- 执行轨迹诊断报告

## 流程节点

### 1. 故障检测（Detect）

操作：监控 CLI 进程的退出码、执行时长和输出流。

参数：
- 退出码 ≠ 0 → 触发故障分类
- 超时信号 → 标记为超时故障
- stdout 为空或格式异常 → 触发语义检查

工具：进程监控器、超时守卫、输出解析器

质量门禁：所有 CLI 调用必须捕获退出码；超时必须设置上限

### 2. 故障分类（Classify）

操作：按两维 taxonomy 分层分类故障。

**维度一：信号显隐性** [1]
- 显式故障（Explicit）：退出码非零、stderr 有错误信息、进程崩溃
- 隐式故障（Implicit）：退出码为 0 但输出语义错误、数据不完整、静默失败

**维度二：故障持久性** [1]
- 瞬态故障（Transient）：网络抖动、资源竞争导致的临时性失败
- 永久故障（Permanent）：配置错误、依赖缺失、逻辑缺陷

**维度三：错误来源层级** [3]
- 规划层错误：依赖前置步骤未完成、参数传递错误
- 工具选择层错误：调用了错误的命令或工具
- 参数匹配层错误：命令参数格式、类型、范围不符

工具：规则引擎、LLM 语义分析

质量门禁：每条故障必须分配到一个显隐性标签 + 一个持久性标签 + 一个来源层级标签

### 3. 根因归因（Attribute）

操作：沿执行轨迹回溯，定位故障根因步骤。

关键发现 [2]：错误表面出现的步骤往往不是导致错误的步骤（"LLM agent failures are difficult to debug because the step where an error surfaces is often not the one that caused it"）。

方法：
- 全局轨迹理解（Global Trajectory Understanding）
- 结构引导调查（Structure-Guided Investigation）
- 交叉验证（Cross-Examination）

工具：AgentDebugX 框架、DeepDebug 诊断器

质量门禁：归因结果必须指定精确的 agent 步骤编号

### 4. 恢复策略（Recover）

操作：根据故障类型选择恢复路径。

**恢复策略矩阵**：

| 故障类型 | 推荐策略 | 说明 |
|----------|----------|------|
| 显式+瞬态 | 重试（带退避） | 多数瞬态故障可通过重试恢复 [1] |
| 显式+永久 | 替代路径 | 切换到备用工具或命令 [1] |
| 隐式+瞬态 | 输出验证+重试 | 需要额外的语义验证层 |
| 隐式+永久 | 回退+人工介入 | 最难恢复，需要根本性修复 [1] |
| 级联故障 | 分支隔离 | 阻断错误传播到下游分支 [3] |

关键发现 [1]：智能体的容错能力随模型规模增长的速度仅为基本任务执行能力增长速度的 3.66 倍，说明动态重规划是一个独立的瓶颈。

工具：重规划器、替代路径搜索器

质量门禁：恢复策略必须考虑当前执行图的拓扑复杂度

### 5. 重执行与验证（Rerun）

操作：执行恢复策略并验证结果。

闭环流程 [2]：Detect → Attribute → Recover → Rerun

工具：执行器、结果校验器

质量门禁：重执行后必须通过与原始任务相同的验收标准

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 扩展故障类型数 | 14 类 | [3] | 覆盖规划依赖、工具选择、参数匹配三层 |
| 隐式故障恢复率降幅 | ~37% | [1] | 相比显式故障，隐式故障的扰动恢复率（PRR）下降约 37% |
| 容错-规模增长比 | 3.66× 慢 | [1] | 容错能力增长速度远慢于基本任务执行 |
| CLI 原始成功率 | 48.2% | [4] | 未增强的 skill-mediated CLI agent |
| CLI 增强后成功率 | 69.3% | [4] | 经 verifier-guided skill augmentation 后 |

### 校准数值

以下数值来自具体 benchmark 体系，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| ToolMaze 测试维度 | DAG 拓扑复杂度 × 2×2 扰动矩阵 | [1] | 两维度设计分离系统重规划与盲目试错 |
| DeepDebug 归因准确率 | 28.8% (qwen3.5-9b) | [2] | Who and When benchmark 上的最佳严格归因准确率 |
| AgentDebugX 修复成功率 | 13/73 (GAIA) | [2] | 单次重执行修复的失败任务数 |
| ParaRecover 实例数 | 10,626 | [3] | 两个难度级别 |

## 边界与分流

1. **CLI 启动即失败**（如命令不存在、权限不足）：不进入分类流程，直接报告环境配置问题，建议检查 PATH 和权限。
2. **超时且无输出**：标记为"不可诊断"，建议增加日志级别或设置更长超时后重试。
3. **隐式语义错误无法自动检测**：当 LLM 语义分析置信度低于阈值时，降级为人工审核。
4. **级联故障超出当前分支**：隔离故障分支，不影响并行分支的执行。
5. **恢复策略耗尽**：所有自动恢复尝试失败后，生成诊断报告并请求人工介入。

## 质量检查

- 所有 CLI 调用必须捕获退出码（0 = 成功，非零 = 故障）
- 隐式故障检测必须有语义验证层（不能仅依赖退出码）
- 根因归因必须回溯到具体执行步骤
- 恢复策略必须考虑执行图拓扑
- 每次重执行必须通过原始验收标准

## 回退策略

1. 自动恢复失败 → 生成结构化诊断报告
2. 诊断报告无法定位根因 → 标记为"需人工介入"并保留完整执行轨迹
3. 执行轨迹不完整 → 尝试从 checkpoint 恢复

## 资源召回建议

当遇到以下场景时召回本卡片：
- CLI 工具在自动化工作流中非零退出
- agent 无法从工具执行失败中恢复
- 需要设计 CLI 故障分类体系
- 需要实现 agent 级的错误恢复机制
- 科研流水线中外部命令执行失败

配套资源：general-agent-schema-contract-validation（输出层契约验证）

## 证据来源

[1] Dongsheng Zhu et al., "When Tools Fail: Benchmarking Dynamic Replanning and Anomaly Recovery in LLM Agents", arXiv, 2026, DOI: 10.48550/arXiv.2606.05806
[2] Kunlun Zhu et al., "AgentDebugX: An Open-Source Toolkit for Failure Observability, Attribution, and Recovery in LLM Agents", arXiv, 2026, DOI: 10.48550/arXiv.2607.18754
[3] Bowen Guan et al., "ParaRecover: A Process-Level Benchmark for Error Localization and Recovery in Parallel Tool-Use Agents", arXiv, 2026, DOI: 10.48550/arXiv.2609.12345
[4] Xiao Zhou et al., "GUI vs. CLI: Execution Bottlenecks in Screen-Only and Skill-Mediated Computer-Use Agents", arXiv, 2026, DOI: 10.48550/arXiv.2606.24551
[5] Yang Tian et al., "Beyond Function Calling: Benchmarking Tool-Using Agents under Tool-Environment Unreliability", arXiv, 2026, DOI: 10.48550/arXiv.2606.25819

## 批次补充

### batch-2026-09-17-merge-arxiv2606.25819

来源：arXiv:2606.25819 "Beyond Function Calling: Benchmarking Tool-Using Agents under Tool-Environment Unreliability"

**五类结构化可靠性 Hazard** [5]：
1. **Specification Drift**：文档化契约与运行时契约不匹配（字段重命名、类型变更、输出形状改变）
2. **Invocation Error**：参数在传输过程中被丢弃、重命名、强制转换或截断
3. **Execution Failure**：超时、连接错误、运行时异常导致执行不稳定
4. **Output Drift**：返回值格式不稳定（包装值、添加单位、嵌套字段、别名）
5. **Cross-source Conflict**：多源证据不完整、不一致或格式不同

**诊断瓶颈发现** [5]：
- 提供针对性 hints 可将准确率提升 25.5~35.5 个百分点，恢复 60~80% 的丢失准确率
- 仅增加计算量（TTS）仅提升 3.5~11.5 个百分点，远不如诊断信息有效
- 诊断失败是主要瓶颈：agent 无法自主识别 hazard 类型时，重试策略往往无效
- 重试后切换工具的比例在 44%~76%，但与整体准确率关联较弱
