# CLI非交互执行与故障分类

## 适用范围
面向命令行工具的非交互执行场景，提供故障分类、退出码解读和错误处理的最佳实践。适用于自动化脚本、CI/CD流水线、远程执行环境、批处理作业和无人值守任务。不适用于交互式终端会话或需要用户输入的场景。

## 输入
- 命令行工具或脚本的执行请求
- 执行环境配置（本地、远程、容器化）
- 输入参数和选项
- 环境变量和依赖项

## 输出
- 进程执行结果（成功/失败状态）
- 标准输出和标准错误流
- 退出码和错误信息
- 执行日志和诊断信息

## 流程节点
1. **命令解析** → 2. **环境准备** → 3. **进程创建** → 4. **输入重定向** → 5. **输出捕获** → 6. **超时监控** → 7. **退出码处理** → 8. **错误分类** → 9. **恢复策略**

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码0 | 成功 | [D2][D3] | 命令执行成功，无错误 |
| 退出码1-2 | 一般错误 | [D2] | 通用错误捕获，具体含义由命令定义 |
| 退出码2 | Shell内置命令误用 | [D3] | 根据Bash文档，内置命令使用不当 |
| 退出码126 | 命令不可执行 | [D2][D3] | 权限问题或非可执行文件 |
| 退出码127 | 命令未找到 | [D2][D3] | 命令不存在或PATH配置错误 |
| 退出码128+n | 信号终止 | [D2][D3] | 进程被信号n终止，n为信号编号 |
| 退出码130 | Ctrl+C终止 | [D2][D3] | 进程被控制中断信号终止（128+2） |
| 退出码137 | SIGKILL终止 | [D3] | 进程被SIGKILL信号终止（128+9） |
| 退出码255 | 范围外 | [D2] | 退出码超出0-255有效范围 |
| 退出码64-113 | 用户自定义范围 | [D2] | 建议用户自定义退出码使用此范围 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| subprocess.run超时 | 30秒 | [D1] | Python subprocess默认超时设置 |
| 进程组创建 | 创建新进程组 | [D1] | Windows使用CREATE_NEW_PROCESS_GROUP |
| 输出缓冲 | 系统默认 | [D1] | 使用io.DEFAULT_BUFFER_SIZE |
| 管道缓冲 | 无缓冲 | [D1] | bufsize=0表示无缓冲读写 |

## 认证与沙箱配置

### 进程隔离参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| user | None 或 UID | [D1] | POSIX系统下设置子进程用户身份（setreuid） |
| group | None 或 GID | [D1] | POSIX系统下设置子进程组身份（setregid） |
| extra_groups | None 或 GID列表 | [D1] | 补充组身份（setgroups），用于权限控制 |
| umask | -1 或 0-0o777 | [D1] | 子进程文件创建掩码 |
| start_new_session | True/False | [D1] | 创建新会话（setsid），隔离信号和终端 |
| process_group | 0 或 PGID | [D1] | 创建新进程组（setpgid），隔离作业控制 |
| creationflags | Windows标志 | [D1] | Windows下CREATE_NEW_PROCESS_GROUP等隔离标志 |

### 安全边界
- **shell=True风险**：shell元字符可能被注入，需使用shlex.quote()转义
- **env参数**：显式传递环境变量可防止敏感信息泄漏
- **close_fds**：默认True，关闭非标准文件描述符防止泄漏
- **pass_fds**：显式传递需要保留的文件描述符，其余自动关闭

## 边界与分流
- **命令不存在**（退出码127）：检查PATH环境变量，验证命令是否已安装
- **权限不足**（退出码126）：使用sudo或修改文件权限（chmod +x）
- **超时处理**：设置合理超时时间，捕获TimeoutExpired异常
- **输出死锁**：使用communicate()而非直接读写管道，避免缓冲区满
- **资源泄漏**：使用上下文管理器（with语句）确保进程资源释放
- **信号处理**：正确处理SIGTERM、SIGKILL等信号，避免僵尸进程
- **退出码超出范围**（退出码>255）：检查退出码计算逻辑，避免模256截断
- **Shell内置命令错误**（退出码2）：检查内置命令语法和参数
- **沙箱隔离不足**：使用start_new_session或process_group隔离进程
- **认证失败**：检查user/group参数和系统权限配置

