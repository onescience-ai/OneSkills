# CLI 工作流执行可靠性与结构化输出验证

## 适用范围

面向命令行接口驱动的科学计算工作流，提供非交互执行环境下的故障分类方法与结构化输出（JSON）交付契约验证框架。适用于需要将 CLI 工具集成到自动化流水线、持续集成/持续部署（CI/CD）管道、或分布式计算环境中的场景，覆盖气象数值预报后处理、生物信息学流水线、材料科学数据提取等需要可靠执行和可验证输出的科学工作流。

不适用于图形界面交互式工具的自动化（应先重构为 CLI 工具）、纯脚本语言无需编译的简单批处理、或不涉及结构化输出的纯流式数据处理。

## 输入

- CLI 工具的命令行参数规范（包括必需参数、可选参数、默认值）
- 工具的退出码约定文档
- 输出数据的 JSON Schema 定义（可选，用于验证契约）
- 测试数据集（用于烟雾测试）
- 工作流引擎或调度系统的执行环境信息

## 输出

- 结构化执行报告（JSON 格式），包含任务身份、执行状态、退出码、标准错误输出
- 故障分类诊断（连接失败、模式不匹配、执行错误、结果存储失败等）
- 验证通过/失败的判定报告，与 JSON Schema 的对比结果
- 可追溯的日志证据链

## 流程节点

### Step 1：CLI 接口规范化
- **操作**：确保所有配置选项可通过运行时参数覆盖，输入输出路径显式指定为参数
- **参数**：命令行参数格式=POSIX 风格，配置文件可选但可覆盖
- **工具**：argparse / click / typer 等 CLI 框架
- **质量门禁**：`--help` 输出完整，所有参数有文档说明

### Step 2：退出码与错误流约定
- **操作**：定义标准化退出码体系，将日志/错误信息输出到 STDERR，数据输出到 STDOUT
- **参数**：成功退出码=0，一般失败=1，保留退出码按 POSIX 规范使用
- **工具**：系统标准流（stdout/stderr）
- **质量门禁**：非零退出码对应可分类的错误类型

### Step 3：烟雾测试执行
- **操作**：在实际执行前运行最小化测试验证六个关键条件
- **参数**：测试数据=合成数据或脱敏样本，测试轮次=至少 1 轮
- **工具**：DEATHSTAR 框架或自定义烟雾测试套件
- **质量门禁**：六个条件（连接接口、模式匹配、历史结果加载、无错误执行、结果存储、结果聚合）全部通过

### Step 4：JSON 输出验证
- **操作**：对 CLI 工具的 JSON 输出执行 Schema 验证
- **参数**：Schema 版本=语义化版本号，验证器=jsonschema / ajv
- **工具**：JSON Schema 验证器
- **质量门禁**：输出可解析、必填字段完整、类型匹配、与任务身份一致

### Step 5：报告生成与归档
- **操作**：将执行结果、验证结果、诊断信息组装为结构化报告
- **参数**：报告格式=JSON，包含 task_id、task、summary、issues 字段
- **工具**：模板引擎或直接 JSON 构造
- **质量门禁**：报告通过 Schema 校验，task_id 与任务索引一致

## 关键参数

### 通用判据（方法层）

| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 退出码 0 | 表示执行成功 | [1] | POSIX 标准约定 |
| 退出码 1 | 表示一般性失败 | [1] | 最简单的失败标识 |
| STDERR | 用于日志和错误输出 | [1] | 不应与数据输出混合 |
| STDOUT | 仅用于数据输出 | [1] | 保持数据流纯净 |
| 运行时参数 | 所有配置可通过参数覆盖 | [1] | 避免硬编码依赖 |
| 烟雾测试条件数 | ≥6 项关键条件 | [2] | 覆盖执行全生命周期 |
| JSON Schema 必填字段 | task_id, task, summary, issues | 归因报告 | 报告契约核心字段 |

### 校准数值（来自特定体系，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 烟雾测试成功率 | 96.6%（29 名参与者中 28 个成功） | [2] | DEATHSTAR 用户研究结果 |
| SUS 可用性评分 | 88.3（"优秀"级别） | [2] | 系统可用性量表评分 |
| JSON 输出解析成功率 | ~99% | [3] | 当训练样本 >50 时 |
| 标注时间减少 | 57%（n=300 模型 vs n=1 模型） | [3] | 人机协同标注效率提升 |

## 边界与分流

**前提 1：CLI 工具支持非交互执行**
- 不成立时：工具依赖 GUI 或人工输入 → 重构为 CLI 模式（Rule 1），或将工作流拆分为两阶段，人工介入点在阶段间
- 参考：Brack et al. Rule 9 建议将 GUI 工具拆分为独立 CLI 工具 [1]

**前提 2：退出码体系已定义且一致**
- 不成立时：工具使用非标准退出码或不返回退出码 → 在调用层包装退出码映射，或要求工具维护者修正
- 参考：POSIX 保留退出码 126-125 范围有特殊含义 [1]

