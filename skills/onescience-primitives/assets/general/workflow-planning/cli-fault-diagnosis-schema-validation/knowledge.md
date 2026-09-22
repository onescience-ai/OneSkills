# CLI非交互执行故障诊断与JSON Schema报告校验

## 适用范围

本卡片适用于CLI工具在非交互式环境（自动化流水线、CI/CD、批处理任务）中的执行故障诊断，以及结构化报告（JSON格式）的Schema校验与契约一致性检查。覆盖命令参数解析、进程退出码判读、超时处理、输出捕获、JSON格式验证、Schema合规性检查等场景。不适用于交互式终端调试、Web服务API设计、或非JSON格式的报告校验。

## 输入

- **CLI命令与参数**：待执行的命令行指令及其参数序列
- **执行环境配置**：超时时间、工作目录、环境变量、stdin/stdout/stderr重定向策略
- **报告Schema定义**：JSON Schema文件或等效的字段约束规范
- **实际输出内容**：CLI执行后的stdout/stderr输出或JSON报告文件

## 输出

- **退出码分类结果**：成功(0)、应用错误(1-127)、信号终止(128+N)、超时异常
- **故障诊断报告**：错误类型、错误位置、根因分析、恢复建议
- **Schema校验报告**：通过/失败状态、违规字段列表、错误消息
- **结构化执行结果**：包含returncode、stdout、stderr的完整执行记录

## 流程节点

### 1. CLI进程启动与监控
- **操作**：使用subprocess.run()或Popen()启动子进程
- **参数**：args(命令序列)、timeout(秒)、capture_output(布尔)、check(布尔)
- **工具**：Python subprocess模块
- **质量门禁**：进程必须在指定timeout内完成，否则触发TimeoutExpired异常 [D1]

### 2. 退出码捕获与分类
- **操作**：读取CompletedProcess.returncode属性，按以下规则分类
- **分类规则**：
  - `returncode == 0`：执行成功
  - `0 < returncode < 128`：应用层错误（由程序自身定义）
  - `returncode < 0`：被信号N终止（POSIX系统，returncode = -N）
  - `returncode == 128+N`：shell模式下被信号N终止（如SIGKILL=137）[D1]
- **质量门禁**：必须区分正常退出、异常退出、信号终止三种情况

### 3. 输出捕获与解析
- **操作**：通过capture_output=True或stdout=PIPE, stderr=PIPE捕获输出
- **参数**：text=True以文本模式读取，encoding指定字符编码
- **工具**：CompletedProcess.stdout/stderr属性
- **质量门禁**：输出必须完整捕获，不得丢失错误信息 [D1]

### 4. JSON输出格式验证
- **操作**：使用json.loads()或json.tool验证输出是否为合法JSON
- **错误类型**：
  - JSONDecodeError：格式错误（缺少引号、括号不匹配、尾随逗号等）
  - ValueError：包含NaN/Infinity等非法数值（严格模式下）
- **质量门禁**：非JSON输出必须被识别并标记为格式违规 [D2]

### 5. JSON Schema合规性检查
- **操作**：使用jsonschema库验证JSON是否符合预定义Schema
- **检查项**：
  - 必填字段是否存在（required）
  - 字段类型是否正确（type）
  - 字段值是否在允许范围内（enum, minimum, maximum）
  - 数组约束是否满足（minItems, maxItems）
  - 字符串模式是否匹配（pattern）
- **质量门禁**：Schema校验必须返回结构化的错误列表 [D3]

### 6. 故障恢复与重试策略
- **操作**：根据故障类型选择恢复策略
- **策略映射**：
  - 退出码非零：检查命令参数、环境依赖、权限配置
  - 超时异常：增加timeout值或优化命令执行效率
  - JSON格式错误：检查输出重定向、编码设置、缓冲区大小
  - Schema违规：修正输出字段、补充必填项、调整数据类型
- **质量门禁**：恢复策略必须有明确的触发条件和预期效果

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 进程成功退出码 | 0 | [D1] | POSIX标准约定，表示正常执行完成 |
| 应用错误退出码范围 | 1-127 | [D1] | 程序自定义的错误码，128以上保留给信号 |
| 信号终止计算公式 | 128 + signal_number | [D1] | shell环境下被信号终止时的退出码 |
| 超时处理方式 | TimeoutExpired异常 | [D1] | 子进程超时后被kill，需重新communicate()获取输出 |
| JSON解码错误类型 | JSONDecodeError | [D2] | 包含msg, doc, pos, lineno, colno等诊断信息 |

