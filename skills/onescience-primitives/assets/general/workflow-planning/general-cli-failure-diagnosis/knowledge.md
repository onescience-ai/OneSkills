# CLI工具执行失败诊断与故障分类

## 适用范围

面向命令行工具（CLI）在自动化工作流中执行失败的场景，提供退出码解读、标准错误分析和故障恢复策略。适用于各类CLI工具的非交互执行模式故障排查，包括但不限于Python脚本、Node.js工具、Shell脚本等。

## 输入

- CLI工具的退出码（exit code）
- 标准错误输出（stderr）
- 执行环境信息（操作系统、Python版本等）
- 工具配置参数

## 输出

- 故障类型分类（成功/失败/异常）
- 错误原因定位
- 恢复建议与修复策略

## 流程节点

1. **捕获退出码** → 获取CLI工具的退出状态
2. **分类退出码** → 按退出码含义进行故障分类
3. **分析标准错误** → 解读stderr输出的错误信息
4. **诊断根因** → 定位具体故障原因
5. **制定恢复策略** → 提供修复建议

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码 0 | 成功 | [D1] | 通常表示工具正常执行完成 |
| 退出码 1 | 通用错误 | [D1] | 未明确分类的错误 |
| 退出码 2 | 命令行用法错误 | [D1] | 参数错误或用法不当 |
| 退出码 126 | 权限问题 | [D1] | 文件不可执行或权限不足 |
| 退出码 127 | 命令未找到 | [D1] | 执行路径错误或依赖缺失 |
| 退出码 128+ | 信号终止 | [D1] | 进程被信号终止，退出码=128+信号编号 |
| 退出码 130 | 用户中断 | [D1] | Ctrl+C (SIGINT) |
| 退出码 137 | 强制终止 | [D1] | SIGKILL (通常因资源不足) |
| 退出码 143 | 正常终止 | [D1] | SIGTERM (优雅终止) |

### 校准数值（Python sys.exit特有）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| sys.exit(None) | 等价于exit(0) | [D1] | 表示成功退出 |
| sys.exit(字符串) | 打印到stderr，exit(1) | [D1] | 快速错误退出方式 |
| sys.exit(整数) | 指定退出码 | [D1] | 0=成功，非0=失败 |

**注：以下数值来自Python标准库，供量级校准；其他CLI工具需以自身文档重新锚定。**

## 边界与分流

- **退出码为0**：工具执行成功，无需进一步诊断
- **退出码为1-125**：应用程序级错误，需分析stderr获取具体原因
- **退出码为126-127**：系统级问题（权限、路径），需检查环境配置
- **退出码为128-255**：信号相关问题，需检查进程终止原因
- **退出码为120**：Python清理过程出错（缓冲区刷新失败）

## 质量检查

- 验证退出码是否在预期范围内（0-255）
- 检查stderr输出是否包含关键错误信息
- 确认工具配置是否正确
- 验证依赖项是否完整安装

## 回退策略

- 退出码异常时，尝试使用--help或-h参数获取用法说明
- 权限问题时，检查文件权限和执行权限
- 依赖缺失时，安装所需依赖包
- 环境问题时，检查PATH和环境变量配置

## 资源召回建议

本卡片适用于：
- 自动化工作流中CLI工具执行失败
- CI/CD管道中的工具执行问题
- 批处理脚本中的错误诊断
- Python脚本的进程退出码分析

配套资源：
- general-json-schema-report-contract（JSON Schema报告契约）

## 补充证据（开源文档）

[D1] Python sys.exit() Documentation, Python Software Foundation, v3.14.7, URL: https://docs.python.org/3/library/sys.html#sys.exit (accessed_at: 2026-09-17, 官方权威来源)
[D2] Linux System Exit Codes, The Linux Documentation Project, 2024, URL: https://tldp.org/LDP/abs/html/exitcodes.html (accessed_at: 2026-09-17, 交叉验证)

## 证据来源

[1] Python Software Foundation. "sys — System-specific parameters and functions". Python 3.14.7 Documentation. https://docs.python.org/3/library/sys.html
[2] The Linux Documentation Project. "Exit Codes With Special Meanings". Advanced Bash-Scripting Guide. https://tldp.org/LDP/abs/html/exitcodes.html
