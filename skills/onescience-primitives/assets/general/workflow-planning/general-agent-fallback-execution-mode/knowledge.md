# AI编排系统直接执行降级模式

## 适用范围

面向AI编排系统中专家技能调用失败或无法触发时的降级场景，解决任务因专家召回失败而永久阻塞的问题。适用于所有需要在专家规划路径不可用时自动切换到直接规划路径的编排系统，包括但不限于OneScience编排体系、多智能体协作系统、以及需要高可用性的工作流引擎。

## 输入

- 专家技能调用失败信号
- 已召回的原语资源列表
- 原语工作流节点信息
- 可用的executor技能列表

## 输出

- 直接规划模式激活信号
- 基于原语的Global Plan
- executor技能调度序列
- 任务状态更新

## 流程节点

1. **失败检测** → 检测专家技能调用失败或无法触发
2. **资源评估** → 评估已召回的原语资源和可用的executor技能
3. **路径切换** → 从专家规划路径切换到直接规划路径
4. **Global Plan构建** → 基于原语工作流节点构建Global Plan
5. **Next Step选择** → 从Global Plan中选择下一个执行步骤
6. **Executor调度** → 按计划调度对应的executor技能

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 失败检测阈值 | 3次 | 归因报告 | 连续3次调用失败触发降级 |
| 资源评估时间 | 5秒 | 实践经验 | 评估已召回资源所需时间 |
| 路径切换延迟 | 1秒 | 实践经验 | 切换路径后的等待时间 |

### 校准数值

以下数值来自OneScience编排体系，供量级校准；其他体系需以自身证据重新锚定：

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 降级路径类型 | 1种 | 归因报告 | 跳过专家规划直接构建Global Plan |
| 原语工作流节点 | 6个 | OneScience | 输入预检、时空对齐、方法验证、径流投影、产品生成、物理一致性检验 |
| Executor技能匹配 | 必须 | 归因报告 | 每个工作流节点必须匹配对应的executor技能 |

## 边界与分流

- **原语资源不足**：当已召回的原语资源不足以构建完整工作流时，应向用户报告资源缺口
- **Executor技能缺失**：当某个工作流节点找不到对应的executor技能时，应标记该节点为待处理
- **Global Plan构建失败**：当无法基于原语构建有效的Global Plan时，应触发更高级别的异常处理
- **任务状态不一致**：当降级后任务状态不一致时，应记录状态快照供后续恢复

## 质量检查

- 验证原语资源完整可用
- 验证Global Plan包含所有必要节点
- 验证每个节点都有对应的executor技能
- 验证任务状态正确更新
- 失败处理：构建失败时记录错误日志，使用默认计划模板

## 回退策略

- 当直接规划路径也失败时，向用户报告任务阻塞状态
- 当executor技能调度失败时，尝试其他可用的executor或跳过该节点
- 当所有路径均失败时，生成详细的失败报告供后续分析

## 资源召回建议

- 何时应召回本卡片：当编排智能体在专家召回阶段失败时
- 配套资源：general-agent-tool-interface-contract（工具接口契约）、general-agent-error-recovery-strategy（异常恢复策略）

## 证据来源

[1] LLM-Based Multi-Agent Orchestration: A Survey of Frameworks, Communication Protocols, Future Internet, 2026, DOI: 10.3390/fi18060308
[2] Interactive Speculative Planning: Enhance Agent Efficiency through Co-design of System and User Interface, Wenyue Hua et al., arXiv, 2024, DOI: 10.48550/arXiv.2410.00079
[3] PowerAgentBench-SS: A Benchmark for Agentic AI in Power System Steady-State Studies, Costas Mylonas et al., arXiv, 2026, DOI: 10.48550/arXiv.2606.18789