### 校准数值（体系专属值）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Python subprocess默认超时 | None（无超时） | [D1] | 默认不设超时，需显式指定timeout参数 |
| JSON默认ensure_ascii | True | [D2] | 默认转义非ASCII字符，确保跨平台兼容 |
| JSON最大整数字符串长度 | 受解释器限制 | [D2] | Python 3.11+限制整数字符串长度防止DoS攻击 |

## 边界与分流

- **非POSIX系统（Windows）**：信号终止退出码不适用，需使用Windows特有错误码（如ERROR_SERVICE_SPECIFIC=1066）；kill()在Windows上等同于terminate()
- **shell=True模式**：退出码反映shell本身状态（如bash返回128+N），而非子进程状态；应优先使用shell=False避免歧义
- **二进制输出模式**：未设置text=True时，stdout/stderr为bytes类型，需注意编码转换；非文本内容（如图片）不应使用json.loads()解析
- **大文件输出**：communicate()将全部输出读入内存，超大输出可能导致内存溢出；应改用流式读取（Popen.stdout.readline()）
- **嵌套JSON Schema**：复杂Schema的校验错误可能包含嵌套路径（如"items[0].name"），需递归解析错误位置

## 质量检查

- **退出码完整性**：每次CLI执行必须捕获returncode，不得遗漏
- **输出捕获验证**：capture_output=True时，stdout和stderr都必须被检查
- **JSON格式预检**：在Schema校验前，必须先验证JSON格式合法性
- **Schema版本兼容**：校验时必须使用与Schema定义版本兼容的jsonschema库版本
- **错误消息可读性**：Schema校验错误必须包含字段路径和具体违规描述，不得仅返回"validation failed"

## 回退策略

- **subprocess模块不可用**：使用os.system()或os.popen()作为降级方案，但会丧失输出捕获和超时控制能力
- **jsonschema库不可用**：手动实现基本字段检查（类型、必填、范围），但无法处理复杂约束（pattern、oneOf等）
- **非交互环境限制**：若stdin不可用（如CI/CD），需确保CLI命令不依赖交互式输入；必要时使用--yes或--batch模式

## 资源召回建议

当遇到以下场景时应召回本卡片：
- CLI工具在自动化流水线中返回非零退出码
- 需要诊断子进程执行失败的原因（超时、信号终止、应用错误）
- 结构化报告（JSON）格式校验失败
- Schema定义与实际输出字段不匹配
- 需要设计CLI工具的错误码规范或报告契约

配套资源：
- onescience-runtime（运行执行技能）：处理具体的CLI任务执行和环境配置
- onescience-coder（编码技能）：实现CLI工具的错误处理和报告生成逻辑

## 补充证据（权威文档）

[D1] Python subprocess module documentation, Python Software Foundation, v3.14.7, https://docs.python.org/3/library/subprocess.html（accessed 2026-09-16，交叉验证：文档详细说明了exit code语义、TimeoutExpired异常处理、输出捕获机制）

[D2] Python json module documentation, Python Software Foundation, v3.14.7, https://docs.python.org/3/library/json.html（accessed 2026-09-16，交叉验证：文档定义了JSONDecodeError异常结构、格式校验规则、命令行验证工具）

[D3] JSON Schema reference, JSON Schema Organization, v2020-12, https://json-schema.org/understanding-json-schema/（accessed 2026-09-16，交叉验证：官方文档提供了完整的Schema关键字参考和校验规则说明）

## 证据来源

[D1] Python subprocess module documentation, Python Software Foundation, v3.14.7, https://docs.python.org/3/library/subprocess.html
[D2] Python json module documentation, Python Software Foundation, v3.14.7, https://docs.python.org/3/library/json.html
[D3] JSON Schema reference, JSON Schema Organization, v2020-12, https://json-schema.org/understanding-json-schema/

## 批次补充（2026-09-16：归因分析CLI故障案例）

### 实际应用案例

基于归因分析任务（任务ID：396，钙钛矿封装层降解抑制机器学习筛选）的故障案例：

