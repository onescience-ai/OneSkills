# 通用CLI故障诊断与错误处理

## 适用范围

面向命令行接口（CLI）工具的非交互执行场景，提供故障识别、分类、诊断和恢复的系统化方法。适用于自动化脚本调用、CI/CD流水线、批处理任务等需要无人值守执行CLI工具的场景。不适用于交互式终端会话或GUI应用程序的错误处理。

## 输入

- **CLI工具路径**：可执行文件的绝对或相对路径
- **命令参数**：完整的命令行参数列表
- **执行环境**：操作系统类型、shell环境、资源限制配置
- **超时配置**：预期执行时间上限（秒）
- **重试策略**：最大重试次数、重试间隔

## 输出

- **退出码分类**：成功(0)、用户错误(1-2)、内部错误(2-125)、信号中断(126-128+)、自定义错误码(128-255)
- **错误类型映射**：参数错误、权限不足、资源不可用、超时、依赖缺失、沙箱限制
- **诊断报告**：错误类别、根因分析、恢复建议
- **恢复操作**：自动重试、降级执行、人工介入请求

## 流程节点

### 1. 执行前预检
- **操作**：验证CLI路径存在、可执行权限、依赖库可用
- **参数**：`os.path.exists()`, `os.access(path, os.X_OK)`
- **工具**：Python os模块、shutil.which()
- **质量门禁**：预检失败时返回明确的预检错误码（专用约定：126表示权限错误）

### 2. 执行与超时监控
- **操作**：启动子进程，设置超时计时器，监控stdout/stderr
- **参数**：`subprocess.Popen()`, `timeout`参数
- **工具**：Python subprocess模块
- **质量门禁**：超时触发时强制终止进程（SIGTERM → SIGKILL）

### 3. 退出码捕获与分类
- **操作**：读取returncode，按POSIX标准分类
- **参数**：
  - 0：成功
  - 1-2：用户错误（参数无效、配置错误）
  - 2-125：内部错误（程序bug、资源不足）
  - 126：命令不可执行（权限或格式错误）
  - 127：命令未找到
  - 128+N：被信号N终止（N=信号编号）
  - 129=SIGHUP, 130=SIGINT, 137=SIGKILL, 143=SIGTERM
- **工具**：位运算分析returncode
- **质量门禁**：非标准退出码需记录为"自定义错误码"

### 4. 标准错误流解析
- **操作**：捕获stderr输出，提取关键错误信息
- **参数**：正则匹配常见错误模式（timeout, permission denied, not found, connection refused）
- **工具**：Python re模块
- **质量门禁**：空stderr时标记为"无诊断信息"

### 5. 根因定位
- **操作**：综合退出码、stderr、环境信息确定根因
- **参数**：错误分类矩阵
- **工具**：决策树/规则引擎
- **质量门禁**：根因置信度低于阈值时标记为"需人工确认"

### 6. 恢复策略选择
- **操作**：根据错误类别选择恢复路径
- **参数**：重试策略、降级选项、告警阈值
- **工具**：策略配置表
- **质量门禁**：可恢复错误最多重试N次，不可恢复错误立即上报

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码位宽 | 8 bits (0-255) | [D1] POSIX标准 | 超出范围的返回码被截断为低8位 |
| 信号编号偏移 | 128 + signal_number | [D1] POSIX标准 | 被信号终止的进程退出码计算方式 |
| 默认超时 | 无（无限等待） | [D2] Python subprocess | 未设置timeout参数时的行为 |
| SIGTERM等待期 | 5秒 | [D2] Python subprocess | 发送SIGTERM后等待进程退出的时间 |
| stderr缓冲 | 行缓冲 | [D2] Python subprocess | 非管道模式下的缓冲行为 |

### 校准数值（实例值，供量级校准）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 常见自定义错误码范围 | 64-78 | [D2] sysexits.h约定 | BSD/Linux系统常用约定，非强制标准 |
| SIGKILL后强制终止延迟 | 100ms | [D2] Python subprocess实践 | 发送SIGKILL后的等待时间 |
| 最大stderr捕获长度 | 64KB | [D2] Python实践 | 防止无限缓冲的截断阈值 |

