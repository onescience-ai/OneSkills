# 工作流预检清单验证与恢复

## 适用范围

面向工作流编排系统中的预检阶段，验证 execution manifest 文件的完整性、正确性和可恢复性。适用于任何需要预检清单（manifest）来定义任务配置、步骤定义、资源绑定和验证契约的工作流系统。不适用于无需预检或静态配置的简单脚本执行。

## 输入

- **execution manifest 文件**：JSON 格式，包含工作流的完整定义。
- **预检脚本**：如 `workflow_preflight.py`，负责解析 manifest 并验证其有效性。
- **工作流上下文**：任务 ID、目标、约束条件等。

## 输出

- **预检结果**：成功/失败状态，包含验证详情。
- **错误报告**：缺失字段、格式错误、版本不匹配等。
- **恢复建议**：当 manifest 缺失或无效时，提供重新生成或修复的路径。

## 流程节点

1. **Manifest 加载** → 读取 execution manifest 文件，解析 JSON 结构。
2. **字段验证** → 检查必需字段是否存在、类型是否正确、值是否在允许范围内。
3. **版本兼容性检查** → 验证 manifest 版本与预检脚本版本是否兼容。
4. **资源绑定验证** → 确认引用的资源（文件、环境变量、服务）是否存在且可访问。
5. **步骤定义验证** → 检查步骤依赖关系、脚本路径、成功门控条件。
6. **预检执行** → 运行预检脚本，收集验证结果。
7. **异常处理** → 根据错误类型执行恢复策略（重新生成、降级、提示用户）。

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| schema_version | 整数（如 4） | [D1] | manifest 模式版本，用于兼容性检查 |
| required_fields | 列表 | [D1] | 必需字段列表，如 workflow_name, steps, outputs |
| version_control | 语义化版本 | [D1] | manifest 版本号，遵循 semver 规范 |
| validation_checks | 列表 | [D1] | 每个步骤的验证检查项 |
| failure_policy | 对象 | [D1] | 错误处理策略，如 on_error: stop/retry/continue |

### 校准数值

以下数值来自 deterministic-workflow-builder 体系，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| timeout_seconds | 30 | [D1] | 步骤超时时间，防止无限等待 |
| retry_limit | 0 | [D1] | 重试次数，0 表示不重试 |
| min_size_bytes | 1 | [D1] | 产出文件的最小大小，确保非空 |
| retention_days | 7 | [D1] | 产出文件保留天数 |

## 边界与分流

- **manifest 缺失**：当 execution manifest 文件不存在时，触发恢复策略：a) 调用 orchestrator 自动生成机制；b) 回退到规划阶段重新生成；c) 提示用户手动补充。
- **manifest 格式错误**：JSON 解析失败时，报告具体错误位置（行号、字段），建议修复方案。
- **版本不兼容**：manifest 版本高于预检脚本支持版本时，建议升级预检脚本或降级 manifest 版本。
- **资源不可用**：引用的资源不存在时，报告缺失资源路径，建议检查配置或提供替代资源。
- **步骤依赖循环**：检测到步骤依赖循环时，报告循环路径，建议重新设计步骤顺序。

## 质量检查

- **字段完整性**：所有必需字段必须存在，类型正确。
- **版本兼容性**：manifest 版本必须在预检脚本支持范围内。
- **路径有效性**：所有脚本路径、文件路径必须存在且可访问。
- **依赖无环**：步骤依赖关系必须为有向无环图（DAG）。
- **门控条件可验证**：success_gate 中的路径必须可检查（文件存在、内容匹配等）。

## 回退策略

- **自动恢复**：当 manifest 缺失时，调用 `orchestrator.generate_manifest()` 自动生成默认 manifest。
- **手动恢复**：提供 manifest 模板和填写指南，提示用户手动创建。
- **降级执行**：跳过预检，使用最小化配置执行工作流（仅适用于非关键任务）。
- **中止任务**：当恢复失败时，中止任务并生成详细错误报告。

## 资源召回建议

当以下场景发生时，应召回本卡片：
- 工作流预检失败，提示 manifest 缺失或无效。
- 需要设计或验证 execution manifest 的字段和格式。
- 需要实现 manifest 缺失时的自动恢复机制。
- 需要理解工作流预检的验证逻辑和错误处理。

配套资源：
- `onescience-orchestrator`：负责 manifest 生成和任务编排。
- `onescience-runtime`：执行预检和运行工作流。
- `onescience-installer`：环境准备和依赖检查。

## 补充证据（开源文档/用户自有，可选）

[D1] Deterministic Workflow Builder, GitHub 仓库, main 分支, URL: https://github.com/googlarz/deterministic-workflow-builder（accessed_at 2026-09-17，交叉验证：仓库展示了 manifest 的字段定义和验证逻辑）
[D2] workflow-verifier, GitHub 仓库, main 分支, URL: https://github.com/vlu532/workflow-verifier（accessed_at 2026-09-17，单源参考：描述了 manifest validation 的功能）

## 证据来源

[1] Deterministic Workflow Builder, GitHub 仓库, https://github.com/googlarz/deterministic-workflow-builder
[2] workflow-verifier, GitHub 仓库, https://github.com/vlu532/workflow-verifier