#### CLI执行故障案例
- **故障现象**：归因分析智能体退出码为1，报告校验错误
- **错误详情**：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']；包含额外顶层字段 ['error', 'sessionID', 'timestamp', 'type']
- **根因分析**：CLI未正常退出或未产生有效响应，导致工作流逐步对照、领域知识缺口判断和下游优化建议均不可置信
- **恢复策略**：依据故障类别修正启动配置或恢复策略，确保归因分析进程稳定完成并保留诊断证据

#### JSON Schema报告交付契约案例
- **契约要求**：report.json必须包含必填字段 ['issues', 'summary', 'task', 'task_id']，且task_id与任务索引一致，task与任务name一致
- **验证失败**：最终响应缺失、无法解析或字段校验失败
- **修复方法**：在输出前按契约校验报告，使用report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 归因分析CLI退出码 | 1 | 任务396案例 | 应用层错误，表示执行失败 |
| 必填字段数量 | 4 | 任务396案例 | issues, summary, task, task_id |
| 额外字段数量 | 4 | 任务396案例 | error, sessionID, timestamp, type |
| 任务身份验证点 | 2 | 任务396案例 | task_id与索引一致，task与name一致 |

## 批次补充（2026-09-17：基于论文证据的CLI最佳实践与Schema执行）

### 论文证据补充

从最新检索的论文中抽取以下知识，丰富CLI故障诊断与Schema验证体系：

**[1] Bionitio: demonstrating and facilitating best practices for bioinformatics command-line software (PMID: 31544213)**

| 概念 | 描述 | 来源 | 说明 |
|------|------|------|------|
| 命令行最佳实践 | 自动化启动新项目，遵循推荐的最佳实践 | [1] | 包括命令行参数解析、错误处理、进度日志、退出状态值定义 |
| 退出状态值定义 | 定义明确的退出状态值，用于指示执行结果 | [1] | 关键特征包括命令行参数解析、错误处理、进度日志、退出状态值定义 |
| 项目模板 | 提供工作示例和模板，用于构建新工具 | [1] | 包括命令行参数解析、错误处理、进度日志、退出状态值定义、测试套件 |
| 跨平台支持 | 支持多种编程语言和操作系统 | [1] | 12种编程语言，跨平台操作 |

**[2] Schema Enforcement and Structured-Output Stability in Locally Deployed LLMs for Clinical Admission-Note Editing (PMID: 42512666)**

| 概念 | 描述 | 来源 | 说明 |
|------|------|------|------|
| 模式执行 | 强制LLM输出符合预定义Schema的结构化数据 | [2] | 所有模型在模式执行下产生70/70首次通过有效的输出 |
| 结构化输出稳定性 | 评估LLM输出的JSON/schema有效性、运行间稳定性 | [2] | 自动化代理指标评估JSON/schema有效性、运行间稳定性、指令遵循、冗长度 |
| 代理指标 | 使用代理指标评估输出质量 | [2] | 评估JSON/schema有效性、运行间稳定性、指令遵循、冗长度、数字令牌保留、不确定性标记变化 |
| 模型特定行为 | 不同模型在文档行为上存在差异 | [2] | 包括冗长度和数字令牌保留的差异 |

### 补充边界与分流

- **CLI最佳实践实施**：当设计新的CLI工具时，应遵循命令行最佳实践，包括退出状态值定义、错误处理、进度日志等[1]
- **Schema执行验证**：当使用LLM生成结构化输出时，应实施Schema执行，确保输出符合预定义Schema[2]
- **运行间稳定性评估**：评估LLM输出的运行间稳定性，使用代理指标评估JSON/schema有效性、运行间稳定性、指令遵循等[2]
- **模型特定行为处理**：注意不同模型在文档行为上的差异，包括冗长度和数字令牌保留的差异[2]

### 补充质量检查

- 验证CLI工具是否遵循命令行最佳实践，包括退出状态值定义、错误处理、进度日志等
- 检查Schema执行是否强制LLM输出符合预定义Schema
- 验证结构化输出的运行间稳定性，使用代理指标评估JSON/schema有效性
- 确保不同模型在文档行为上的差异得到适当处理

### 补充回退策略