## 质量检查
- 验证退出码在预期范围内（0-255）
- 检查标准错误是否有异常输出
- 验证进程是否正常终止（无僵尸进程）
- 检查超时设置是否合理
- 验证输出捕获是否完整

## 回退策略
- **命令执行失败**：尝试替代命令或不同参数组合
- **权限问题**：请求管理员权限或修改执行环境
- **超时问题**：增加超时时间或优化命令性能
- **依赖缺失**：安装必要依赖或使用容器化环境
- **资源限制**：清理系统资源或增加系统限制

## 资源召回建议
- 当需要执行CLI工具时召回本卡片
- 配套资源：general-json-schema-report-contract（JSON Schema报告验证）
- 适用场景：自动化测试、CI/CD流水线、远程执行、批处理任务

## 补充证据（开源文档/用户自有）
[D1] subprocess — Subprocess management — Python 3.14.7 documentation, Python Software Foundation, 3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed_at，权威文档）
[D2] Exit Codes With Special Meanings, The Linux Documentation Project, Advanced Bash-Scripting Guide Appendix E, URL: https://tldp.org/LDP/abs/html/exitcodes.html（accessed_at，权威文档）
[D3] Exit Status (Bash Reference Manual), GNU, version 5.2, URL: https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html（accessed_at，权威文档）

## 批次补充（2026-09-16-harvest-task29）

### 归因分析CLI故障模式与诊断

**失败现象**：归因分析CLI退出码为1，未产生有效的结构化报告，错误日志显示"缺少顶层字段"和"包含额外顶层字段"。

**故障分类**：
- 退出码1属于"一般错误"类别，具体含义由应用程序定义
- 错误类型：结构化输出契约失败（缺少必需字段、包含未定义字段）
- 失败阶段：CLI生命周期完成但输出不符合Schema校验

**诊断要点**：
1. **退出码1的常见原因**：
   - 参数错误或缺失
   - 依赖缺失或版本不兼容
   - 内部异常或未处理错误
   - 输出格式不符合契约

2. **结构化输出故障特征**：
   - 缺少顶层字段（如issues、summary、task、task_id）
   - 包含额外顶层字段（如error、sessionID、timestamp、type）
   - 字段类型不匹配（如issues必须是数组，summary必须是非空字符串）
   - 任务身份不一致（task_id与任务索引不匹配，task与任务name不匹配）

**修复路径**：
1. **检查输出契约**：验证CLI输出是否符合预期的JSON Schema
2. **验证字段完整性**：确保所有必需字段存在且类型正确
3. **检查任务身份**：确认task_id和task字段与任务索引一致
4. **分析错误日志**：结合stderr和结构化错误信息定位问题
5. **实施Schema校验**：在输出前使用JSON Schema验证器检查报告格式

**预防措施**：
- 实现输出前的Schema校验
- 使用类型注解和验证确保输出结构正确
- 提供详细的错误信息帮助诊断
- 实现优雅的失败处理机制

**与任务29的具体关联**：
- 归因分析CLI退出码1，错误日志显示结构化输出契约失败
- 缺少必需字段：issues、summary、task、task_id
- 包含未定义字段：error、sessionID、timestamp、type
- 任务身份不一致：task_id与任务索引不匹配，task与任务name不匹配
- 这表明CLI执行成功但输出格式不符合Schema校验要求

## 批次补充（2026-09-16-modify-3）

### 实际失败案例：归因分析CLI退出码1

**失败现象**：归因分析CLI进程退出码为1，未产生有效的结构化报告。

**诊断要点**：
- 退出码1属于"一般错误"类别（[D2][D3]），具体含义由应用程序定义
- 需结合stderr输出判断具体失败原因（参数错误、依赖缺失、内部异常等）
- 当CLI输出为空或不完整时，退出码1通常指示启动阶段失败

**修复路径**：
1. 检查stderr日志获取详细错误信息
2. 验证CLI启动参数和环境配置
3. 检查依赖项和系统资源
4. 使用try-except捕获subprocess.CalledProcessError获取详细信息

