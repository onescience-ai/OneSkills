# CLI 非交互执行与故障诊断

## 适用范围

面向命令行工具的非交互执行场景，提供子进程生命周期管理、退出码分类诊断、超时控制与故障恢复的通用方法框架。适用于自动化脚本、CI/CD 流水线、批量任务调度与远程 SSH 环境中 CLI 工具调用的问题排查。不适用于交互式终端操作或图形界面应用。

## 输入

- 目标 CLI 工具的命令行参数与执行环境配置
- 超时阈值（秒）
- 预期退出码（可选）
- 标准输出/错误捕获需求

## 输出

- 子进程执行结果（CompletedProcess 对象）
- 退出码与异常分类
- 标准输出/错误内容
- 故障诊断报告

## 流程节点

### 1. 子进程启动与参数配置

使用 `subprocess.run()` 或 `Popen()` 启动子进程：

```python
import subprocess
result = subprocess.run(
    ["command", "arg1", "arg2"],
    capture_output=True,
    text=True,
    timeout=30,
    check=False
)
```

**关键参数**：
- `capture_output=True`：捕获 stdout 和 stderr
- `text=True`：以文本模式返回输出
- `timeout=N`：设置超时秒数
- `check=False`：不自动抛出异常

### 2. 退出码分类与诊断

退出码分类规则 [D1]：

| 退出码 | 含义 | 诊断动作 |
|--------|------|----------|
| 0 | 执行成功 | 正常流程 |
| 1-125 | 应用错误 | 检查 stderr 输出，定位具体错误原因 |
| 126 | 命令不可执行 | 检查文件权限 |
| 127 | 命令未找到 | 检查 PATH 环境变量 |
| 128+N | 被信号 N 终止 | 分析信号类型（SIGKILL=9, SIGTERM=15等） |
| 130 | Ctrl+C 中断 (SIGINT) | 正常用户中断 |
| 255 | 退出码溢出 | 检查命令返回值范围 |

### 3. 异常处理与恢复策略

```python
import subprocess

try:
    result = subprocess.run(
        ["command"],
        capture_output=True,
        text=True,
        timeout=30,
        check=True  # 非零退出码抛出 CalledProcessError
    )
except subprocess.TimeoutExpired:
    # 超时处理：杀掉进程并获取已捕获输出
    proc = subprocess.Popen(["command"])
    try:
        stdout, stderr = proc.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
    # 重试或降级处理
except subprocess.CalledProcessError as e:
    # 非零退出码处理
    print(f"Exit code: {e.returncode}")
    print(f"Stderr: {e.stderr}")
except OSError as e:
    # 命令不存在或权限错误
    print(f"OS Error: {e}")
```

### 4. 超时控制最佳实践

[D1] 推荐的超时处理模式：

```python
proc = subprocess.Popen(["command"])
try:
    outs, errs = proc.communicate(timeout=15)
except subprocess.TimeoutExpired:
    proc.kill()  # 强制终止
    outs, errs = proc.communicate()  # 清理管道
# 注意：超时后不应调用 wait()，应再次调用 communicate()
```

### 5. 故障分类决策树

```
执行失败
├── 退出码非零
│   ├── 1-125: 应用错误 → 检查 stderr
│   ├── 126: 权限错误 → 检查文件权限
│   ├── 127: 命令未找到 → 检查 PATH
│   ├── 128+N: 信号终止 → 分析信号类型
│   └── 其他: 自定义错误码 → 参考工具文档
├── 超时异常
│   ├── 超时后进程仍在运行 → kill + communicate
│   └── 超时后进程已退出 → 检查退出码
└── 系统异常
    ├── OSError: 文件不存在或权限不足
    └── ValueError: 参数无效
```

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| capture_output | True | [D1] | 捕获 stdout 和 stderr |
| text | True | [D1] | 文本模式输出 |
| timeout | 30s（默认） | [D1] | 防止无限挂起 |
| check | False/True | [D1] | 是否自动抛出异常 |

### 退出码阈值

| 退出码范围 | 语义 | 来源 |
|------------|------|------|
| 0 | 成功 | [D1] |
| 1-125 | 应用错误 | [D1] |
| 126 | 权限错误 | [D1] |
| 127 | 命令未找到 | [D1] |
| 128+N | 信号终止 | [D1] |

## 边界与分流

- **超时场景**：超时后必须先 kill 进程再 communicate，否则管道可能死锁
- **Windows 平台差异**：Windows 不支持 POSIX 信号，kill() 等同于 terminate()
- **shell=True 风险**：使用 shell=True 时需确保命令字符串安全，防止注入攻击
- **编码问题**：非 UTF-8 输出需指定 encoding 参数或使用二进制模式

## 质量检查

- 退出码是否在预期范围内
- stderr 是否包含错误信息
- 是否发生超时异常
- 输出内容是否符合预期格式

## 回退策略

1. 超时失败：增加超时阈值或优化命令性能
2. 退出码异常：检查命令参数与环境配置
3. 权限错误：以适当权限重试或请求权限提升
4. 命令不存在：检查 PATH 或使用绝对路径

## 资源召回建议

当遇到以下场景时召回本卡片：
- CLI 工具执行超时或挂起
- 退出码异常需要诊断
- 自动化脚本中的进程管理
- CI/CD 流水线中的命令执行失败

配套资源：
- general-json-schema-report-contract-validation：JSON 报告格式验证

## 证据来源

[D1] Python Software Foundation. "subprocess — Subprocess management". Python 3.14.7 Documentation. https://docs.python.org/3/library/subprocess.html (accessed 2026-09-17)
