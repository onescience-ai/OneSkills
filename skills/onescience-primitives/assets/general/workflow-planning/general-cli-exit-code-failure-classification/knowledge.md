# CLI 非交互执行与故障分类

## 适用范围

**触发条件**：
- 需要诊断命令行工具在自动化工作流中的异常退出
- 需要根据进程退出码判断故障类型并制定修复策略
- 需要区分超时、信号中断、参数错误、权限问题等不同故障根因

**适用场景**：
- 科研工作流中CLI工具的自动化调用与监控
- 批量作业提交后的失败诊断与重试策略
- CI/CD管道中命令执行状态的判断与处理
- 跨平台（Linux/macOS/Windows）脚本的退出码兼容性设计

**不适用场景**：
- 交互式Shell会话中的命令调试（应使用交互式调试工具）
- 需要深入进程内部状态的调试（应使用gdb/lldb等调试器）
- 网络服务进程的健康检查（应使用专门的健康检查机制）

## 输入

**输入数据格式**：
- 进程退出码（整数，0-255）
- 标准错误输出（stderr）
- 进程运行日志（可选）
- 执行环境信息（操作系统、Shell类型、Python版本）

**来源**：
- Shell变量 `$?` 或 `$LASTEXITCODE`（PowerShell）
- Python `subprocess.run()` 的 `returncode` 属性
- 作业调度系统（SLURM、PBS）的作业状态码

**预处理要求**：
- 确保退出码未被Shell截断（仅取低8位）
- 收集完整的stderr输出用于根因分析

## 输出

**输出产物**：
- 故障分类报告（JSON格式）
- 根因分析结论
- 修复建议与重试策略

**格式**：
```json
{
  "exit_code": 1,
  "category": "general_error",
  "root_cause": "参数错误或运行时异常",
  "severity": "recoverable",
  "retry_strategy": "检查输入参数后重试"
}
```

**验证标准**：
- 退出码语义解读符合POSIX/平台约定
- 故障分类覆盖主要失败场景
- 修复建议可执行、可验证

## 流程节点

### Step 1：退出码捕获
- **操作**：在命令执行后立即捕获退出码
- **参数**：Shell=`$?`，Python=`subprocess.run().returncode`
- **工具**：Shell内置变量、Python subprocess模块
- **质量门禁**：退出码为有效整数（0-255）

### Step 2：语义映射
- **操作**：将退出码映射到标准语义类别
- **参数**：参考POSIX标准与平台约定
- **工具**：退出码语义映射表（见关键参数）
- **质量门禁**：映射结果非空，覆盖已知退出码

### Step 3：故障分类
- **操作**：根据语义映射结果进行故障分类
- **参数**：分类维度=可恢复性、严重程度、是否需要人工干预
- **工具**：故障分类决策树
- **质量门禁**：分类结果明确，无歧义

### Step 4：根因分析
- **操作**：结合stderr输出分析具体故障原因
- **参数**：输入=退出码+stderr+日志
- **工具**：模式匹配、关键词提取
- **质量门禁**：根因描述具体、可验证

### Step 5：修复建议生成
- **操作**：根据故障分类生成修复建议
- **参数**：分类结果、历史修复经验
- **工具**：修复建议模板库
- **质量门禁**：建议可执行、有明确步骤

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 成功退出码 | 0 | [D1][D2][D3] | 所有平台通用的成功标识 |
| 一般错误 | 1 | [D2][D3] | 捕获所有通用错误 |
| Shell内置误用 | 2 | [D2] | Bash文档定义的内置命令误用 |
| 命令不可执行 | 126 | [D2] | 权限问题或非可执行文件 |
| 命令未找到 | 127 | [D2] | PATH问题或命令拼写错误 |
| 无效退出参数 | 128 | [D2] | exit参数超出0-255范围 |
| 信号中断 | 128+n | [D2] | n为信号编号（如Ctrl+C=130） |
| Python退出码 | 0-127 | [D3] | Python约定0=成功，非0=异常 |
| Python字符串异常 | 1 | [D3] | sys.exit("error")输出到stderr |
| 退出码有效范围 | 0-255 | [D1][D2][D3] | 仅低8位可用 |

