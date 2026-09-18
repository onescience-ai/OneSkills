# CLI非交互执行与故障分类知识

## 适用范围

**触发条件**：
- 需要理解命令行接口（CLI）工具的非交互执行流程
- 需要对CLI执行故障进行分类和诊断
- 需要设计CLI工具的测试和验证框架
- 需要处理CLI执行中的错误码和标准错误输出

**适用场景**：
- CLI工具的自动化测试和评估
- 命令行工具的故障诊断和调试
- CLI安全风险分析和防护
- 命令行工具的用户体验优化
- 自然语言到CLI命令的转换系统

**不适用场景**：
- 图形用户界面（GUI）工具的评估
- 交互式CLI会话的实时调试
- 特定领域的科学计算CLI工具（需结合领域知识）

## 输入

- CLI工具的执行规范和文档
- 命令行参数和选项定义
- 执行环境配置（沙箱、容器等）
- 测试用例和预期输出
- 错误码和退出码规范

## 输出

- 故障分类体系（构建失败、执行失败、行为不匹配等）
- 多层等价性评估结果（执行可靠性、副作用一致性、行为等价性）
- 诊断报告（错误原因分析、修复建议）
- 验证通过率统计

## 流程节点

### Step 1：CLI工具规范分析
- **操作**：解析CLI工具的man页面、README文档和--help输出
- **参数**：工具名称、版本、支持的操作系统
- **工具**：文档解析器、LLM辅助提取
- **质量门禁**：完整提取命令结构、参数类型、约束条件

### Step 2：测试用例生成
- **操作**：基于规范生成多样化的测试用例
- **参数**：测试覆盖率要求、边界条件、错误输入
- **工具**：LLM辅助模糊测试、模板生成
- **质量门禁**：测试用例覆盖所有命令模式、包含正常和异常路径

### Step 3：隔离沙箱执行
- **操作**：在隔离环境中执行CLI工具
- **参数**：容器配置、网络隔离、文件系统快照
- **工具**：Docker、沙箱环境
- **质量门禁**：环境一致性、状态隔离、可重复性

### Step 4：多层等价性评估
- **操作**：比较生成工具与参考实现的行为
- **参数**：等价性阈值、匹配策略
- **工具**：差分测试框架、语义匹配器
- **质量门禁**：
  - 执行可靠性（Exec）：工具成功执行无异常
  - 副作用一致性（SP）：文件系统修改匹配
  - 行为等价性（EM/FM/SM）：输出内容匹配

### Step 5：故障分类与诊断
- **操作**：分析失败用例，分类故障类型
- **参数**：故障类别定义、诊断规则
- **工具**：日志分析器、错误模式识别
- **质量门禁**：准确分类故障类型、提供可操作的诊断信息

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 测试仓库数量 | 94个真实世界仓库 | [1] | CLI-Tool-Bench基准数据集 |
| 编程语言 | Python、JavaScript、Go | [1] | 主流CLI开发语言 |
| 任务难度分层 | Easy(≤1500 LOC)、Medium(1500-4000 LOC)、Hard(≥4000 LOC) | [1] | 基于代码行数的难度划分 |
| 执行环境 | Docker隔离容器 | [1] | 确保环境一致性 |
| 等价性匹配策略 | 精确匹配(EM)、模糊匹配(FM)、语义匹配(SM) | [1] | 多层次输出比较 |
| CLI命令组合风险 | 96.59%攻击成功率 | [2] | MOSAIC框架评估结果 |
| 命令状态家族 | 13个家族 | [2] | CLI安全知识库组织结构 |
| 界面偏好 | 60% GUI、32% CLI | [3] | 系统管理员防火墙界面偏好研究 |

## 边界与分流

### 故障分类边界
1. **构建失败**：工具无法安装或编译
   - 分流：检查依赖关系、构建配置、环境兼容性
2. **执行失败**：工具安装成功但运行时崩溃
   - 分流：分析运行时错误、资源限制、环境依赖
3. **行为不匹配**：工具执行成功但输出不符合预期
   - 分流：比较输出差异、检查参数处理、验证业务逻辑

### 执行环境边界
- **网络隔离**：禁止外部网络访问，防止数据污染
- **文件系统隔离**：快照-恢复机制，避免状态泄漏
- **资源限制**：CPU、内存、磁盘空间限制

### 等价性评估边界
- **精确匹配**：适用于格式化输出、确定性结果
- **模糊匹配**：适用于允许格式差异的场景
- **语义匹配**：适用于内容等价但形式不同的场景

## 质量检查

- **构建成功率**：≥90%的测试用例能成功安装
- **执行成功率**：≥80%的已安装工具能正常运行
- **行为等价率**：≥70%的执行结果与参考实现语义等价
- **故障分类准确率**：≥85%的故障能被正确分类
- **诊断信息完整性**：每个故障都能提供可操作的修复建议

## 回退策略

