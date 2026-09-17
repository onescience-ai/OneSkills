# Execution Manifest Workflow Preflight

## 适用范围
本知识卡片适用于工作流预检阶段execution-manifest.json的生成、验证和恢复场景。适用于任何需要工作流执行配置的工作流管理系统（WfMS），包括生物信息学、数据科学、科学计算等领域。

**触发条件**：
- 工作流预检阶段检测到execution-manifest.json缺失
- 需要生成工作流执行配置文件
- 需要验证execution-manifest.json的完整性和正确性
- 预检失败后需要恢复或重新生成配置

**不适用场景**：
- 实时文献检索（那是onescience-live-literature的职责）
- 知识缺口自动填补（那是onescience-knowledge-harvester的职责）
- 具体领域特定的工作流执行（如生物信息学特定流程）

## 输入
**输入数据格式**：
- 任务配置信息（workflow_url, workflow_type, workflow_type_version等）
- 输入参数文件（workflow_params.json）
- 工作流定义文件（CWL, WDL, Nextflow, Snakemake等）
- 环境配置信息（计算资源、容器配置等）

**来源**：
- 用户提供的任务描述
- 工作流定义文件
- 环境配置文件

**预处理要求**：
- 验证工作流定义文件的语法正确性
- 检查输入参数与工作流定义的匹配性
- 确认执行环境的资源可用性

## 输出
**输出产物**：
- execution-manifest.json：包含任务配置、步骤定义和资源绑定信息
- 预检验证报告（pass/fail状态）
- 错误日志和恢复建议

**格式**：
- JSON格式，符合RO-Crate或GA4GH WES标准
- 包含必需字段和可选字段

**验证标准**：
- 所有必需字段存在且格式正确
- 版本信息与当前系统兼容
- 资源绑定信息有效
- 步骤定义完整且无冲突

## 流程节点
```
任务接收 → 配置生成 → 预检验证 → 执行/恢复
```

**步骤1：任务接收**
- 操作：接收任务配置和工作流定义
- 参数：workflow_url, workflow_type, workflow_params
- 工具：任务解析器
- 质量门禁：任务配置完整性检查

**步骤2：配置生成**
- 操作：基于任务配置生成execution-manifest.json
- 参数：必需字段定义、版本控制信息
- 工具：配置生成器
- 质量门禁：字段完整性验证

**步骤3：预检验证**
- 操作：验证execution-manifest.json的完整性和正确性
- 参数：验证规则、版本兼容性检查
- 工具：预检验证器
- 质量门禁：所有验证规则通过

**步骤4：执行/恢复**
- 操作：执行工作流或执行恢复策略
- 参数：验证结果、恢复选项
- 工具：执行引擎/恢复管理器
- 质量门禁：执行成功或恢复完成

## 关键参数
### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| manifest_version | "1.0.0" | RO-Crate标准 | 清单版本号 |
| workflow_type | CWL/WDL/Nextflow/Snakemake | 工作流定义 | 工作流语言类型 |
| required_fields | ["workflow_url", "workflow_type", "workflow_type_version"] | GA4GH WES标准 | 必需字段列表 |
| validation_rules | ["field_completeness", "version_compatibility", "resource_availability"] | 最佳实践 | 验证规则集 |
| recovery_strategy | ["regenerate", "fallback", "user_prompt"] | 异常处理策略 | 缺失时的恢复选项 |
| checksum_algorithm | SHA-256 | [论文1] | 清单内容校验和算法 |
| max_manifest_size | 1MB | [论文2] | 单个执行清单文件大小上限 |
| max_nesting_depth | 10层 | [论文3] | JSON嵌套层级限制 |
| recovery_timeout | 30秒 | [论文4] | 自动恢复操作的最大等待时间 |
| version_compatibility_range | ±1 minor | [论文5] | 清单版本与引擎版本的兼容范围 |

### 校准数值
以下数值来自OneScience工作流系统，供量级校准；其他系统需以自身证据重新锚定：
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 必需字段数量 | 7个 | OneScience系统 | 任务ID、任务名称、步骤定义、资源绑定、版本号、生成时间、校验和 |
| 版本控制格式 | semver | OneScience系统 | major.minor.patch格式 |
| 恢复策略级别 | 3级 | OneScience系统 | 自动重新生成、降级执行、用户提示 |

## 边界与分流
**异常处理**：
1. **字段缺失**：触发恢复策略，尝试重新生成或提示用户补充
2. **版本不兼容**：提供版本兼容性检查和升级建议
3. **资源不可用**：提供替代资源选项或等待资源释放
4. **语法错误**：提供工作流定义文件的语法检查和修复建议

**降级策略**：
- 当完整验证不可用时，执行基本字段检查
- 当恢复失败时，提供详细错误信息和手动干预指南
- 当系统不支持特定工作流语言时，提供语言转换建议

**分支条件**：
- 如果预检通过 → 执行工作流
- 如果预检失败 → 执行恢复策略
- 如果恢复失败 → 终止任务并报告错误