## 边界与分流

### 前提1：CLI工具遵循POSIX退出码约定
- **不成立时转向**：解析特定工具的退出码文档（如Git使用128+N，Docker使用自定义范围）

### 前提2：操作系统支持标准信号机制
- **不成立时转向**：Windows平台需使用`os.kill()`的特殊处理，或依赖Windows错误代码而非信号

### 前提3：stderr包含有用诊断信息
- **不成立时转向**：启用verbose模式、添加--debug参数、检查日志文件

### 前提4：工具支持超时参数或可被外部终止
- **不成立时转向**：使用进程组（`os.setsid`）+ `os.killpg()`实现外部超时控制

## 质量检查

### 退出码校验
- 验证退出码在0-255范围内
- 检查信号退出码的信号编号有效性（1-31）
- 记录所有非标准退出码

### 错误流完整性
- 验证stderr非空（对于失败场景）
- 检查stderr是否包含可解析的错误模式
- 验证日志文件写入成功

### 超时检测准确性
- 验证超时后进程确实被终止
- 检查超时时间与实际执行时间的偏差
- 记录超时触发时的进程状态

## 回退策略

### 重试策略
- **可恢复错误**（如网络超时、资源暂时不可用）：最多重试3次，间隔指数退避（1s, 2s, 4s）
- **不确定错误**：重试1次并记录详细日志
- **不可恢复错误**（如权限不足、命令不存在）：立即终止并上报

### 降级策略
- **完整执行失败**：尝试最小化参数执行
- **依赖缺失**：检查是否可安装或使用替代工具
- **沙箱限制**：请求权限提升或切换执行环境

### 人工介入
- 连续失败超过阈值（默认3次）触发告警
- 不可分类的错误码（128-255中的未知值）立即上报
- 资源耗尽（内存、磁盘）需人工评估

## 资源召回建议

**何时召回本卡片**：
- 需要构建CLI工具的自动化执行框架
- 需要设计CLI工具的错误处理和恢复机制
- 需要诊断CLI工具在自动化环境中的失败问题
- 需要设计CI/CD流水线中的工具调用容错机制

**配套资源**：
- `general-json-schema-validation-report-contract`：验证CLI工具的结构化输出
- `general-process-timeout-monitor`：进程超时监控（如需更详细的超时处理）
- `general-error-logging-standard`：错误日志记录规范

## 补充证据

### 开源权威文档

[D1] **POSIX.1-2017 Standard (IEEE Std 1003.1-2017)**, IEEE/The Open Group, 2017. URL: https://pubs.opengroup.org/openpubs/9699919799/ (accessed_at: 2026-09-16, 交叉验证：退出码规范与信号机制)
- 第2.8.2节"Exit Status"定义了wait status的解释方式
- 第3.1.2节"Termination Signals"定义了信号与退出码的关系

[D2] **Python 3.12 Documentation: subprocess - Subprocess management**, Python Software Foundation, 2024. URL: https://docs.python.org/3/library/subprocess.html (accessed_at: 2026-09-16, 单源参考)
- `subprocess.run()`的timeout参数、check参数、capture_output参数
- `Popen.wait()`的timeout实现机制
- Windows与Unix平台的差异处理

[D3] **Python 3.12 Documentation: argparse - Parser for command-line options**, Python Software Foundation, 2024. URL: https://docs.python.org/3/library/argparse.html (accessed_at: 2026-09-16, 单源参考)
- `parse_args()`失败时的退出码处理（默认调用`sys.exit(2)`）
- `add_mutually_exclusive_group()`的错误处理

## 证据来源

本文档基于以下权威技术标准和官方文档：
- [D1] POSIX.1-2017 Standard (IEEE Std 1003.1-2017) - 退出码和信号机制的权威定义
- [D2] Python 3.12 subprocess模块文档 - CLI工具调用的实践参考
- [D3] Python 3.12 argparse模块文档 - CLI参数解析的错误处理参考
