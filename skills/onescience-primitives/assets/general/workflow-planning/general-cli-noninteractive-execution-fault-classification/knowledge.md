# CLI 非交互执行与故障分类

## 适用范围

在自动化工作流中以非交互方式调用 CLI 工具时，需要管理进程生命周期、捕获退出状态、处理超时与管道阻塞，并根据退出码对故障进行分类以决定恢复策略。本卡适用于 Python subprocess 调用、Shell 脚本编排、CI/CD 流水线中的 CLI 集成等场景。

## 输入

- 要执行的 CLI 命令（字符串或参数列表）
- 可选的 stdin 数据、环境变量、工作目录
- 超时限制（秒）
- 是否检查退出码（check 模式）

## 输出

- CompletedProcess 对象（含 returncode、stdout、stderr）
- 异常信息（CalledProcessError / TimeoutExpired / OSError）
- 结构化故障分类结果

## 流程节点

1. **进程创建** → 使用 subprocess.run() 或 Popen 创建子进程
2. **I/O 管道管理** → 通过 PIPE/DEVNULL/STDOUT 重定向标准流
3. **等待与超时** → communicate() 或 wait() 配合 timeout 参数
4. **退出码检查** → 检查 returncode 属性或使用 check=True 自动抛异常
5. **故障分类** → 根据退出码和异常类型判定故障类别
6. **恢复决策** → 根据故障类别选择重试、降级或终止

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| returncode | 0 | [D1] | 进程正常退出 |
| returncode | 非零正值 | [D1] | 进程异常退出，具体含义由程序定义 |
| returncode | 负值 -N | [D1] | 进程被信号 N 终止（仅 POSIX） |
| timeout | 用户指定秒数 | [D1] | 超时后触发 TimeoutExpired 异常 |
| check | True/False | [D1] | True 时非零退出码自动抛 CalledProcessError |

### 故障分类表

| 故障类别 | 退出码特征 | 异常类型 | 恢复策略 |
|----------|-----------|----------|----------|
| 正常完成 | 0 | 无 | 继续后续流程 |
| 逻辑错误 | 1-125 | CalledProcessError | 检查输入参数，修正后重试 |
| 信号终止 | -1 到 -31 | returncode 为负 | 检查资源限制，增大内存/时间配额 |
| 超时 | 无（进程被杀） | TimeoutExpired | 增大 timeout 值或优化命令 |
| 命令不存在 | 无（启动失败） | OSError | 检查 PATH 或使用绝对路径 |
| 权限拒绝 | 非零（通常 126/127） | CalledProcessError | 检查文件权限或 sudo 需求 |

## 边界与分流

- **shell=True 风险**：使用 shell=True 时，退出码反映 shell 本身状态而非命令；非必要不使用 shell=True
- **管道死锁**：stdout=PIPE 或 stderr=PIPE 时，若子进程输出量大且未调用 communicate()，可能阻塞；必须使用 communicate() 而非直接 read()
- **Windows 差异**：Windows 不支持信号终止语义，负退出码不适用；需使用 creationflags 参数控制进程组
- **编码问题**：默认使用二进制模式；需指定 encoding 或 text=True 获取字符串输出

## 质量检查

- 验证 returncode 是否为预期值（0 或指定错误码）
- 验证 stdout/stderr 内容是否包含预期关键字
- 验证 TimeoutExpired 后进程是否被正确清理（kill + communicate）
- 验证 OSError 异常后子进程是否已清理

## 回退策略

- 超时回退：增大 timeout 值或拆分为多个子命令
- 管道阻塞回退：使用 communicate() 替代直接 read()
- 权限回退：使用 sudo 或修改文件权限
- 编码回退：指定 encoding='utf-8' 或 errors='ignore'

## 资源召回建议

当以下场景出现时召回本卡片：
- CLI 工具在自动化工作流中执行失败
- 需要根据退出码分类故障类型
- 需要处理 CLI 超时或管道阻塞问题
- 需要设计 CLI 调用的错误恢复策略

## 补充证据（开源文档）

[D1] Python subprocess module documentation, Python Software Foundation, v3.14.7, URL: https://docs.python.org/3/library/subprocess.html (accessed_at: 2026-09-17)

## 证据来源

[1] Python subprocess module documentation, Python Software Foundation, v3.14.7, URL: https://docs.python.org/3/library/subprocess.html