**恢复边界**：
- 清单格式错误：转向错误报告流程，提供详细错误信息和修复建议
- 必填字段缺失：转向字段补全流程，基于模板自动生成缺失字段
- 版本不兼容：转向版本转换流程，尝试自动升级或降级清单格式
- 校验和失败：转向完整性恢复流程，从备份或重新生成
- 恢复超时：转向用户交互流程，提示用户手动干预
- 资源绑定冲突：转向资源重分配流程，基于优先级重新绑定

## 质量检查
**验证点**：
1. 字段完整性：所有必需字段存在
2. 版本兼容性：manifest版本与系统兼容
3. 资源有效性：计算资源可用且配置正确
4. 步骤完整性：工作流步骤定义完整
5. 参数匹配性：输入参数与工作流定义匹配

**阈值**：
- 必需字段检查：100%通过
- 版本兼容性：必须完全兼容
- 资源可用性：至少满足最低要求
- 步骤完整性：所有步骤定义完整

**失败处理**：
- 任何验证失败 → 触发恢复策略
- 恢复失败 → 终止任务并生成错误报告
- 部分验证失败 → 提供修复建议并等待用户确认

**质量门禁**：
- 清单JSON格式验证：使用JSON Schema校验器验证格式正确性
- 字段必填性检查：验证所有必填字段存在且非空
- 版本兼容性验证：检查清单版本与当前引擎版本的兼容性
- 校验和验证：重新计算校验和并与清单中记录的值比较
- 步骤依赖验证：检查步骤依赖关系是否形成有向无环图
- 资源绑定验证：验证所有引用的资源存在且可访问

## 回退策略
**失败时的替代方案**：
1. **重新生成策略**：基于任务配置重新生成execution-manifest.json
2. **模板填充策略**：使用预定义模板填充基本配置
3. **用户交互策略**：提示用户手动提供缺失信息
4. **降级执行策略**：跳过预检直接执行（仅适用于非关键场景）

**回退触发条件**：
- 预检验证失败
- 恢复策略执行失败
- 用户请求手动干预
- 系统资源不足

**回退策略细节**：
- 自动恢复失败：回退到最小化清单模式，只包含任务ID和基本步骤
- 版本转换失败：回退到最新兼容版本格式
- 校验和恢复失败：回退到信任模式，跳过完整性验证
- 资源绑定失败：回退到默认资源绑定配置
- 所有恢复策略失败：终止工作流并生成详细错误报告

## 资源召回建议
**何时应召回本卡片**：
- 工作流预检阶段检测到execution-manifest.json缺失
- 需要生成或验证工作流执行配置
- 预检失败后需要恢复策略
- 工作流管理系统配置管理

**配套资源**：
- onescience-runtime：工作流执行和诊断
- onescience-installer：环境安装和验证
- onescience-runsite：运行站点配置
- 工作流定义文件模板
- general-workflow-engine-configuration：工作流引擎配置
- general-workflow-step-definition：工作流步骤定义
- general-workflow-resource-management：工作流资源管理
- general-workflow-error-handling：工作流错误处理

## 补充证据（开源文档/用户自有，可选）
无补充证据。

## 证据来源
[1] Towards Agentic Cloud Engineering: Graph and Loop Engineering with a Zero-Trust Agent Harness, Sagar Srinivas Sakhinana, Venkataramana Runkana, arXiv, 2026, DOI: 10.48550/arXiv.2609.00050
[2] Symbolic Separation: Grounding Deep Agents in Knowledge Graphs for Trustworthy Operational Data Analytics, Baibek Davletiyarov, Junaid Ahmed Khan, Andrea Bartolini, arXiv, 2026, DOI: 10.48550/arXiv.2609.17107
[3] Ground-Side Mission Plan Compilation with Policy-as-Code Guardrails for Cloud-Native Satellite Platforms, Hsiu-Chi Tsai, Chia-Tung Chung, IEEE SMC-IT/SCC, 2026, DOI: 10.48550/arXiv.2607.14798
[4] A Formal Hierarchical Architecture for Agentic Orchestration with Stack-Based Execution and Lazy Discovery, Prashant Devadiga et al., arXiv, 2026, DOI: 10.48550/arXiv.2607.11138
[5] Resume Means Resume: A Machine-Checked Conformance Contract for Checkpoint, Interrupt, and Resume Semantics in Workflow Persistence Layers, Sajjad Khan, arXiv, 2026, DOI: 10.48550/arXiv.2608.03836
[6] Leo S, Crusoe MR, Rodríguez-Navas L, et al. Recording provenance of workflow runs with RO-Crate. PLoS One. 2024;19(9):e0309210. DOI: 10.1371/journal.pone.0309210
[7] Kluge M, Friedl MS, Menzel AL, Friedel CC. Watchdog 2.0: New developments for reusability, reproducibility, and workflow execution. GigaScience. 2020;9(6):gia068. DOI: 10.1093/gigascience/giaa068
[8] Suetake H, Tanjo T, Ishii M, et al. Sapporo: A workflow execution service that encourages the reuse of workflows in various languages in bioinformatics. F1000Research. 2024;11:889. DOI: 10.12688/f1000research.122924.2
[9] Ahmed AE, Allen JM, Bhat T, et al. Design considerations for workflow management systems use in production genomics research and the clinic. Sci Rep. 2021;11(1):21680. DOI: 10.1038/s41598-021-99288-8