- **CLI最佳实践未遵循**：当CLI工具未遵循最佳实践时，应逐步实施退出状态值定义、错误处理、进度日志等
- **Schema执行失败**：当Schema执行失败时，应检查Schema定义是否正确，或使用更简单的Schema
- **运行间稳定性差**：当运行间稳定性差时，应调整模型参数或使用更稳定的模型
- **模型特定行为问题**：当模型特定行为导致问题时，应针对特定模型进行调整或使用替代模型

## 批次补充（2026-09-17：任务334案例补充）

### 实际应用案例

基于归因分析任务（任务ID：334，MOF合成应用多模态机器学习关联）的故障案例：

#### CLI执行故障案例
- **故障现象**：归因分析智能体退出码为1，报告校验错误
- **错误详情**：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']；包含额外顶层字段 ['error', 'sessionID', 'timestamp', 'type']
- **根因分析**：CLI启动、超时或结构化输出契约失败，导致工作流逐步对照、领域知识缺口判断和下游优化建议均不可置信
- **恢复策略**：依据故障类别修正启动配置或恢复策略，确保归因分析进程稳定完成并保留诊断证据

#### JSON Schema报告交付契约案例
- **契约要求**：report.json必须包含必填字段 ['issues', 'summary', 'task', 'task_id']，且task_id与任务索引一致，task与任务name一致
- **验证失败**：最终响应缺失、无法解析或字段校验失败
- **修复方法**：在输出前按契约校验报告，使用report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 归因分析CLI退出码 | 1 | 任务334案例 | 应用层错误，表示执行失败 |
| 必填字段数量 | 4 | 任务334案例 | issues, summary, task, task_id |
| 额外字段数量 | 4 | 任务334案例 | error, sessionID, timestamp, type |
| 任务身份验证点 | 2 | 任务334案例 | task_id与索引一致，task与name一致 |

## 批次补充（2026-09-17：任务342案例补充）

### 实际应用案例

基于归因分析任务（任务ID：342，MXeneKevlar复合膜渗透压发电设计）的故障案例：

#### CLI执行故障案例
- **故障现象**：归因分析智能体退出码为1，报告校验错误
- **错误详情**：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']；包含额外顶层字段 ['error', 'sessionID', 'timestamp', 'type']
- **根因分析**：CLI启动、超时或结构化输出契约失败，导致工作流逐步对照、领域知识缺口判断和下游优化建议均不可置信
- **恢复策略**：依据故障类别修正启动配置或恢复策略，确保归因分析进程稳定完成并保留诊断证据

#### JSON Schema报告交付契约案例
- **契约要求**：report.json必须包含必填字段 ['issues', 'summary', 'task', 'task_id']，且task_id与任务索引一致，task与任务name一致
- **验证失败**：最终响应缺失、无法解析或字段校验失败
- **修复方法**：在输出前按契约校验报告，使用report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（案例专属值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 归因分析CLI退出码 | 1 | 任务342案例 | 应用层错误，表示执行失败 |
| 必填字段数量 | 4 | 任务342案例 | issues, summary, task, task_id |
| 额外字段数量 | 4 | 任务342案例 | error, sessionID, timestamp, type |
| 任务身份验证点 | 2 | 任务342案例 | task_id与索引一致，task与name一致 |

## 批次补充（2026-09-17：基于任务269归因报告的知识补充）

### 任务背景

基于归因分析任务（任务ID：269，天气驱动次日大面积野火危险概率预报）的优化计划补充知识。

### CLI执行故障案例

- **故障现象**：归因分析智能体退出码为1，报告校验错误
- **错误详情**：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']；包含额外顶层字段 ['error', 'sessionID', 'timestamp', 'type']
- **根因分析**：CLI启动、超时或结构化输出契约失败，导致工作流逐步对照、领域知识缺口判断和下游优化建议均不可置信
- **恢复策略**：依据故障类别修正启动配置或恢复策略，确保归因分析进程稳定完成并保留诊断证据

### JSON Schema报告交付契约案例

- **契约要求**：report.json必须包含必填字段 ['issues', 'summary', 'task', 'task_id']，且task_id与任务索引一致，task与任务name一致
- **验证失败**：最终响应缺失、无法解析或字段校验失败
- **修复方法**：在输出前按契约校验报告，使用report-schema.json校验最终输出并执行错配字段反例测试

