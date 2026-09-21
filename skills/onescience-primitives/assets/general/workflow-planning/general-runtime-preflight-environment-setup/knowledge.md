# GPU 加速推理任务的运行前环境预检工作流

## 适用范围

面向需要 GPU 加速的深度学习推理或训练任务，在正式执行前完成环境就绪验证。核心流程为 discover→preflight→execute→diagnose 四步闭环，preflight 阶段必须在 execute 之前完成，产出 environment_readiness 和 preflight_passed 指标后方可进入执行阶段。适用于基因组学深度学习模型推理、分子动力学模拟、大规模数据分析等计算密集型科研场景。

## 输入

| 输入 | 格式 | 说明 |
|------|------|------|
| onescience.json | JSON 配置 | 项目级运行配置（含 execution_profile） |
| 任务需求 | 自然语言描述 | 需要的硬件/软件/数据资源 |
| 远程站点配置 | SSH/SLURM 信息 | 如需远程执行 |

## 输出

| 输出 | 格式 | 说明 |
|------|------|------|
| preflight_passed | boolean | 环境是否就绪 |
| execution_readiness | string | ready / blocked / degraded |
| environment_report | JSON | 详细的检测结果 |
| preflight-evidence.json | JSON | 预检证据记录 |

## 流程节点

### Step 1：Discover — 读取配置
- **操作**：读取 onescience.json 获取 execution_profile 和运行站点配置
- **参数**：execution_profile 三元组（execution_mode, compute_type, runtime_env）
- **工具**：onescience-runtime discover 步骤
- **质量门禁**：配置文件存在且格式正确

### Step 2：Preflight — 环境预检
- **操作**：委托 onescience-installer 执行环境就绪检测
- **子步骤**：
  - 2a. GPU 可用性检测（nvidia-smi、CUDA 版本）
  - 2b. 软件依赖检查（JAX 版本≥0.4、Haiku、Orbax）
  - 2c. Checkpoint 存在性和完整性验证
  - 2d. Conda 环境状态检查
  - 2e. 运行站点连接验证（如需远程）
- **工具**：onescience-installer 环境预检能力
- **质量门禁**：preflight_passed=true、evidence.preflight.status=passed

### Step 3：Execute — 执行任务
- **操作**：在 preflight 通过后执行实际计算任务
- **参数**：任务脚本、输入数据、输出路径
- **工具**：onescience-runtime execute 步骤
- **质量门禁**：任务完成、输出产物存在

### Step 4：Diagnose — 诊断与恢复
- **操作**：若执行失败，诊断原因并尝试恢复
- **参数**：错误类型、环境限制、资源不足
- **工具**：onescience-runtime diagnose 步骤
- **质量门禁**：诊断报告生成、恢复路径明确

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| preflight 必须先于 execute | true | [1] | 闭环流程硬约束 |
| GPU 检测工具 | nvidia-smi / jax.devices() | [1] | 硬件可用性验证 |
| JAX 最低版本 | >= 0.4 | [1] | 框架兼容性要求 |
| CUDA 最低版本 | >= 12.0 | [1] | GPU 加速支持 |
| Checkpoint 验证 | 文件存在 + 参数加载 | [1] | 模型可用性 |
| Conda 环境 | 激活状态 + 包版本 | [1] | 依赖隔离 |

### AlphaGenome 任务校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| GPU 最低配置 | 1× NVIDIA H100 或等效 | [1] | 单次推理 <1s |
| 训练配置 | 8× TPU v3 或 8× GPU | [1] | 序列并行 |
| 内存需求 | ≥ 32 GB GPU 内存 | [1] | 1 Mb 序列处理 |
| Checkpoint 格式 | Orbax | [1] | JAX 模型保存格式 |
| Organism 注释文件 | FASTA + GTF + PAS + splice_site | [1] | 物种配置完整性 |

## 边界与分流

- **preflight 失败（GPU 不可用）**：委托 onescience-runsite 申请 SLURM GPU 计算节点
- **preflight 失败（Checkpoint 缺失）**：从 OneScience datasets 或 ModelScope 下载
- **preflight 失败（依赖不满足）**：委托 onescience-installer 安装或修复
- **远程站点不可达**：检查 SSH 配置、网络连接、VPN 状态
- **所有恢复路径失败**：标记 BLOCKED，输出恢复指南

## 质量检查

| 检查项 | 阈值 | 失败处理 |
|--------|------|----------|
| preflight_passed | true | 不得进入 execute |
| GPU 设备数 | ≥ 1 | 申请计算节点 |
| JAX 版本 | ≥ 0.4 | 安装/升级 |
| Checkpoint 加载 | 无错误 | 重新下载 |
| Conda 环境 | 激活且依赖完整 | 安装缺失包 |

## 回退策略

- 本地 GPU 不可用 → SLURM 计算节点申请
- Checkpoint 下载失败 → 公共镜像或备用路径
- 依赖安装失败 → 指定版本或使用容器化环境
- 所有回退失败 → 标记 BLOCKED 并输出详细恢复指南

## 资源召回建议

- 当任务涉及 GPU 加速计算时召回本卡
- 配套资源：onescience-installer（环境安装）、onescience-runsite（站点配置）

## 补充证据（开源文档）

[D1] OneScience Runtime SKILL.md, OneScience, current, internal://skills/onescience-runtime/SKILL.md（闭环流程规范）
[D2] OneScience Installer SKILL.md, OneScience, current, internal://skills/onescience-installer/SKILL.md（环境预检能力）

## 证据来源

[1] "Advancing regulatory variant effect prediction with AlphaGenome", Avsec et al., Nature, 2026, DOI: 10.1038/s41586-025-10014-0
