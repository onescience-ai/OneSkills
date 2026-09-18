# 数据集路径获取与验证工作流

## 适用范围

本卡面向所有需要从文件系统中获取和验证数据集路径的科学计算工作流，提供基于Python pathlib和os.path的标准化路径验证流程。适用于数据驱动的科学计算任务，包括但不限于CFD流场预测、气象预报、生物信息学分析等场景。当任务需要访问外部数据集时，应先使用本卡验证路径有效性，确保数据源可用且可访问。

## 输入

- 路径字符串（必填）：用户提供的数据集路径，支持本地路径、相对路径、绝对路径
- 路径类型（可选）：预期的路径类型（文件、目录、不存在）
- 跨平台标志（可选）：是否需要跨平台兼容性检查
- 严格模式标志（可选）：是否启用严格模式（路径不存在时抛出异常）

## 输出

- 验证结果：布尔值（True/False）表示路径是否有效
- 解析后的路径对象：Path对象或规范化后的字符串路径
- 错误信息：当验证失败时，返回具体的错误原因和建议修复措施
- 任务状态：`PATH_VALID`（路径有效）、`PATH_INVALID`（路径无效）、`PATH_NOT_FOUND`（路径不存在）

## 流程节点

1. **路径构造** → 将用户输入的路径字符串构造为Path对象或使用os.path构造路径
2. **路径规范化** → 使用resolve()或normpath()规范化路径，消除冗余分隔符和上级引用
3. **路径存在性检查** → 使用exists()方法检查路径是否存在
4. **路径类型验证** → 使用is_file()、is_dir()方法验证路径类型是否符合预期
5. **路径可访问性检查** → 验证当前进程是否有权限访问该路径
6. **跨平台兼容性处理** → 处理不同操作系统间的路径分隔符差异
7. **异常情况处置** → 处理路径不存在、权限不足、符号链接循环等异常情况

每步含：操作（具体验证逻辑）、参数（验证阈值）、工具（pathlib.Path、os.path）、质量门禁（所有验证通过才允许继续）

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 路径存在性检查 | 必须通过 | [D1] | 路径不存在时任务必须立即终止，不得尝试自动创建 |
| 路径类型匹配 | 必须匹配预期类型 | [D1] | 文件路径必须指向文件，目录路径必须指向目录 |
| 路径可访问性 | 必须可读 | [D1] | 路径存在但不可读（权限不足）同样阻断任务 |
| 跨平台兼容性 | 支持Windows/POSIX | [D1][D2] | 路径分隔符在不同平台上正确处理 |

### 校准数值（来自Python标准库，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| pathlib.Path.exists() | 布尔值 | [D1] | 检查路径是否存在，返回True/False |
| pathlib.Path.is_file() | 布尔值 | [D1] | 检查路径是否为文件，返回True/False |
| pathlib.Path.is_dir() | 布尔值 | [D1] | 检查路径是否为目录，返回True/False |
| os.path.exists() | 布尔值 | [D2] | 检查路径是否存在，返回True/False |
| os.path.isfile() | 布尔值 | [D2] | 检查路径是否为文件，返回True/False |
| os.path.isdir() | 布尔值 | [D2] | 检查路径是否为目录，返回True/False |

## 边界与分流

- **路径不存在**：直接返回 `PATH_NOT_FOUND`，错误信息包含实际尝试的路径和预期路径格式建议。不执行任何文件创建操作。
- **路径存在但类型不匹配**：返回 `PATH_INVALID`，错误信息列出预期类型与实际类型的差异。
- **路径存在但不可访问**：返回 `PATH_INVALID`，错误信息指向权限不足的具体原因。
- **路径存在但为符号链接**：根据strict模式决定是否解析符号链接，strict模式下符号链接循环会抛出异常。
- **跨平台路径不兼容**：返回 `PATH_INVALID`，错误信息提示路径分隔符差异。
- **路径字符串为空**：返回 `PATH_NOT_FOUND`，错误信息提示路径不能为空。
- **路径字符串格式错误**：返回 `PATH_INVALID`，错误信息提示正确的路径格式。

## 质量检查

- 所有路径验证必须在任务启动前完成，不得在业务逻辑执行中才检测
- 验证结果必须以结构化格式输出，便于下游系统解析和日志记录
- 错误信息必须包含：错误码（如 `PATH_NOT_FOUND`）、失败参数名、实际值（如有）、期望值描述
- 验证报告必须持久化保存，供后续审计和问题排查使用

## 回退策略

- 路径验证失败时，任务以 `PATH_INVALID` 状态终止，不执行任何后续步骤
- 若系统支持，可提供场景索引中可能配置的默认数据路径作为备选方案
- 若默认路径也不存在，终止并提示用户手动配置正确路径
- 不允许"跳过验证直接执行"的降级模式

## 资源召回建议

- 当任务编排器（onescience-orchestrator）准备调度任何需要外部数据输入的工作流前，应先召回本卡
- 配套资源：`cfd-data-input-contract-validation` 卡（提供数据契约验证框架）、`scientific-workflow-preflight-check` 卡（提供通用预检框架）
- 本卡适用于任何需要数据输入步骤的前置验证，也可作为独立验证技能被调用

## 补充证据（开源权威文档）

[D1] pathlib — Object-oriented filesystem paths, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/pathlib.html（accessed_at 2026-09-18，交叉验证：官方文档）
[D2] os.path — Common pathname manipulations, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/os.path.html（accessed_at 2026-09-18，交叉验证：官方文档）
[D3] PEP 428 – The pathlib module – object-oriented filesystem paths, Python Software Foundation, Final, URL: https://www.python.org/dev/peps/pep-0428/（accessed_at 2026-09-18，交叉验证：PEP文档）

## 证据来源

[1] pathlib — Object-oriented filesystem paths, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/pathlib.html
[2] os.path — Common pathname manipulations, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/os.path.html
[3] PEP 428 – The pathlib module – object-oriented filesystem paths, Python Software Foundation, Final, URL: https://www.python.org/dev/peps/pep-0428/