- **环境不可用**：使用本地环境模拟，记录环境差异
- **测试用例不足**：基于规范补充生成，增加边界条件覆盖
- **参考实现缺失**：使用多个LLM生成结果进行交叉验证
- **网络限制**：使用本地缓存的文档和规范

## 资源召回建议

当遇到以下情况时应召回本卡片：
- CLI工具执行失败需要诊断
- 需要设计CLI工具的测试框架
- 需要评估CLI工具的可靠性
- 需要分析CLI安全风险
- 需要优化CLI工具的用户体验

配套资源：
- CLI工具开发规范
- 容器化和沙箱配置指南
- 错误码和退出码标准
- 自然语言处理技术

## 补充证据（开源权威文档）

[D1] Python subprocess Module Documentation, Python Software Foundation, 版本 3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-18，交叉验证）

## 批次补充 2026-09-18（onescience-knowledge-harvester）

### 补充证据：Python subprocess模块CLI执行与错误处理规范

本次补充引入Python官方文档中关于subprocess模块的CLI执行、错误处理和故障分类的权威规范，增强对进程退出码、异常类型和超时处理的理解。

**进程退出码语义**（基于 [D1]）：

| 退出码 | 含义 | 说明 |
|--------|------|------|
| 0 | 成功 | 进程正常退出 |
| 非零 | 失败 | 进程异常退出，具体值由程序定义 |
| 负值 -N | 信号终止 | 进程被信号N终止（仅POSIX系统） |

**异常类型分类**（基于 [D1]）：

| 异常类型 | 继承关系 | 触发条件 | 关键属性 |
|----------|----------|----------|----------|
| SubprocessError | 基类 | 所有subprocess模块异常 | - |
| TimeoutExpired | SubprocessError | 超时参数超时 | cmd, timeout, output, stdout, stderr |
| CalledProcessError | SubprocessError | check=True且非零退出码 | returncode, cmd, output, stdout, stderr |

**超时处理机制**（基于 [D1]）：

| 参数 | 说明 | 异常行为 |
|------|------|----------|
| timeout | 超时秒数，传递给Popen.communicate() | 超时后子进程被终止，抛出TimeoutExpired |
| 超时后行为 | 子进程未被kill，需手动清理 | 调用proc.kill()后再次communicate() |

**错误检查参数**（基于 [D1]）：

| 参数 | 说明 | 行为 |
|------|------|------|
| check=False（默认） | 不检查退出码 | 无论退出码如何都返回CompletedProcess |
| check=True | 检查退出码 | 非零退出码抛出CalledProcessError |

**输出捕获常量**（基于 [D1]）：

| 常量 | 说明 | 使用场景 |
|------|------|----------|
| PIPE | 创建新的管道连接到标准流 | 需要捕获stdout/stderr时 |
| DEVNULL | 使用os.devnull文件 | 不需要输出时 |
| STDOUT | stderr合并到stdout | 需要统一处理输出时 |

**CLI执行最佳实践**（基于 [D1]）：

1. **参数传递**：优先使用序列而非字符串，避免shell注入风险
2. **超时处理**：始终设置timeout参数，防止进程挂起
3. **错误处理**：根据场景选择check=True或check=False
4. **输出管理**：使用communicate()而非直接读写管道，避免死锁
5. **环境隔离**：使用env参数控制环境变量，避免继承敏感信息

**故障诊断策略**（基于 [D1]）：

| 故障类型 | 诊断方法 | 修复建议 |
|----------|----------|----------|
| 进程未找到 | 检查executable路径，使用shutil.which() | 使用完整路径或验证PATH |
| 超时 | 增加timeout值或优化程序性能 | 分析性能瓶颈，考虑异步处理 |
| 非零退出码 | 分析stderr输出，检查返回码语义 | 根据具体错误码采取相应措施 |
| 管道死锁 | 使用communicate()代替直接读写 | 确保管道缓冲区不会满 |

## 证据来源

[1] "Evaluating LLM-Based 0-to-1 Software Generation in End-to-End CLI Tool Scenarios", Ruida Hu et al., arXiv:2604.06742, 2026
[2] "MOSAIC: Knowledge-Guided CLI Command Composition Attack in LLM Coding Agents", Jiangrong Wu et al., arXiv:2607.02857, 2026
[3] "System Administrators Prefer Command Line Interfaces, Don't They? An Exploratory Study of Firewall Interfaces", Artem Voronkov et al., SOUPS 2019
[4] "The Command Line GUIde: Graphical Interfaces from Man Pages via AI", Saketh Ram Kasibatla et al., IEEE VL/HCC 2025
[5] "EQSANS-CLI: A natural-language, agent-ready command-line tool for small-angle neutron scattering data reduction at EQ-SANS", Changwoo Do, arXiv:2605.00651, 2026
[D1] Python subprocess Module Documentation, Python Software Foundation, 版本 3.14.7