## 批次补充（2026-09-16-harvest-task344）

### 科学计算流水线的CLI执行模式

**来源**：Compi框架论文 [P1]，该框架为生物信息学和数据科学提供基于XML定义的流水线CLI自动生成。

**关键发现**：
- **自动CLI生成**：从流水线参数规格自动生成完整的命令行接口，包含参数名、描述和类型，遵循标准CLI约定 [P1]
- **细粒度执行控制**：支持`--from`/`--after`/`--until`/`--before`/`--single-task`修饰符精确控制子流水线执行范围，以及`resume`命令从失败点恢复 [P1]
- **并行任务调度**：通过可配置大小的worker线程池实现多任务并行，`--num-tasks`参数控制最大并行数 [P1]
- **任务级日志分离**：每个任务的标准输出(stdout)、标准错误(stderr)和参数值分别存储为`task-name.out.log`、`task-name.err.log`和`task-name.params`，通过`--logs`选项启用 [P1]
- **警告中止机制**：`--abort-if-warnings`选项在流水线验证发现警告时中止执行，适用于开发阶段的测试 [P1]
- **任务解释器与运行器**：任务解释器允许使用非Bash语言定义任务代码；任务运行器（如Slurm/SGE提交脚本）可在不修改流水线定义的情况下适配不同计算环境 [P1]
- **动态调度**：通过`if`属性在任务运行前执行命令实现动态跳过，通过foreach循环的命令输出实现动态迭代次数 [P1]

**对故障分类的补充**：
- 流水线级别的故障诊断需结合任务级日志（.err.log）和退出码
- 从失败点恢复（resume）是科学流水线的关键容错策略
- 任务运行器失败（如HPC提交失败）会产生不同于本地执行的错误模式

## 批次补充（2026-09-16-harvest-task361）

### LLM代理CLI故障分类研究

**来源**：LLM代理故障分类论文 [P2]，该研究对Codex、Gemini-CLI、LangChain和CrewAI的255个bug报告进行了分析。

**关键发现**：
- **双轴分类法**：构建了覆盖可观测症状和触发LLM行为的双轴分类法(taxonomy)，适用于CLI接口上的故障分类 [P2]
- **静默错误检测**：许多代理响应性(AR)bug以静默错误形式出现，缺乏明确的测试预言(test oracle)，使故障检测困难 [P2]
- **随机性复杂化**：LLM响应的随机性进一步复杂化了故障再现，增加了诊断难度 [P2]
- **故障模式**：研究识别了CLI接口上的多种故障模式，包括参数错误、依赖缺失、输出格式不符合契约等 [P2]

**对故障分类的补充**：
- LLM代理的CLI故障分类需要考虑响应随机性带来的诊断挑战
- 静默错误检测需要更精细的测试预言和监控机制
- 双轴分类法提供了更系统的故障分析框架

## 证据来源
[P1] "Command-line interface for the RNA-Seq Compi pipeline", Nogueira-Rodríguez et al., PeerJ Computer Science, 2021, DOI: 10.7717/peerj-cs.593
[P2] "Understanding Agent-Reactive Bugs at the Model-Harness Boundary: An Empirical Study of LLM Agent Issue Reports", Chen et al., arXiv, 2026, DOI: 10.48550/arXiv.2607.15684
[D1] subprocess — Subprocess management — Python 3.14.7 documentation, Python Software Foundation, 2026
[D2] Exit Codes With Special Meanings, The Linux Documentation Project, 2026
[D3] Exit Status (Bash Reference Manual), GNU, 2026

## 批次补充（2026-09-16-harvest-task49）

### 多模态推理增强遗传扰动虚拟细胞预测任务的CLI执行故障

**失败现象**：归因分析CLI退出码为1，未产生有效的结构化报告。报告校验错误显示：缺少顶层字段 `['issues', 'summary', 'task', 'task_id']`；包含额外顶层字段 `['error', 'sessionID', 'timestamp', 'type']`；task_id与任务索引不一致；task与任务name不一致。

**故障分类**：
- 退出码1属于"一般错误"类别（[D2][D3]），具体含义由应用程序定义
- 错误类型：结构化输出契约失败（缺少必需字段、包含未定义字段、任务身份不一致）
- 失败阶段：CLI生命周期完成但输出不符合Schema校验