**前提 3：输出格式为可验证的结构化格式（JSON/XML）**
- 不成立时：输出为自由文本或二进制格式 → 增加格式转换层，或在输出前强制序列化为 JSON
- 参考：Dagdelen et al. 建议使用 JSON Schema 定义输出结构 [3]

**前提 4：测试数据可获取（合成或脱敏）**
- 不成立时：无任何测试数据可用 → 使用数据模式信息生成合成数据实例（DEATHSTAR 插件系统方法 [2]），或仅验证连接性和 Schema 兼容性

**前提 5：JSON Schema 契约已定义**
- 不成立时：无预定义 Schema → 从现有输出反向推导 Schema，或仅验证 JSON 可解析性和必填字段存在性

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|---------|
| 退出码分类覆盖 | 所有非零退出码有对应错误类别 | 补充退出码映射表 |
| STDERR/STDOUT 分离 | STDERR 无数据输出混入 | 重构输出流 |
| JSON Schema 验证 | 必填字段 100% 存在 | 标记报告为无效并记录缺失字段 |
| 烟雾测试通过率 | ≥90% 的测试用例通过 | 分析失败用例并修复 |
| 报告 task_id 一致性 | 报告 task_id == 任务索引 | 修正任务身份绑定逻辑 |
| 重复执行稳定性 | 连续 3 次执行结果一致 | 排查随机种子或状态残留问题 |

## 回退策略

1. **退出码不可用**：检查进程返回值（`$?`），或解析 STDERR 中的错误关键词
2. **JSON 解析失败**：尝试截断修复（补全缺失括号），或回退到文本正则提取
3. **Schema 验证失败**：记录所有验证错误，生成部分有效的报告并标注不完整原因
4. **烟雾测试环境不可用**：跳过烟雾测试，在实际执行后收集诊断信息

## 资源召回建议

当以下条件之一满足时应召回本卡片：
- 需要将 CLI 工具集成到自动化工作流中
- CLI 工具在非交互环境下执行失败需要诊断
- 需要验证 CLI 工具的 JSON 输出是否符合预定义契约
- 需要为科学计算工具设计退出码和错误处理规范
- 需要在分布式或 HPC 环境中运行 CLI 工具并收集诊断证据

配套资源：onescience-runtime（执行通道）、onescience-installer（环境预检）

## 证据来源

[1] Brack P, Crowther P, Soiland-Reyes S, et al. "Ten simple rules for making a software tool workflow-ready." PLoS Computational Biology, 2022, 18(3): e1009823. DOI: 10.1371/journal.pcbi.1009823

[2] Welten S, Weber S, Holt A, et al. "Will it run? - A proof of concept for smoke testing decentralized data analytics experiments." Frontiers in Medicine, 2023, 10: 1305415. DOI: 10.3389/fmed.2023.1305415

[3] Dagdelen J, Dunn A, Lee S, et al. "Structured information extraction from scientific text with large language models." Nature Communications, 2024, 15: 1418. DOI: 10.1038/s41467-024-45563-x

[4] Suetake H, Fukusato T, Igarashi T, et al. "A workflow reproducibility scale for automatic validation of biological interpretation results." GigaScience, 2022, 12: giad031. DOI: 10.1093/gigascience/giad031

[5] Sun S. "Testing JSON Schema Instruction Artifacts: Distributional Robustness under Validation-Equivalent Serialization and JSON Mode." Research Square Preprint, 2026. DOI: 10.21203/rs.3.rs-10610100/v1

[6] Demšar J, Kraljič A, Matkovič A, et al. "QuNex recipes: Executable, human-readable workflows for reproducible neuroimaging research." Imaging Neuroscience, 2026, 4: IMAG.a.1274. DOI: 10.1162/IMAG.a.1274

[D1] Python Software Foundation. "subprocess — Subprocess management." Python 3.14.7 documentation. URL: https://docs.python.org/3/library/subprocess.html (accessed_at: 2026-09-16, 官方权威文档)

[D2] JSON Schema. "JSON Schema reference." Understanding JSON Schema. URL: https://json-schema.org/understanding-json-schema/reference/ (accessed_at: 2026-09-16, 官方权威文档)

## 补充证据（权威文档）

[D1] Python subprocess模块文档提供了CLI执行的核心API规范：
- `subprocess.run()` 函数用于运行命令并等待完成
- `returncode` 属性返回子进程退出码，0表示成功，非零表示失败
- 负值 `-N` 表示子进程被信号N终止（仅POSIX）
- `CalledProcessError` 异常在非零退出码时抛出（当`check=True`）
- `TimeoutExpired` 异常在超时时抛出
- `stdout` 和 `stderr` 可分别捕获标准输出和标准错误

[D2] JSON Schema官方文档定义了结构化数据验证规范：
- `type` 关键字指定数据类型（array, boolean, null, numeric, object, string）
- `required` 关键字定义必需属性
- `properties` 关键字定义属性模式
- `additionalProperties` 控制额外属性
- `format` 关键字提供语义信息（date-time, email, uri等）
- 支持条件验证和模式组合
