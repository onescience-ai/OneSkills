# JSON Schema 报告交付契约

## 适用范围

面向需要在自动化工作流或 Agent 系统中验证结构化报告完整性的场景，定义 CLI 工具或 Agent 系统输出报告的 JSON Schema 契约。适用于需要确保报告字段完整、任务身份匹配、数组约束正确的场景。不适用于非 JSON 格式的报告或无需校验的简单输出。

## 输入

- 报告交付契约规范（必填字段、可选字段、字段类型）
- 任务身份信息（task_id、task_name、session_id）
- 校验规则（严格模式/宽松模式）

## 输出

- JSON Schema 定义文件（schema.json）
- 校验结果（通过/失败 + 详细错误信息）
- 校验日志（时间戳、校验模式、错误列表）

## 流程节点

### Step 1：Schema 定义与版本管理
- **操作**：根据报告规范生成 JSON Schema 文件
- **参数**：Schema 版本（Draft 2020-12）、字段定义、约束规则
- **工具**：JSON Schema 编辑器、Schema 验证器
- **质量门禁**：Schema 文件可被标准 JSON Schema 验证器解析

### Step 2：必填字段校验
- **操作**：验证报告包含所有必填顶层字段
- **参数**：必填字段列表（如 task_id, task, summary, issues）
- **工具**：JSON Schema required 关键字
- **质量门禁**：所有必填字段均存在且非空

### Step 3：任务身份匹配
- **操作**：验证报告中的任务身份与预期一致
- **参数**：预期 task_id、预期 task_name、匹配规则（精确匹配/正则匹配）
- **工具**：JSON Schema pattern 关键字、自定义校验器
- **质量门禁**：task_id 和 task_name 均匹配预期值

### Step 4：数组约束验证
- **操作**：验证报告中的数组字段符合约束
- **参数**：数组最小长度、最大长度、元素类型约束
- **工具**：JSON Schema minItems/maxItems/items 关键字
- **质量门禁**：数组字段长度在允许范围内，元素类型正确

### Step 5：格式标准验证
- **操作**：验证报告字段格式符合标准
- **参数**：日期格式（ISO 8601）、字符串编码、数值范围
- **工具**：JSON Schema format 关键字、自定义格式校验器
- **质量门禁**：所有字段格式符合规范，无非法字符

## 关键参数

### 通用判据（方法层，同类体系可参考）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Schema 版本 | Draft 2020-12 | [D1] JSON Schema 官方文档 | 当前推荐的 Schema 版本 |
| 必填顶层字段 | task_id, task, summary, issues | 归因报告契约 | 报告必须包含的核心字段 |
| task_id 格式 | 数字字符串 | 任务规范 | 任务唯一标识符 |
| issues 字段类型 | 数组 | 归因报告契约 | issues 必须是数组类型 |
| summary 字段类型 | 非空字符串 | 归因报告契约 | summary 必须是非空字符串 |
| 校验模式 | strict / lenient | 配置项 | strict 模式拒绝所有警告，lenient 模式仅拒绝错误 |
| 动态引用 | $dynamicRef/$dynamicAnchor | [2] Modern JSON Schema | Draft 2019-09+ 新增特性，支持运行时 Schema 组件引用 |
| 注解依赖验证 | $comment/注解关键字 | [2] Modern JSON Schema | 验证过程依赖注解信息，改变评估模型 |

### 校准数值（体系专属值）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 验证复杂度 | PSPACE-complete | [2] Validation of Modern JSON Schema | 现代 JSON Schema 验证问题的计算复杂度 |
| 编译加速比 | 10x | [3] Blaze | 编译后验证速度提升倍数 |

以下数值来自 JSON Schema 研究论文，供量级校准；其他体系需以自身证据重新锚定。

## 边界与分流

- **Schema 版本不兼容**：当报告使用的 Schema 版本与校验器不兼容时，尝试降级校验或提示升级校验器。
- **额外字段处理**：strict 模式下拒绝包含额外字段的报告；lenient 模式下忽略额外字段但记录警告。
- **嵌套对象校验**：对 issues 数组中的每个对象递归应用 Schema 校验，确保嵌套结构完整。
- **空数组处理**：issues 字段允许为空数组（表示无问题），但不允许为 null 或缺失。

## 质量检查

- Schema 校验通过率检查：使用标准测试用例验证校验器正确性
- 任务身份匹配测试：使用正确/错误的 task_id 和 task_name 测试匹配逻辑
- 数组约束测试：使用空数组、超长数组、类型错误数组测试约束
- 格式校验测试：使用非法日期、非法编码测试格式校验

## 现代 JSON Schema 特性（Draft 2019-09+）

### 动态引用（Dynamic References）
- **特性**：`$dynamicRef` 和 `$dynamicAnchor` 关键字支持运行时 Schema 组件引用
- **应用场景**：在嵌套校验中实现 Schema 片段的动态绑定，适用于报告中不同层级使用不同校验规则
- **复杂度影响**：引入动态引用后，验证问题变为 PSPACE-complete [2]

### 注解依赖验证（Annotation-Dependent Validation）
- **特性**：验证过程依赖 Schema 注解信息（如 `$comment`、`title`、`description`）
- **应用场景**：根据 Schema 注解动态调整校验行为，适用于需要上下文感知的报告校验
- **评估模型变化**：从静态验证变为依赖注解的动态验证 [2]

