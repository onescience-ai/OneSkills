# CLI非交互执行与故障分类知识

## 适用范围
本卡片适用于命令行接口（CLI）工具在非交互式环境中的执行故障诊断。当CLI工具在脚本、自动化流程或后台任务中运行时，需要根据退出码和错误模式进行故障分类和恢复。适用于各类CLI工具，包括科学计算工具、数据处理工具、系统管理工具等。

## 输入
- CLI命令执行结果
- 退出码（exit code）
- 标准错误输出（stderr）
- 标准输出（stdout）
- 执行环境信息（shell类型、操作系统）

## 输出
- 故障分类结果
- 错误原因分析
- 恢复策略建议
- 退出码解释

## 流程节点
1. **退出码捕获** → 获取CLI命令的退出码
2. **退出码分类** → 根据退出码范围确定故障类型
3. **错误模式识别** → 分析stderr输出和退出码组合
4. **故障诊断** → 确定具体故障原因
5. **恢复策略生成** → 提供修复或重试建议

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 成功退出码 | 0 | [D1] | 命令执行成功 |
| 通用错误退出码 | 1 | [D1] | 通用错误，如除零、权限问题 |
| Shell内置命令误用 | 2 | [D1] | Bash文档定义的shell内置命令误用 |
| 命令不可执行 | 126 | [D1] | 权限问题或命令不是可执行文件 |
| 命令未找到 | 127 | [D1] | PATH问题或命令拼写错误 |
| 无效退出参数 | 128 | [D1] | exit命令接受0-255范围的整数参数 |
| 致命信号 | 128+n | [D1] | 进程收到信号n后终止 |
| Ctrl+C终止 | 130 | [D1] | 控制信号2（128+2） |
| 退出状态超出范围 | 255 | [D1] | exit命令参数超出0-255范围 |
| 用户自定义退出码范围 | 64-113 | [D1] | 推荐的用户自定义退出码范围（共50个有效码） |

### 校准数值
以下数值来自Linux/Unix系统，供量级校准；其他系统需以自身证据重新锚定。
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码模运算 | 退出码 mod 256 | [D1] | 退出码大于255时取模运算（如exit 3809返回225） |
| Bash/sh退出码 | $?变量 | [D1] | 从Bash或sh提示符获取退出码 |
| C-shell/tcsh差异 | 可能不同 | [D1] | C-shell或tcsh可能返回不同值 |

## 边界与分流
1. **退出码为0** → 命令执行成功，无需故障处理
2. **退出码1-2, 126-165, 255** → 特殊含义退出码，参考标准分类
3. **退出码128+n** → 进程被信号终止，需检查信号类型
4. **退出码64-113** → 用户自定义退出码，需查看具体应用文档
5. **退出码>255** → 执行模256运算后解释
6. **不同shell环境** → 验证shell类型，可能影响退出码解释

## 质量检查
1. 退出码是否在有效范围（0-255）
2. 退出码是否符合标准分类
3. stderr输出是否提供额外错误信息
4. 执行环境是否与预期一致
5. 退出码与错误信息是否匹配

## 回退策略
1. 如果退出码无法解释 → 检查应用特定文档
2. 如果环境差异导致 → 记录环境信息，调整诊断逻辑
3. 如果信号相关 → 检查进程资源限制和信号处理

## 资源召回建议
当遇到以下情况时召回本卡片：
- CLI工具在自动化流程中失败
- 需要根据退出码进行故障诊断
- 脚本中需要处理CLI命令返回值
- 非交互式环境中的错误处理

配套资源：
- general-json-schema-validation-report-contract（用于结构化报告验证）

## 补充证据（开源文档）
[D1] Exit Codes With Special Meanings, The Linux Documentation Project, Advanced Bash-Scripting Guide, URL: https://tldp.org/LDP/abs/html/exitcodes.html（accessed_at: 2026-09-18, 权威文档）
[D2] The GNU C Library - Exit Status, Free Software Foundation, glibc manual 2.44, URL: https://www.gnu.org/software/libc/manual/html_node/Exit-Status.html（accessed_at: 2026-09-18, 权威文档）

## 证据来源
[D1] Exit Codes With Special Meanings, The Linux Documentation Project, Advanced Bash-Scripting Guide
[D2] The GNU C Library - Exit Status, Free Software Foundation, glibc manual 2.44