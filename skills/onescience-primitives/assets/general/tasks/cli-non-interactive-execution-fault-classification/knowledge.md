# CLI非交互执行与故障分类

## 适用范围
适用于命令行工具在无人值守环境（CI/CD流水线、自动化脚本、远程调度系统）中的非交互执行场景。当CLI进程需要在沙箱、容器或远程服务器上自动运行，并需要对执行结果进行故障诊断时，本卡片提供退出码语义解析、超时检测、标准错误判读与故障恢复的完整知识框架。

## 输入
- CLI命令字符串及参数列表
- 执行环境配置（工作目录、环境变量、沙箱约束）
- 超时阈值配置
- 预期退出码与标准输出/错误格式

## 输出
- 执行状态分类（成功/失败/超时/异常）
- 退出码语义解析结果
- 标准错误内容摘要
- 故障根因分类与恢复建议
- 诊断证据包（日志、退出码、时间戳）

## 流程节点
1. **环境预检** → 验证CLI工具可用性、权限、依赖项
2. **命令构建** → 组装参数、设置超时、配置沙箱约束
3. **进程启动** → 以非交互模式启动CLI进程
4. **状态监控** → 监控进程状态、捕获退出码、检测超时
5. **输出解析** → 提取标准输出、标准错误、返回码
6. **故障分类** → 根据退出码和错误信息分类故障类型
7. **诊断报告** → 生成结构化诊断结果

每步含：操作、参数、工具、质量门禁

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码语义 | 0=成功, 非0=失败 | [D1] | POSIX标准约定，Python subprocess文档明确说明 |
| 超时检测 | 进程运行时间超过阈值 | [D1] | TimeoutExpired异常在超时时抛出 |
| 标准错误 | 独立于标准输出的错误流 | [D1] | 通过stderr=PIPE捕获 |
| 沙箱约束 | 限制文件系统、网络、进程访问 | [1] | 安全执行环境 |
| 进程终止信号 | SIGTERM→SIGKILL两阶段 | [D1] | 先terminate()后kill() |
| CalledProcessError | 非零退出码时抛出 | [D1] | check=True时触发 |

### 校准数值
以下数值来自典型CLI执行场景，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 典型超时阈值 | 300秒 | 实践经验 | 可根据任务复杂度调整 |
| 退出码范围 | 0-255 | POSIX标准 | 高位被截断，负值表示信号终止 |
| 重试次数 | 3次 | [1] | 指数退避策略 |
| 负退出码含义 | -N表示被信号N终止 | [D1] | POSIX only |

## 边界与分流
- **超时场景**：进程运行超过阈值时，捕获TimeoutExpired异常，调用proc.kill()终止进程，再调用proc.communicate()清理管道
- **非零退出码**：捕获CalledProcessError，记录returncode、cmd、output、stderr属性
- **沙箱拒绝**：权限不足时，记录拒绝原因并建议权限提升方案
- **依赖缺失**：工具未安装或版本不匹配时，记录缺失项并建议安装命令（OSError异常）
- **网络不可达**：远程资源访问失败时，建议离线模式或代理配置
- **Shell模式差异**：shell=True时退出码反映shell本身的退出状态，可能为128+N格式

## 质量检查
- 退出码解析正确性验证
- 标准错误内容完整性检查
- 超时检测准确性验证
- 诊断报告结构完整性检查

## 回退策略
- 降级到交互模式（如适用）
- 使用替代CLI工具
- 手动执行并记录步骤

## 资源召回建议
当遇到以下场景时应召回本卡片：
- CLI工具在自动化流程中执行失败
- 需要诊断CLI退出码含义
- 需要配置CLI超时和重试策略
- 需要构建CLI执行的诊断报告
- Python subprocess调用出现异常

配套资源：
- JSON Schema报告交付契约（用于结构化诊断输出）
- 工作流规划卡（用于编排多步骤CLI执行）

## 补充证据（开源文档/用户自有，可选）
[D1] Python subprocess documentation - Subprocess management, Python Software Foundation, Python 3.14.7, URL: https://docs.python.org/3/library/subprocess.html（accessed_at 2026-09-21，权威文档）

## 证据来源
[1] Testing Error Handling Code With Software Fault Injection and Error-Coverage-Guided Fuzzing, IEEE Transactions on Dependable and Secure Computing, 2024, DOI: 10.1109/tdsc.2023.3288876
[2] Implementing Centralized Error Handling for Software Systems through the Integration of Machine Learning Techniques, Engineering: Open Access, 2023, DOI: 10.33140/eoa.01.01.11
[3] Error-Type–A Novel Set of Software Metrics for Software Fault Prediction, IEEE Access, 2023, DOI: 10.1109/access.2023.3297218
[4] Bumps in the Code: Error Handling During Software Development, IEEE Software, 2021, DOI: 10.1109/ms.2020.3024981
[5] Secure Command Line Solution for Token-based Authentication, EPJ Web of Conferences, 2021, DOI: 10.1051/epjconf/202125102036