### 补充通用判据（CLI参数构建与信号处理）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码126 | 命令不可执行 | [D1] | 命令存在但无执行权限 |
| 退出码127 | 命令未找到 | [D1] | 命令不存在或PATH错误 |
| SIGTERM信号编号 | 15 | [D1] | 默认终止信号 |
| SIGKILL信号编号 | 9 | [D1] | 强制终止信号（无法捕获） |

### 补充边界与分流

- **命令不存在或不可执行**：使用shutil.which()查找程序路径，检查文件权限（os.access），验证PATH环境变量
- **输出编码不匹配**：尝试多种编码（UTF-8, GBK, Latin-1），使用errors='replace'或'ignore'，记录编码警告但继续处理

### 校准数值（任务269案例专属值）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 归因分析CLI退出码 | 1 | 任务269案例 | 应用层错误，表示执行失败 |
| 必填字段数量 | 4 | 任务269案例 | issues, summary, task, task_id |
| 额外字段数量 | 4 | 任务269案例 | error, sessionID, timestamp, type |
| 任务身份验证点 | 2 | 任务269案例 | task_id与索引一致，task与name一致 |

## 批次补充（2026-09-17：任务237归因分析报告案例）

### 任务背景

基于归因分析任务（任务ID：237，北海区风暴潮临近预报模型）的优化计划补充知识。

### CLI执行故障案例

- **故障现象**：归因分析智能体退出码为1，报告校验错误
- **错误详情**：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']；包含额外顶层字段 ['error', 'sessionID', 'timestamp', 'type']
- **根因分析**：CLI启动、超时或结构化输出契约失败，导致工作流逐步对照、领域知识缺口判断和下游优化建议均不可置信
- **恢复策略**：依据故障类别修正启动配置或恢复策略，确保归因分析进程稳定完成并保留诊断证据

### JSON Schema报告交付契约案例

- **契约要求**：report.json必须包含必填字段 ['issues', 'summary', 'task', 'task_id']，且task_id与任务索引一致，task与任务name一致
- **验证失败**：最终响应缺失、无法解析或字段校验失败
- **修复方法**：在输出前按契约校验报告，使用report-schema.json校验最终输出并执行错配字段反例测试

### 任务身份校验失败案例

- **失败现象**：task_id与任务索引不一致，task与任务name不一致
- **错误详情**：
  - task_id字段值与实际任务索引不匹配
  - task字段值与实际任务名称不匹配
  - summary字段不是非空字符串
  - issues字段不是数组类型
- **修复方法**：确保report.json中的task_id与任务索引一致，task与任务name一致，summary为非空字符串，issues为数组类型

### 校准数值（任务237案例专属值）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 归因分析CLI退出码 | 1 | 任务237案例 | 应用层错误，表示执行失败 |
| 必填字段数量 | 4 | 任务237案例 | issues, summary, task, task_id |
| 额外字段数量 | 4 | 任务237案例 | error, sessionID, timestamp, type |
| 任务身份验证点 | 2 | 任务237案例 | task_id与索引一致，task与name一致 |
| summary字段约束 | 非空字符串 | 任务237案例 | summary必须是非空字符串 |
| issues字段约束 | 数组类型 | 任务237案例 | issues必须是数组 |

## 批次补充（2026-09-17：任务86归因分析报告案例）

### 任务背景

基于归因分析任务（任务ID：86，藏红花酸通路酶骨架序列设计与折叠筛选）的优化计划补充知识。

### CLI执行故障案例

- **故障现象**：归因分析智能体退出码为1，报告校验错误
- **错误详情**：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']；包含额外顶层字段 ['error', 'sessionID', 'timestamp', 'type']；task_id 与任务索引不一致；task 与任务 name 不一致
- **根因分析**：CLI启动、超时或结构化输出契约失败，导致工作流逐步对照、领域知识缺口判断和下游优化建议均不可置信
- **恢复策略**：依据故障类别修正启动配置或恢复策略，确保归因分析进程稳定完成并保留诊断证据

### JSON Schema报告交付契约案例

