# 科学工作流编排系统状态管理

## 适用范围

面向科学计算工作流编排系统，提供任务状态管理、执行清单生成、阶段过渡触发条件、数据传递契约和预检失败恢复机制的设计原则与实现模式。适用于需要管理复杂多阶段工作流的科学计算场景，包括气象模拟、流体动力学、生物信息学和材料科学等领域。

## 输入

- 任务描述和用户目标
- 资源检索结果（resource_retrieval_result.json）
- 任务状态信息（task_state.json）
- 工作流定义和步骤序列

## 输出

- 执行清单（execution-manifest.json）
- 任务状态更新
- 工作流步骤执行结果
- 预检验证结果

## 流程节点

### 1. 资源检索阶段

资源检索是工作流编排的第一步，负责识别任务需求并匹配相关资源。

**操作**：根据任务描述搜索相关资源，包括模型、数据集、组件和工作流规划。

**参数**：
- 任务描述（task_description）
- 领域标识（domain）
- 资源类型过滤（resource_type）

**工具**：资源检索引擎、知识库查询

**质量门禁**：
- 检索到的资源数量 > 0
- 资源相关度评分 > 阈值
- 资源类型与任务需求匹配

### 2. 意图识别阶段

意图识别将资源检索结果转化为结构化的任务意图。

**操作**：分析资源检索结果，提取任务的关键方面和约束条件。

**参数**：
- 资源检索结果（resource_retrieval_result.json）
- 任务上下文（task_context）

**工具**：意图识别算法、上下文分析器

**质量门禁**：
- 识别出的意图方面数量 > 0
- 意图与资源检索结果一致
- 意图覆盖任务的主要需求

### 3. 执行器能力台账构建

执行器能力台账记录可用执行器的能力和约束。

**操作**：枚举可用执行器，构建能力台账。

**参数**：
- 执行器列表（executor_list）
- 任务需求（task_requirements）

**工具**：执行器发现服务、能力匹配算法

**质量门禁**：
- 可用执行器数量 > 0
- 执行器能力满足任务需求
- 执行器约束与任务约束兼容

### 4. 专家提案收集与融合

专家提案收集来自不同专家的建议，并将其融合为统一的执行计划。

**操作**：收集专家提案，进行冲突检测和解决，生成全局计划。

**参数**：
- 专家提案列表（proposals）
- 任务约束（constraints）

**工具**：提案融合算法、冲突解决器

**质量门禁**：
- 提案数量 > 0
- 冲突检测通过
- 全局计划满足所有约束

### 5. 执行清单生成

执行清单是工作流编排的核心输出，定义工作流的完整执行计划。

**操作**：根据全局计划生成execution-manifest.json。

**参数**：
- 全局计划（global_plan）
- 任务元数据（task_metadata）

**工具**：清单生成器、字段验证器

**质量门禁**：
- 清单包含所有必需字段
- 清单字段格式正确
- 清单与全局计划一致

### 6. 预检验证

预检验证确保执行清单的完整性和正确性。

**操作**：验证execution-manifest.json的存在性和格式正确性。

**参数**：
- 执行清单（execution-manifest.json）
- 验证规则（validation_rules）

**工具**：预检脚本、JSON验证器

**质量门禁**：
- 清单文件存在
- 清单JSON格式正确
- 清单包含所有必需字段

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 任务状态流转 | none → scheduled → queued → running → success | [D1] | 任务实例的标准状态流转路径 |
| 任务状态数量 | 12种 | [D1] | 任务实例的可能状态包括none, scheduled, queued, running, success, failed, skipped, upstream_failed, up_for_retry, up_for_reschedule, deferred, awaiting_input, removed |
| 工作流触发方式 | 调度触发、手动触发、外部触发 | [D2] | 工作流可以通过调度器、UI或外部系统触发 |
| 重试策略 | 固定次数和延迟、自定义策略 | [D1] | 任务失败后可以重试，支持固定策略和自定义策略 |
| 超时处理 | execution_timeout、timeout | [D1] | 任务执行有最大时间限制，超时后会触发异常 |

### 校准数值