**诊断要点**：
1. **退出码1的结构化输出故障特征**：
   - 缺少顶层必需字段（issues、summary、task、task_id）
   - 包含未在Schema中定义的额外字段（error、sessionID、timestamp、type）
   - 字段类型不匹配（issues必须是数组，summary必须是非空字符串）
   - 任务身份不一致（task_id与任务索引不匹配，task与任务name不匹配）

2. **与前次失败（Task 29）的对比**：
   - Task 29同样出现退出码1和结构化输出契约失败
   - Task 49的额外特征：包含额外顶层字段（error、sessionID、timestamp、type）
   - 共同根因：CLI执行成功但输出格式不符合Schema校验要求

**修复路径**：
1. **输出前Schema校验**：在CLI输出报告前，使用JSON Schema验证器检查报告格式
2. **字段完整性检查**：确保所有必需字段（issues、summary、task、task_id）存在且类型正确
3. **附加字段控制**：使用`additionalProperties: false`严格模式，禁止未定义字段
4. **任务身份校验**：在输出前确认task_id与任务索引一致、task与任务name一致
5. **错误日志分析**：结合stderr和结构化错误信息定位具体失败原因

**预防措施**：
- 实现CLI输出前的Schema校验流程
- 使用类型注解和验证确保输出结构正确
- 提供详细的错误信息帮助诊断
- 实现优雅的失败处理机制
- 在CLI启动前验证任务身份信息的一致性

## 批次补充（2026-09-17-harvest-task291）

### 渤黄海海浪智能订正模型归因分析CLI故障

**失败现象**：归因分析CLI退出码为1，未产生有效的结构化报告。

**错误详情**：
- 校验错误：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']
- 额外字段：包含 ['error', 'sessionID', 'timestamp', 'type']
- 任务身份不一致：task_id 与任务索引不一致、task 与任务 name 不一致
- 字段约束违反：summary 必须是非空字符串；issues 必须是数组

**故障分类**：
- 退出码1属于"一般错误"类别（[D2][D3]），具体含义由应用程序定义
- 错误类型：结构化输出契约失败（缺少必需字段、包含未定义字段、任务身份不一致）
- 失败阶段：CLI生命周期完成但输出不符合Schema校验

**诊断要点**：
1. **退出码1的结构化输出故障特征**：
   - 缺少顶层必需字段（issues、summary、task、task_id）
   - 包含未在Schema中定义的额外字段（error、sessionID、timestamp、type）
   - 字段类型不匹配（issues必须是数组，summary必须是非空字符串）
   - 任务身份不一致（task_id与任务索引不匹配，task与任务name不匹配）

2. **与前次失败案例的对比**：
   - Task 29、Task 49、Task 81同样出现退出码1和结构化输出契约失败
   - Task 291的特征与Task 81相似：缺少必需字段、包含额外字段、任务身份不一致
   - 共同根因：CLI执行成功但输出格式不符合Schema校验要求

**修复路径**：
1. **输出前Schema校验**：在CLI输出报告前，使用JSON Schema验证器检查报告格式
2. **字段完整性检查**：确保所有必需字段（issues、summary、task、task_id）存在且类型正确
3. **附加字段控制**：使用`additionalProperties: false`严格模式，禁止未定义字段
4. **任务身份校验**：在输出前确认task_id与任务索引一致、task与任务name一致
5. **错误日志分析**：结合stderr和结构化错误信息定位具体失败原因

**预防措施**：
- 实现CLI输出前的Schema校验流程
- 使用类型注解和验证确保输出结构正确
- 提供详细的错误信息帮助诊断
- 实现优雅的失败处理机制
- 在CLI启动前验证任务身份信息的一致性

**与任务291的具体关联**：
- 归因分析CLI退出码1，错误日志显示结构化输出契约失败
- 缺少必需字段：issues、summary、task、task_id
- 包含未定义字段：error、sessionID、timestamp、type
- 任务身份不一致：task_id与任务索引不匹配，task与任务name不匹配
- 这表明CLI执行成功但输出格式不符合Schema校验要求

