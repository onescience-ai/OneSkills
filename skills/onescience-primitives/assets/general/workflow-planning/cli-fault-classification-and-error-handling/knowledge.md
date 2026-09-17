# CLI 非交互执行与故障分类知识

## 适用范围

本卡为需要在自动化环境（脚本、CI/CD、科学计算流水线）中执行 CLI 命令并诊断失败的场景提供通用方法框架。适用于任何需要以非交互方式启动子进程、捕获输出、判断退出状态并执行恢复策略的任务。
不适用于交互式终端调试、图形界面应用或仅需简单 `os.system()` 调用的场景。
## 输入

- **命令与参数**：完整的命令字符串或参数列表
- **超时设置**：可选的秒级超时阈值
- **环境变量**：可选的自定义环境映射
- **工作目录**：可选的 `cwd` 路径
- **输入数据**：通过 stdin 传递的字节或字符串（可选）

## 输出

- **returncode**：子进程退出码（整数）
- **stdout**：标准输出捕获内容（字节或字符串）
- **stderr**：标准错误捕获内容（字节或字符串）
- **异常对象**：`CalledProcessError` 或 `TimeoutExpired`（当 `check=True` 或超时触发时）
## 流程节点

### 1. 命令构建与参数化

操作：将命令拆分为参数列表，避免 shell 注入风险。
```
subprocess.run(["program", "arg1", "arg2"], check=False)
```

工具：`shlex.split()` 可将单字符串命令安全分词。
质量门禁：参数列表不含未转义的 shell 元字符。
### 2. 输出捕获配置

操作：设置 `stdout=subprocess.PIPE` 和 `stderr=subprocess.PIPE` 以捕获输出；若需合并 stderr 和 stdout，使用 `stderr=subprocess.STDOUT`。
```
result = subprocess.run(cmd, capture_output=True, text=True)
```

工具：`capture_output=True` 是 `stdout=PIPE, stderr=PIPE` 的简写。
质量门禁：大输出场景使用流式读取避免内存溢出。
### 3. 超时控制

操作：设置 `timeout=N`（秒），超时后子进程被 `kill()`，抛出 `TimeoutExpired`。
```
try:
    result = subprocess.run(cmd, timeout=30)
except subprocess.TimeoutExpired:
    # 进程已被终止，可重试或记录
```

工具：`TimeoutExpired` 异常提供 `cmd`、`timeout`、`output`、`stdout`、`stderr` 属性用于诊断。
质量门禁：超时后必须调用 `proc.communicate()` 完成管道清理，避免僵尸进程。
### 4. 退出码判读

操作：检查 `returncode` 值。
| 退出码 | 含义 | 典型原因 |
|--------|------|----------|
| 0 | 成功 | 正常完成 |
| 1 | 通用错误 | 参数错误、运行时异常 |
| 2 | 误用 shell 命令 | 命令语法错误 |
| 126 | 权限不足 | 文件不可执行 |
| 127 | 命令未找到 | PATH 中无该程序 |
| 128+N | 被信号 N 终止 | SIGKILL(9)、SIGTERM(15) |
| 130 | Ctrl+C | SIGINT(2) |
| -N (POSIX) | 被信号 N 终止 | 内核信号 |

工具：`returncode` 属性直接读取。
质量门禁：正数退出码需配合 stderr 内容进行根因分析。
### 5. 异常分类与恢复

操作：根据异常类型执行不同恢复策略。
- **CalledProcessError**：`check=True` 时非零退出码触发。检查 `returncode`、`stdout`、`stderr` 属性。
- **TimeoutExpired**：超时触发。先 `kill()` 后 `communicate()` 清理管道。
- **OSError**：程序不存在或权限不足。验证路径和执行权限。
- **ValueError**：参数非法。检查 `Popen` 构造参数。
工具：异常类层次 `SubprocessError → CalledProcessError / TimeoutExpired`。
质量门禁：每次异常处理后记录完整诊断上下文（命令、退出码、输出、异常栈）。
### 6. 诊断证据保留

操作：将 stdout、stderr、returncode、异常信息写入结构化日志或报告文件。
```
{
  "command": "...",
  "returncode": 1,
  "stdout": "...",
  "stderr": "...",
  "error_type": "CalledProcessError",
  "error_message": "..."
}
```

工具：JSON 格式输出便于下游自动化处理。
质量门禁：诊断文件在进程异常退出后仍可读。
## 关键参数

### 通用判据（方法层）
| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| check | False（首次执行） | [D1] | 首次执行避免异常中断，后续手动检查 returncode |
| capture_output | True | [D1] | 自动捕获 stdout+stderr 用于诊断 |
| text | True | [D1] | 以字符串而非字节返回输出，便于日志记录 |
| timeout | 按任务设置 | [D1] | 防止无限挂起，超时后 kill+communicate 清理 |
| shell | False | [D1] | 避免 shell 注入，优先使用参数列表 |

### 校准数值（实例参考值）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| SIGKILL 退出码 | 128+9=137 | [D1] | bash 下 kill -9 的典型退出码 |
| SIGTERM 退出码 | 128+15=143 | [D1] | bash 下 kill -15 的典型退出码 |
| SIGINT 退出码 | 128+2=130 | [D1] | Ctrl+C 的典型退出码 |

## 边界与分流
- **shell=True 场景**：仅在需要 shell 特性（管道、通配符）时使用，且必须用 `shlex.quote()` 转义用户输入。
- **POSIX vs Windows**：信号退出码仅 POSIX 支持；Windows 下 `TerminateProcess()`，退出码为 1。
- **大输出场景**：避免 `communicate()` 一次性读取，改用流式 `proc.stdout.readline()`。
- **子解释器/嵌入环境**：`preexec_fn` 在子解释器中不可用，改用 `start_new_session` 或 `process_group`。
## 质量检查
- 每次执行后检查 returncode 是否在预期范围内
- stderr 非空时触发人工审查或自动诊断
- 超时事件必须有 kill + communicate 的清理记录
- 退出码 126/127 指示环境问题，需检查 PATH 和文件权限
## 回退策略

- **程序不存在（127）**：检查 PATH、使用 `shutil.which()` 验证路径
- **权限不足（126）**：`chmod +x` 或检查文件系统挂载
- **超时**：增加 timeout 值、优化命令性能、拆分子任务
- **信号终止（137）**：检查 OOM Killer 日志、降低内存使用
## 资源召回建议

- 当任务涉及自动化 CLI 执行、CI/CD 流水线、科学计算批处理时召回本卡。
- 配套卡片：`json-schema-report-validation-contract`（用于结构化报告输出验证）。
## 证据来源

[D1] Python subprocess - Subprocess management, Python Software Foundation, Python 3.14.7, URL: https://docs.python.org/3/library/subprocess.html (accessed_at: 2026-09-16)

## 批次补充

### 补充证据：Bash Shell退出码语义

基于GNU Bash Reference Manual，补充以下通用判据：

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 成功状态码 | 0 | [D2] | 命令成功执行完成 |
| 命令未找到 | 127 | [D2] | 系统找不到指定命令 |
| 命令不可执行 | 126 | [D2] | 命令存在但无执行权限 |
| 信号终止码 | 128+N | [D2] | 进程被信号N终止，N为信号编号 |
| Shell内置命令错误 | 2 | [D2] | 内置命令参数错误或缺失 |
| 最大退出码值 | 255 | [D2] | 退出码为8位，最大255 |

[D2] GNU Bash Reference Manual - Exit Status, https://www.gnu.org/software/bash/manual/bash.html#Exit-Status