### 编译优化
- **Blaze 编译器**：将 JSON Schema 编译为优化的验证程序，实现 10x 加速 [3]
- **应用场景**：高吞吐量报告校验场景，如大规模自动化工作流中的实时验证

## 回退策略

- 当 JSON Schema 校验器不可用时，使用基础 JSON 解析 + 字段存在性检查作为降级方案
- 当 Schema 版本不兼容时，使用最宽松的 Schema 进行基础校验
- 当校验器报错信息不明确时，输出原始校验错误并建议人工审查
- 当遇到现代 JSON Schema 特性（动态引用、注解依赖）时，降级到 Draft-07 基础校验

## 资源召回建议

当需要验证 CLI 工具或 Agent 系统输出的结构化报告时召回本卡片。配套资源包括：CLI 非交互执行与故障分类方法论（用于 CLI 执行管理）、领域特定的报告格式规范。

## 批次补充（411-2026-09-21）

本次补充基于"高压晶体结构深度学习搜索"任务的归因报告，针对 CLI 执行和 JSON Schema 校验故障进行了知识扩展。新增了现代 JSON Schema 特性（动态引用、注解依赖验证）的详细说明，以及 Blaze 编译优化的性能数据。

## 批次补充（2026-09-21：任务306案例补充）

### 实际应用案例

基于归因分析任务（任务ID：306，近岸有效波高—周期—波向短期预报）的JSON Schema校验故障案例：

#### JSON Schema校验故障案例
- **故障类型**：报告校验失败
- **错误表现**：缺少顶层字段: ['issues', 'summary', 'task', 'task_id']；包含额外顶层字段: ['error', 'sessionID', 'timestamp', 'type']；task_id与任务索引不一致；task与任务name不一致；summary必须是非空字符串；issues必须是数组
- **诊断方法**：使用report-schema.json验证报告结构；核对任务上下文
- **修复建议**：确保输出格式符合Schema契约；确保任务身份信息正确传递

### 校验流程（任务306案例）
1. **Schema加载**：加载report-schema.json验证规则
2. **字段存在性检查**：验证必填字段issues、summary、task、task_id存在
3. **字段类型检查**：验证issues为数组类型，summary为非空字符串
4. **额外字段检测**：检查是否包含额外顶层字段error、sessionID、timestamp、type
5. **任务身份匹配**：核对task_id与任务索引的一致性，task与任务name的一致性
6. **数组约束验证**：验证issues数组符合Schema约束

### 关键发现
- 缺少必填字段会导致报告校验失败
- 包含额外字段会导致报告校验失败（strict模式下）
- 任务身份不匹配（task_id/task）会导致报告交付失败
- 字段类型错误会导致报告校验失败

## 补充证据

[D1] "JSON Schema Official Documentation", JSON Schema Organization, version 2020-12, URL: https://json-schema.org/（accessed 2026-09-17，权威标准文档）

## 批次补充（2026-09-22：任务45案例补充）

### 实际应用案例

基于归因分析任务（任务ID：45，多功能基序支架蛋白生成）的JSON Schema校验故障案例：

#### JSON Schema校验故障案例
- **故障类型**：报告校验失败
- **错误表现**：缺少顶层字段: ['issues', 'summary', 'task', 'task_id']；包含额外顶层字段: ['error', 'sessionID', 'timestamp', 'type']；task_id与任务索引不一致；task与任务name不一致；summary必须是非空字符串；issues必须是数组
- **诊断方法**：使用report-schema.json验证报告结构；核对任务上下文
- **修复建议**：确保输出格式符合Schema契约；确保任务身份信息正确传递

### 校验流程（任务45案例）
1. **Schema加载**：加载report-schema.json验证规则
2. **字段存在性检查**：验证必填字段issues、summary、task、task_id存在
3. **字段类型检查**：验证issues为数组类型，summary为非空字符串
4. **额外字段检测**：检查是否包含额外顶层字段error、sessionID、timestamp、type
5. **任务身份匹配**：核对task_id与任务索引的一致性，task与任务name的一致性
6. **数组约束验证**：验证issues数组符合Schema约束

### 关键发现
- 缺少必填字段会导致报告校验失败
- 包含额外字段会导致报告校验失败（strict模式下）
- 任务身份不匹配（task_id/task）会导致报告交付失败
- 字段类型错误会导致报告校验失败
- 归因分析智能体退出码为1通常表示报告校验失败

## 证据来源

[1] "Adamant: a JSON schema-based metadata editor for research data management workflows", Siffa et al., F1000Research, 2022, DOI: 10.12688/f1000research.110875.2
[2] "Validation of Modern JSON Schema: Formalization and Complexity", Attouche et al., Proceedings of the ACM on Programming Languages, 2024, DOI: 10.1145/3632891
[3] "Blaze: Compiling JSON Schema for 10x Faster Validation", Viotti & Mior, Proceedings of the VLDB Endowment, 2025, DOI: 10.14778/3773749.3773764
[4] "Elimination of annotation dependencies in validation for Modern JSON Schema", Attouche et al., Theoretical Computer Science, 2025, DOI: 10.1016/j.tcs.2025.115645
[5] 基于任务306归因报告中的JSON Schema校验故障案例总结
[6] 基于任务45归因报告中的JSON Schema校验故障案例总结（新增）