### 校准数值（平台特定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Linux默认Shell | bash | [D2] | 退出码行为以Bash为准 |
| Python清理失败码 | 120 | [D3] | Python 3.6+清理失败时返回 |
| Windows等效码 | 与Linux相同 | [D3] | Python跨平台行为一致 |

> 以上数值来自POSIX/Linux/Python标准环境，供量级校准；其他平台（如Windows CMD、PowerShell）需以自身证据重新锚定。

## 边界与分流

**前提1：退出码可捕获**
- 若进程被SIGKILL(9)强制终止，退出码可能不可靠
- 分流：检查系统日志（dmesg/journalctl）获取OOM或硬件故障信息

**前提2：退出码未被截断**
- 某些Shell可能对退出码取模（% 256）
- 分流：使用Python subprocess直接获取原始退出码

**前提3：stderr可读**
- 若进程输出被重定向或管道截断
- 分流：检查日志文件或启用详细输出模式

**前提4：平台约定一致**
- Windows与Linux退出码语义可能存在差异
- 分流：查阅平台特定文档，建立映射表

## 质量检查

**验证点**：
1. 退出码是否在有效范围（0-255）
2. 语义映射是否覆盖所有已知退出码
3. 故障分类是否无歧义
4. 修复建议是否可执行
5. 是否考虑了平台差异

**阈值**：
- 已知退出码覆盖率 ≥ 90%
- 故障分类准确率 ≥ 85%（需人工验证）
- 修复建议可执行率 ≥ 80%

**失败处理**：
- 未知退出码：标记为"未分类"，收集更多信息
- 语义冲突：以平台官方文档为准，记录冲突
- 修复建议无效：回退到通用修复策略（重试、回滚）

## 回退策略

**策略1：通用重试**
- 适用于可恢复性错误（exit code 1）
- 重试次数：3次，间隔递增（1s, 5s, 15s）

**策略2：参数检查**
- 适用于参数错误（exit code 126, 127）
- 检查项：命令路径、权限、依赖库

**策略3：环境重置**
- 适用于环境问题（exit code 127）
- 操作：重建conda环境、重新加载modules

**策略4：人工介入**
- 适用于严重错误或未知退出码
- 操作：收集诊断信息，报告给运维团队

## 资源召回建议

**何时应召回本卡片**：
- 自动化工作流中CLI工具返回非零退出码
- 需要批量诊断多个作业的失败原因
- 需要设计健壮的错误处理与重试逻辑
- 需要跨平台兼容的退出码处理方案

**配套资源**：
- `general-json-schema-report-validation`：用于验证结构化故障报告的格式
- `onescience-runtime`：用于SLURM作业的退出码诊断
- `onescience-installer`：用于环境相关故障的修复

## 补充证据

[D1] "The GNU C Library (glibc) manual - exit", GNU Project, Free Software Foundation, version 2.44, URL: https://www.gnu.org/software/libc/manual/html_node/Exit-Status.html (accessed 2026-09-17，权威标准文档)

[D2] "Exit Codes With Special Meanings - Advanced Bash-Scripting Guide", The Linux Documentation Project, Appendix E, URL: https://tldp.org/LDP/abs/html/exitcodes.html (accessed 2026-09-17，经典参考)

[D3] "Python sys.exit() documentation", Python Software Foundation, version 3.14.7, URL: https://docs.python.org/3/library/sys.html#sys.exit (accessed 2026-09-17，官方文档)

[D4] "POSIX.1-2017 exit() specification", IEEE/The Open Group, Issue 7 2018, URL: https://pubs.opengroup.org/onlinepubs/9699919799/functions/exit.html (accessed 2026-09-17，标准规范)

## 证据来源

[D1] The GNU C Library (glibc) manual - exit, GNU Project, Free Software Foundation, version 2.44
[D2] Exit Codes With Special Meanings - Advanced Bash-Scripting Guide, The Linux Documentation Project, Appendix E
[D3] Python sys.exit() documentation, Python Software Foundation, version 3.14.7
[D4] POSIX.1-2017 exit() specification, IEEE/The Open Group, Issue 7 2018