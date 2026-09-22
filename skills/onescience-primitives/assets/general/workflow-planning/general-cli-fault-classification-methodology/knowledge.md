# 命令行界面(CLI)故障分类方法论

## 适用范围
本卡片为CLI程序提供非交互执行与故障分类的方法论框架，适用于任何需要通过命令行接口执行的程序、脚本或工具。涵盖故障检测、分类、诊断和恢复的完整流程。不适用于图形用户界面(GUI)程序或交互式终端会话。

## 输入
- CLI程序或脚本的执行命令
- 执行环境信息（操作系统、依赖版本、环境变量）
- 输入参数和配置文件
- 历史执行日志（如有）

## 输出
- 结构化的故障分类报告（包含退出码、错误类型、影响范围）
- 故障根因分析（基于日志和状态信息）
- 恢复建议和修复策略
- 可复用的故障模式库

## 流程节点
1. **执行监控** → 记录命令启动、执行过程和终止状态
2. **退出码解析** → 分类退出码（0成功、1通用错误、2误用、信号终止码等）
3. **日志收集** → 捕获标准输出、标准错误和环境快照
4. **故障分类** → 按原因分类（环境错误、输入错误、资源错误、逻辑错误）
5. **根因分析** → 关联退出码、日志内容和执行上下文
6. **恢复策略** → 生成修复建议和重试策略

## 关键参数
### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码分类 | 0=成功, 1-2=应用错误, 3-125=用户错误, 126-125=执行错误, 128+=信号终止 | [通用] | 基于Unix/Linux标准退出码约定 |
| 故障分类维度 | 环境、输入、资源、逻辑 | [1] | 从Slurm集群监控中提取的故障分类框架 |
| 日志保留策略 | 执行前、执行中、执行后三阶段 | [2] | LLM代理调试中的日志收集最佳实践 |

### 校准数值
以下数值来自实际系统监控场景，供量级校准；其他系统需以自身证据重新锚定：
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码阈值 | 128+信号号 | [通用] | 如130=128+2(SIGINT) |
| 日志缓冲区大小 | 1MB | [1] | Slurm集群监控的典型日志大小 |
| 故障检测延迟 | <100ms | [1] | 实时监控系统的响应时间要求 |

## 边界与分流
- **环境不匹配**：转向环境检测和依赖验证流程
- **输入验证失败**：转向参数解析和输入格式检查
- **资源不可用**：转向资源调度和等待重试策略
- **逻辑错误**：转向代码审查和单元测试验证
- **信号终止**：转向信号处理和优雅关闭机制

## 质量检查
- 退出码分类准确率 > 95%
- 故障根因定位成功率 > 80%
- 恢复建议可执行性验证
- 故障模式库覆盖率评估

## 回退策略
- 当退出码非标准时，回退到日志内容分析
- 当日志不完整时，回退到环境状态检查
- 当无法自动诊断时，生成人工干预指南

## 资源召回建议
- 当遇到具体领域CLI工具故障时，召回相关领域task卡片
- 当需要实时监控时，召回相关tool或component卡片
- 当涉及分布式系统时，召回workflow卡片

## 补充证据（开源文档）
[D1] Python argparse documentation: exit_on_error parameter, Python 3.14.7, https://docs.python.org/3/library/argparse.html#exit-on-error（accessed_at 2026-09-21，交叉验证：官方Python文档）
[D2] Python argparse documentation: error handling and exit codes, Python 3.14.7, https://docs.python.org/3/library/argparse.html#exit-on-error（accessed_at 2026-09-21，交叉验证：官方Python文档）
[D3] Python argparse documentation: suggest_on_error parameter, Python 3.14.7, https://docs.python.org/3/library/argparse.html#suggest-on-error（accessed_at 2026-09-21，交叉验证：官方Python文档）

## 证据来源
[1] Conclave: A Unified Platform for Real-Time Slurm Cluster Data Monitoring, Dymko & Robila, ICDMW 2025, DOI: 10.1109/ICDMW69685.2025.00210
[2] Understanding Agent-Reactive Bugs at the Model-Harness Boundary, Chen et al., arXiv 2026, DOI: 10.48550/arXiv.2607.15684
[3] Leveraging Large Language Models for Automated Test Results Analysis, Akhoondi & Sharbaf, ICWR 2026, DOI: 10.1109/ICWR69602.2026.11513366