## 批次补充（2026-09-17-harvest-task412）

### 高居里温度二维铁磁材料高通量筛选归因分析CLI故障

**失败现象**：归因分析CLI退出码为1，未产生有效的结构化报告。

**错误详情**：
- 校验错误：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']
- 额外字段：包含 ['error', 'sessionID', 'timestamp', 'type']
- 任务身份不一致：task_id 与任务索引不一致、task 与任务 name 不一致
- 字段约束违反：summary 必须是非空字符串；issues 必须是数组

**故障分类**：
- 退出码1属于"一般错误"类别（[D2][D3]），具体含义由应用程序定义
- 错误类型：结构化输出契约失败（缺少必需字段、包含未定义字段、任务身份不一致）
- 失败阶段：CLI生命周期完成但输出不符合Schema校验

**与前次失败案例的对比**：
- Task 29、49、81、291同样出现退出码1和结构化输出契约失败
- Task 412的错误模式与前次完全一致：缺少必需字段、包含额外字段、任务身份不一致
- 共同根因：CLI执行成功但输出格式不符合Schema校验要求
- 任务产物目录包含 agent-events.log、agent-final.txt、agent-stderr.log 等诊断文件，但科学正确性尚未得到有效报告确认

**诊断要点**：
1. **退出码1的结构化输出故障特征**：
   - 缺少顶层必需字段（issues、summary、task、task_id）
   - 包含未在Schema中定义的额外字段（error、sessionID、timestamp、type）
   - 字段类型不匹配（issues必须是数组，summary必须是非空字符串）
   - 任务身份不一致（task_id与任务索引不匹配，task与任务name不匹配）

2. **重复故障模式确认**：
   - 这是该故障模式在不同任务（29→49→81→291→412）上的第5次复现
   - 故障特征完全一致，说明根因未被修复

**修复路径**：
1. **输出前Schema校验**：在CLI输出报告前，使用JSON Schema验证器检查报告格式
2. **字段完整性检查**：确保所有必需字段（issues、summary、task、task_id）存在且类型正确
3. **附加字段控制**：使用`additionalProperties: false`严格模式，禁止未定义字段
4. **任务身份校验**：在输出前确认task_id与任务索引一致、task与任务name一致
5. **错误日志分析**：结合stderr和结构化错误信息定位具体失败原因

**预防措施**：
- 实现CLI输出前的Schema校验流程
- 使用类型注解和验证确保输出结构正确
- 提供详细的错误信息帮助诊断
- 实现优雅的失败处理机制
- 在CLI启动前验证任务身份信息的一致性
- 对重复出现的故障模式实施回归保护（防止已修复问题复发）

## 批次补充（2026-09-17-harvest-task97）

### 跨物种抗菌药物耐药性预测归因分析CLI故障

**失败现象**：归因分析CLI退出码为1，未产生有效的结构化报告。

**错误详情**：
- 校验错误：缺少顶层字段 ['issues', 'summary', 'task', 'task_id']
- 额外字段：包含 ['error', 'sessionID', 'timestamp', 'type']
- 任务身份不一致：task_id 与任务索引不一致、task 与任务 name 不一致
- 字段约束违反：summary 必须是非空字符串；issues 必须是数组

**故障分类**：
- 退出码1属于"一般错误"类别（[D2][D3]），具体含义由应用程序定义
- 错误类型：结构化输出契约失败（缺少必需字段、包含未定义字段、任务身份不一致）
- 失败阶段：CLI生命周期完成但输出不符合Schema校验

**与前次失败案例的对比**：
- Task 29、49、81、291、412同样出现退出码1和结构化输出契约失败
- Task 97的错误模式与前次完全一致：缺少必需字段、包含额外字段、任务身份不一致
- 共同根因：CLI执行成功但输出格式不符合Schema校验要求
- 任务产物目录包含 agent-events.log、agent-final.txt、agent-stderr.log 等诊断文件，但科学正确性尚未得到有效报告确认