- **契约要求**：report.json必须包含必填字段 ['issues', 'summary', 'task', 'task_id']，且task_id与任务索引一致，task与任务name一致，summary必须是非空字符串，issues必须是数组
- **验证失败**：最终响应缺失、无法解析或字段校验失败
- **修复方法**：在输出前按契约校验报告，使用report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（任务86案例专属值）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 归因分析CLI退出码 | 1 | 任务86案例 | 应用层错误，表示执行失败 |
| 必填字段数量 | 4 | 任务86案例 | issues, summary, task, task_id |
| 额外字段数量 | 4 | 任务86案例 | error, sessionID, timestamp, type |
| 任务身份验证点 | 2 | 任务86案例 | task_id与索引一致，task与name一致 |
| summary字段约束 | 非空字符串 | 任务86案例 | summary必须是非空字符串 |
| issues字段约束 | 数组类型 | 任务86案例 | issues必须是数组 |

## 批次补充（2026-09-18：任务347归因分析报告案例）

### 任务背景

基于归因分析任务（任务ID：347，PdCeO2单原子催化剂CO氧化动态分析）的优化计划补充知识。

### CLI执行故障案例

- **故障现象**：归因分析智能体退出码为1，报告校验错误
- **错误详情**：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']；包含额外顶层字段 ['error', 'sessionID', 'timestamp', 'type']；task_id与任务索引不一致；task与任务name不一致
- **根因分析**：CLI启动、超时或结构化输出契约失败，导致工作流逐步对照、领域知识缺口判断和下游优化建议均不可置信
- **恢复策略**：依据故障类别修正启动配置或恢复策略，确保归因分析进程稳定完成并保留诊断证据

### JSON Schema报告交付契约案例

- **契约要求**：report.json必须包含必填字段 ['issues', 'summary', 'task', 'task_id']，且task_id与任务索引一致，task与任务name一致，summary必须是非空字符串，issues必须是数组
- **验证失败**：最终响应缺失、无法解析或字段校验失败
- **修复方法**：在输出前按契约校验报告，使用report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（任务347案例专属值）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 归因分析CLI退出码 | 1 | 任务347案例 | 应用层错误，表示执行失败 |
| 必填字段数量 | 4 | 任务347案例 | issues, summary, task, task_id |
| 额外字段数量 | 4 | 任务347案例 | error, sessionID, timestamp, type |
| 任务身份验证点 | 2 | 任务347案例 | task_id与索引一致，task与name一致 |
| summary字段约束 | 非空字符串 | 任务347案例 | summary必须是非空字符串 |
| issues字段约束 | 数组类型 | 任务347案例 | issues必须是数组 |

## 批次补充（2026-09-21：任务302归因分析报告案例）

### 任务背景

基于归因分析任务（任务ID：302，臭氧与颗粒物历史序列的气象归一化和趋势归因）的优化计划补充知识。

### CLI执行故障案例

- **故障现象**：归因分析智能体退出码为1，报告校验错误
- **错误详情**：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']；包含额外顶层字段 ['error', 'sessionID', 'timestamp', 'type']；task_id与任务索引不一致；task与任务name不一致
- **根因分析**：CLI启动、超时或结构化输出契约失败，导致工作流逐步对照、领域知识缺口判断和下游优化建议均不可置信
- **恢复策略**：依据故障类别修正启动配置或恢复策略，确保归因分析进程稳定完成并保留诊断证据

### JSON Schema报告交付契约案例

- **契约要求**：report.json必须包含必填字段 ['issues', 'summary', 'task', 'task_id']，且task_id与任务索引一致，task与任务name一致，summary必须是非空字符串，issues必须是数组
- **验证失败**：最终响应缺失、无法解析或字段校验失败
- **修复方法**：在输出前按契约校验报告，使用report-schema.json校验最终输出并执行错配字段反例测试

### 校准数值（任务302案例专属值）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 归因分析CLI退出码 | 1 | 任务302案例 | 应用层错误，表示执行失败 |
| 必填字段数量 | 4 | 任务302案例 | issues, summary, task, task_id |
| 额外字段数量 | 4 | 任务302案例 | error, sessionID, timestamp, type |
| 任务身份验证点 | 2 | 任务302案例 | task_id与索引一致，task与name一致 |
| summary字段约束 | 非空字符串 | 任务302案例 | summary必须是非空字符串 |
| issues字段约束 | 数组类型 | 任务302案例 | issues必须是数组 |