以下数值来自科学工作流编排系统，供量级校准；其他系统需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 任务状态检查间隔 | 600秒 | [D1] | 任务实例心跳超时检测间隔 |
| 任务心跳超时 | 2秒 | [D1] | 任务实例心跳超时阈值 |
| 检测间隔 | 5秒 | [D1] | 任务心跳超时检测间隔 |
| 默认重试次数 | 1次 | [D2] | 任务失败后的默认重试次数 |
| 重试延迟 | 3分钟 | [D2] | 任务重试的默认延迟时间 |

## 边界与分流

### 资源检索失败

当资源检索未找到匹配资源时，应转向知识补充流程（onescience-knowledge-harvester），补充相关知识后再重新执行资源检索。

### 意图识别失败

当意图识别无法提取有效的任务意图时，应返回资源检索阶段，调整检索策略或扩展资源库。

### 执行器不可用

当所有执行器都不满足任务需求时，应转向执行器扩展流程，添加新的执行器或修改现有执行器的能力。

### 执行清单生成失败

当执行清单生成失败时，应检查全局计划的完整性和一致性，修复问题后重新生成清单。

### 预检验证失败

当预检验证失败时，应检查execution-manifest.json的存在性和格式，修复问题后重新验证。

## 质量检查

### 检查点1：资源检索完成性
- 验证资源检索结果包含至少一个匹配资源
- 验证资源相关度评分超过阈值

### 检查点2：意图识别准确性
- 验证识别出的意图与任务描述一致
- 验证意图覆盖任务的主要需求

### 检查点3：执行器能力匹配
- 验证可用执行器数量 > 0
- 验证执行器能力满足任务需求

### 检查点4：执行清单完整性
- 验证execution-manifest.json存在
- 验证清单包含所有必需字段（task_id, step_sequence, executor_binding, input契约, output契约, quality_gate）
- 验证清单JSON格式正确

### 检查点5：预检验证通过
- 验证workflow_preflight.py退出码为0
- 验证预检证据显示所有检查通过

## 回退策略

### 策略1：知识补充回退
当资源检索失败时，使用onescience-knowledge-harvester技能补充相关知识，然后重新执行资源检索。

### 策略2：执行器扩展回退
当执行器不可用时，扩展执行器库，添加新的执行器或修改现有执行器的能力。

### 策略3：清单重建回退
当执行清单生成失败时，重新检查全局计划，修复问题后重建清单。

### 策略4：预检修复回退
当预检验证失败时，检查并修复execution-manifest.json，然后重新验证。

## 资源召回建议

当遇到以下情况时，应召回本卡片：

1. 科学工作流编排系统的状态管理设计
2. 执行清单生成和验证机制
3. 工作流阶段过渡的触发条件
4. 预检失败恢复策略
5. 任务状态流转和重试机制

配套资源：
- 科学工作流系统文档（Airflow, Nextflow, Snakemake）
- 工作流编排最佳实践
- 状态管理设计模式

## 补充证据（开源文档）

[D1] Apache Airflow Documentation - Tasks, Apache Software Foundation, Version 3.3.1, URL: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html (accessed_at: 2026-09-17T13:00:00Z)

[D2] Apache Airflow Documentation - Dag Runs, Apache Software Foundation, Version 3.3.1, URL: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html (accessed_at: 2026-09-17T13:00:00Z)

[D3] Nextflow Documentation, Seqera Labs, Version latest, URL: https://www.nextflow.io/docs/latest/ (accessed_at: 2026-09-17T13:00:00Z)

[D4] Snakemake Documentation, Snakemake Community, Version 9.27.0, URL: https://snakemake.readthedocs.io/en/stable/ (accessed_at: 2026-09-17T13:00:00Z)

## 证据来源

[1] Apache Airflow Documentation - Tasks, Apache Software Foundation, 2026, URL: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html
[2] Apache Airflow Documentation - Dag Runs, Apache Software Foundation, 2026, URL: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html
[3] Nextflow Documentation, Seqera Labs, 2026, URL: https://www.nextflow.io/docs/latest/
[4] Snakemake Documentation, Snakemake Community, 2026, URL: https://snakemake.readthedocs.io/en/stable/