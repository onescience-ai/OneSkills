# CLI Non-Interactive Execution Failure Classification

## 适用范围

面向科学计算 CLI 工具的非交互式批量调用场景，覆盖归因分析进程、工作流编排脚本和自动化数据处理管道中的命令行工具执行。适用于需要根据退出码、标准错误输出和超时状态对故障进行分类并选择恢复策略的任务。

## 输入

- CLI 命令序列（命令名、参数列表、工作目录）
- 执行环境配置（conda 环境、Python 解释器路径、环境变量）
- 超时阈值（秒）
- 预期退出码（通常为 0 表示成功）

## 输出

- 结构化执行状态：成功 / 非零退出 / 超时 / 未启动
- 故障分类标签与诊断证据（stderr 摘要、退出码、信号编号）
- 建议恢复动作

## 流程节点

1. **进程启动** → 选择 `subprocess.run()` 或 `Popen` 构造器，配置 stdin/stdout/stderr 管道
2. **等待完成** → 设置 `timeout` 参数监控执行时间
3. **状态判定** → 检查 `returncode`：0=成功，负值=信号终止（POSIX），正值=应用错误
4. **故障分类** → 根据退出码、stderr 内容和异常类型归类
5. **恢复决策** → 依据故障类别选择重试、降级或终止

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 0 | 成功 | [D1] subprocess 文档 | 进程正常完成 |
| 退出码 -N | 信号 N 终止 | [D1] subprocess 文档 | POSIX 系统，N 为信号编号 |
| 退出码正值 | 应用错误 | [D1] subprocess 文档 | 具体含义由应用程序定义 |
| timeout 过期 | TimeoutExpired 异常 | [D1] subprocess 文档 | 子进程被终止并重新抛出异常 |
| stderr 非空 | 可能警告或错误 | [D1] subprocess 文档 | 需结合退出码综合判断 |

### 校准数值

以下数值来自 Python subprocess 文档中的示例和规范，供量级校准；其他 CLI 工具需以自身证据重新锚定。

| 场景 | 典型退出码 | 来源 | 说明 |
|------|-----------|------|------|
| shell=True 时 shell 本身未找到 | OSError | [D1] subprocess 文档 | 子进程无法启动 |
| `check=True` 且非零退出 | CalledProcessError | [D1] subprocess 文档 | 包含 returncode、cmd、output 属性 |
| communicate() 超时后 | TimeoutExpired | [D1] subprocess 文档 | 需手动 kill() 后再 communicate() |

## 边界与分流

- **前提：CLI 工具遵循标准退出码约定** → 若工具使用非标准退出码语义（如用 0 表示部分失败），需在调用侧维护退出码映射表，不适用本卡默认分类。
- **前提：执行环境可启动子进程** → 若沙箱或容器环境禁止 subprocess 调用，应转向容器内直接执行或使用任务调度器（如 SLURM sbatch）替代 CLI 调用。
- **前提：stderr 输出可被捕获** → 若工具将关键诊断信息写入文件而非 stderr，需额外配置日志收集通道。

## 质量检查

- 进程启动前验证命令路径存在（`shutil.which()`）
- 执行后检查 returncode 是否在预期范围内
- stderr 中包含 "Error"/"Exception"/"Failed" 关键词时标记为需人工审查
- 超时场景必须确认进程已被终止（`proc.poll()` 返回非 None）

## 回退策略

- 非零退出：解析 stderr 提取错误关键词，尝试修正参数后重试一次
- 超时：增大 timeout 值或拆分为更小的子任务
- 进程未启动：检查 conda 环境、Python 路径和文件权限

## 资源召回建议

当遇到以下场景时召回本卡片：
- CLI 工具执行后返回非零退出码但无明确错误信息
- 归因分析或工作流编排进程超时
- 自动化管道中需要根据退出码分流处理逻辑
- 需要区分信号终止与应用错误

## 补充证据（权威文档）

[D1] Python subprocess — Subprocess management, Python Software Foundation, v3.14.7, https://docs.python.org/3/library/subprocess.html（accessed 2026-09-18，交叉验证：Python 官方文档）

## 证据来源

[1] Python subprocess — Subprocess management, Python Software Foundation, v3.14.7, https://docs.python.org/3/library/subprocess.html