**诊断要点**：
1. **退出码1的结构化输出故障特征**：
   - 缺少顶层必需字段（issues、summary、task、task_id）
   - 包含未在Schema中定义的额外字段（error、sessionID、timestamp、type）
   - 字段类型不匹配（issues必须是数组，summary必须是非空字符串）
   - 任务身份不一致（task_id与任务索引不匹配，task与任务name不匹配）

2. **重复故障模式确认**：
   - 这是该故障模式在不同任务（29→49→81→291→412→97）上的第6次复现
   - 故障特征完全一致，说明根因未被修复

**修复路径**：
1. **输出前Schema校验**：在CLI输出报告前，使用JSON Schema验证器检查报告格式
2. **字段完整性检查**：确保所有必需字段（issues、summary、task、task_id）存在且类型正确
3. **附加字段控制**：使用`additionalProperties: false`严格模式，禁止未定义字段
4. **任务身份校验**：在输出前确认task_id与任务索引一致、task与任务name一致
5. **错误日志分析**：结合stderr和结构化错误信息定位具体失败原因

**预防措施**：
- 实现CLI输出前的Schema校验流程
- 使用类型注解和验证确保输出结构正确
- 提供详细的错误信息帮助诊断
- 实现优雅的失败处理机制
- 在CLI启动前验证任务身份信息的一致性
- 对重复出现的故障模式实施回归保护（防止已修复问题复发）

## 批次补充（2026-09-17-harvest-CFD-S004）

### 几何编码网络跨声速翼型激波流场预测归因分析CLI故障

**失败现象**：归因分析CLI退出码为1，未产生有效的结构化报告。

**错误详情**：
- 校验错误：报告根节点不是JSON对象
- JSON语法错误：Expecting ',' delimiter: line 1 column 1112 (char 1111)
- 任务产物目录包含：agent-events.log、agent-final.txt、agent-stderr.log、analysis-events.jsonl、analysis-stderr.log、blocked-run.log、preflight-evidence.json、report-agent-final.txt
- 任务产物的科学正确性尚未得到有效报告确认

**故障分类**：
- 退出码1属于"一般错误"类别（[D2][D3]），具体含义由应用程序定义
- 错误类型：JSON解析失败（语法错误导致报告根节点无法识别为JSON对象）
- 失败阶段：CLI生命周期完成但输出格式不符合JSON解析要求

**与前次失败案例的对比**：
- Task 29、49、81、291、412、97同样出现退出码1
- 但本次故障特征不同：前次为"结构化输出契约失败"（缺少必需字段、包含额外字段），本次为"JSON语法错误"
- 前次CLI能产生JSON但不符合Schema校验，本次CLI产生的输出甚至不是有效JSON

**诊断要点**：
1. **JSON语法错误的常见原因**：
   - 字符串未正确转义（如包含未转义的引号或反斜杠）
   - 数值格式错误（如NaN、Infinity）
   - 字符串拼接错误（如生成过程中断）
   - 编码问题（如UTF-8 BOM、特殊字符）

2. **错误位置定位**：
   - 错误发生在第1行第1112字符（char 1111）
   - 这表明JSON在前1111个字符是有效的，之后出现语法错误
   - 可能是某个字段值过长或包含特殊字符导致解析失败

3. **与前次故障的本质区别**：
   - 前次：CLI产生有效JSON，但Schema校验失败（字段缺失/多余）
   - 本次：CLI产生的输出不是有效JSON（语法错误）
   - 前次需要修复Schema合规性，本次需要修复JSON生成逻辑

**修复路径**：
1. **检查输出内容**：读取report-agent-final.txt，定位第1112字符附近的语法错误
2. **验证JSON格式**：使用JSON验证工具检查输出文件的语法正确性
3. **检查特殊字符**：确保所有字符串值中的引号、反斜杠等特殊字符已正确转义
4. **验证编码**：确保输出文件使用UTF-8编码，无BOM头
5. **分段生成**：考虑分段生成JSON并在最后拼接，避免单次生成过长导致错误

**预防措施**：
- 实现JSON输出前的语法验证（而非仅Schema验证）
- 使用JSON序列化库（如json.dumps）而非字符串拼接生成JSON
- 对长字符串进行截断或转义处理
- 添加编码声明和特殊字符转义逻辑
- 实现增量JSON生成，避免一次性生成大文件