# CLI Non-Interactive Execution and Failure Classification

## 适用范围
适用于需要在非交互式环境（自动化脚本、CI/CD 管道、批处理任务）中执行命令行程序并处理其执行结果的场景，包括但不限于科学计算任务的 CLI 包装器、数据处理流水线的外部工具调用等。

## 输入
- 命令字符串或参数列表
- 超时时间（秒）
- 工作目录
- 环境变量
- 输入数据（通过 stdin 或临时文件传递）

## 输出
- 进程退出码（returncode）
- 标准输出（stdout）
- 标准错误（stderr）
- 执行状态（成功/失败/超时）

## 流程节点
1. **命令构造** → 2. **进程启动** → 3. **输出捕获** → 4. **超时监控** → 5. **退出码分析** → 6. **错误分类**

每步含：操作、参数、工具、质量门禁

### 1. 命令构造
- 操作：将命令字符串或参数列表格式化为可执行格式
- 参数：命令字符串、参数列表、shell 标志
- 工具：shlex.split()（推荐）、shell=True（谨慎使用）
- 质量门禁：参数列表避免 shell 注入风险；特殊字符需正确转义

### 2. 进程启动
- 操作：使用 subprocess.run() 或 Popen() 启动子进程
- 参数：stdin/stdout/stderr 管道设置、cwd、env
- 工具：subprocess 模块
- 质量门禁：确保 stdin/stdout/stderr 管道正确设置以捕获输出

### 3. 输出捕获
- 操作：等待进程完成并读取 stdout/stderr
- 参数：timeout、input（可选）
- 工具：Popen.communicate()
- 质量门禁：避免管道死锁；大数据量时考虑流式处理

### 4. 超时监控
- 操作：设置并监控执行超时
- 参数：timeout 秒数
- 工具：subprocess.run(timeout=...) 或 Popen.communicate(timeout=...)
- 质量门禁：超时后正确终止子进程；捕获 TimeoutExpired 异常

### 5. 退出码分析
- 操作：检查进程返回码
- 参数：returncode
- 工具：CompletedProcess.returncode
- 质量门禁：0 表示成功；非零表示失败；负值表示信号终止（POSIX）

### 6. 错误分类
- 操作：根据退出码和异常类型分类错误
- 参数：returncode、异常类型、stdout/stderr 内容
- 工具：异常类层次结构
- 质量门禁：区分程序错误、系统错误、超时错误；提供有意义的错误信息

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 成功退出码 | 0 | [D1] | 标准 Unix/Linux 退出码约定 |
| 信号终止退出码 | -N (POSIX) | [D1] | N 为信号编号 |
| 超时异常 | TimeoutExpired | [D1] | 子进程超时未完成 |
| 非零退出异常 | CalledProcessError | [D1] | check=True 时非零退出码 |

## 边界与分流
- **超时处理**：超时后必须终止子进程（proc.kill()）并等待其结束
- **管道死锁**：避免直接读写 stdin/stdout/stderr，使用 communicate() 方法
- **Windows 兼容性**：Windows 下 shell=True 会使用 cmd.exe，注意命令格式差异
- **信号处理**：POSIX 下负退出码表示信号终止，Windows 下 kill() 等同于 terminate()

## 质量检查
- 验证退出码是否符合预期（0 为成功）
- 检查 stdout/stderr 是否包含错误信息
- 验证超时设置是否合理
- 确认异常处理是否覆盖所有失败场景

## 回退策略
- 超时后重试（增加超时时间或简化命令）
- 降级处理（部分执行结果可用时继续）
- 日志记录（保存 stdout/stderr 用于调试）

## 资源召回建议
- 当需要在自动化脚本中执行外部命令时召回本卡
- 当需要处理 CLI 程序的执行结果和错误时召回本卡
- 配套资源：onescience-runtime（执行环境管理）、onescience-installer（环境安装）

## 补充证据（开源文档）
[D1] Python subprocess module documentation, Python Software Foundation, v3.14, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-21，官方权威文档）

## 证据来源
[1] Testing Error Handling Code With Software Fault Injection and Error-Coverage-Guided Fuzzing, Jia-Ju Bai et al., IEEE Transactions on Dependable and Secure Computing, 2024, DOI: 10.1109/tdsc.2023.3288876
[2] Implementing Centralized Error Handling for Software Systems through the Integration of Machine Learning Techniques, Engineering: Open Access, 2023, DOI: 10.33140/eoa.01.01.11
