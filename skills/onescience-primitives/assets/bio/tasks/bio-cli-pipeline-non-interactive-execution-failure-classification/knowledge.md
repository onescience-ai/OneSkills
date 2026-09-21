# 生物信息学 CLI 流水线非交互执行与故障分类

## 适用范围
适用于生物信息学分析流水线（Nextflow、Snakemake、Bash 脚本等）在自动化、批处理或远程执行场景下的非交互模式运行，覆盖命令参数解析、认证处理、沙箱执行、超时控制、退出码语义和标准错误判读。不适用于交互式分析环境（如 Jupyter Notebook）或图形界面工具。

## 输入
- 流水线脚本或配置文件（.nf、.smk、.sh）
- 输入数据路径与参数文件
- 执行环境信息（Conda 环境、容器镜像、计算节点配置）
- 认证凭证（如需访问远程数据库或 API）

## 输出
- 标准输出（stdout）：流水线日志与结果摘要
- 标准错误（stderr）：错误诊断信息
- 退出码：0（成功）、非零（失败，具体值按约定分类）
- 日志文件：完整执行记录

## 流程节点

### 1. 环境预检
- 检查依赖工具版本（如 Nextflow ≥ 22.10、Python ≥ 3.8）
- 验证输入文件存在性与格式
- 确认计算资源（CPU、内存、GPU）可用性
- **质量门禁**：预检失败立即退出并返回退出码 2

### 2. 非交互模式启动
- 使用 `--non-interactive` 或 `-batch` 标志禁用交互提示
- 设置环境变量 `BATCH_MODE=1` 或 `NON_INTERACTIVE=1`
- 将 stdin 重定向到 `/dev/null` 或提供空输入
- **质量门禁**：检测到交互提示时记录警告但不阻塞

### 3. 超时控制
- 设置全局超时（如 `timeout 3600s`）
- 设置步骤级超时（如 Nextflow `time '2h'`）
- 超时触发时发送 SIGTERM（优雅终止），等待 30s 后 SIGKILL
- **质量门禁**：超时事件写入日志并返回退出码 124

### 4. 退出码分类
| 退出码 | 含义 | 处理策略 |
|--------|------|----------|
| 0 | 成功完成 | 继续下游分析 |
| 1 | 一般错误 | 检查 stderr，重试或人工干预 |
| 2 | 预检失败 | 修复环境或输入后重试 |
| 124 | 超时 | 增加资源或优化代码 |
| 125 | 资源不足 | 申请更多计算资源 |
| 126 | 权限问题 | 检查文件权限 |
| 127 | 命令未找到 | 检查 PATH 或安装依赖 |
| 130 | 用户中断（Ctrl+C） | 记录状态，支持断点续跑 |

### 5. 标准错误判读
- **致命错误**（Fatal）：立即终止，返回非零退出码
- **警告**（Warning）：记录但继续执行
- **信息**（Info）：正常日志输出
- **调试**（Debug）：详细追踪信息，仅在调试模式启用

### 6. 故障恢复
- 检查点机制：定期保存中间状态
- 断点续跑：从最后成功步骤恢复
- 重试策略：指数退避重试临时性错误（网络、IO）
- **质量门禁**：恢复后验证中间结果完整性

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 退出码语义 | 0=成功, 1-125=错误, 124=超时 | [论文3] | 遵循 POSIX 约定 |
| 超时阈值 | 3600s（全局），7200s（步骤级） | [论文1] | 根据任务规模调整 |
| 重试次数 | 3 次 | [论文4] | 指数退避间隔 1s, 4s, 16s |
| 日志级别 | INFO（默认），DEBUG（调试） | [论文1] | 通过环境变量控制 |

### 校准数值
以下数值来自 PangenePro 和 DeSP 流水线，供量级校准；其他体系需以自身证据重新锚定：
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Nextflow 最低版本 | 22.10 | [论文1] | 支持 DSL2 语法 |
| Python 最低版本 | 3.8 | [论文1] | 类型注解支持 |
| 内存下限 | 8GB | [论文1] | 小型基因组分析 |
| 磁盘空间 | 100GB | [论文3] | DNA 存储模拟 |

## 边界与分流
- **依赖缺失**：返回退出码 127，建议安装缺失工具
- **输入文件损坏**：返回退出码 1，建议重新下载或校验
- **计算资源不足**：返回退出码 125，建议申请更多资源或降低任务规模
- **网络不可用**：返回退出码 1，建议检查网络连接或使用离线模式
- **认证失败**：返回退出码 1，建议刷新凭证或检查权限

## 质量检查
- 预检阶段：验证所有输入文件存在且格式正确
- 执行阶段：监控资源使用（CPU、内存、磁盘）
- 完成阶段：验证输出文件完整性（非空、格式正确）
- 退出码检查：确认退出码与实际执行状态一致

## 回退策略
- 临时性错误：指数退避重试
- 永久性错误：记录详细错误信息，通知人工干预
- 超时：增加资源或优化代码后重试
- 资源不足：降级到更小数据集或简化分析流程

## 资源召回建议
- 当任务需要在 SLURM/HPC 集群上批量执行时召回本卡
- 当流水线需要自动化运行且无需人工干预时召回本卡
- 当需要处理多种退出码和错误场景时召回本卡
- 配套资源：bio-json-schema-report-delivery-contract（报告交付契约）

## 证据来源
[1] PangenePro: an automated pipeline for rapid identification and classification of gene family members, Fatima et al., Bioinformatics Advances, 2024, DOI: 10.1093/bioadv/vbaf159
[2] CoSAG-nf: A Scalable Nextflow Pipeline for Co-assembly, Optimization, and Interactive Visualization of High-Throughput Single-Cell Genomes, Xu & Quan, Bioinformatics, 2026, DOI: 10.1093/bioinformatics/btag671
[3] DeSP: a systematic DNA storage error simulation pipeline, BMC Genomics, 2022, DOI: 10.1186/s12864-022-08459-3
[4] Testing Error Handling Code With Software Fault Injection and Error-Coverage-Guided Test Generation, IEEE Transactions on Dependable and Secure Computing, 2024, DOI: 10.1109/TDSC.2024.3351456
