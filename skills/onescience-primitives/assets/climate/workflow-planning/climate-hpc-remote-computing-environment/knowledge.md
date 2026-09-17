# HPC 远程计算环境连接与预检执行

## 适用范围

**触发条件**：用户需要通过 SSH 连接到远程 HPC 集群执行科学计算任务（如气候数据处理、降尺度计算）。

**适用场景**：
- 在超算中心（如 SCNet、国家超级计算中心）提交计算作业
- 使用 SLURM 作业调度系统管理计算资源
- 执行需要大量计算资源的气候降尺度任务
- 本地环境与远程环境一致性校验

**不适用场景**：
- 本地单机计算（不需要 SSH 连接）
- 云服务器计算（使用不同认证机制）
- 实时交互式计算（应使用 JupyterHub 等）

## 输入

- **SSH 连接参数**：主机地址、端口、用户名、认证方式（密钥/密码）
- **SLURM 配置**：分区(partition)、队列(queue)、资源请求（节点数、GPU/CPU 数量、内存、时间限制）
- **任务脚本**：作业脚本（.sh）或 Python 计算脚本
- **环境依赖**：conda 环境、Python 包、科学计算软件（如 GROMACS、LAMMPS）

## 输出

- **连接状态**：SSH 连接成功/失败状态
- **环境就绪报告**：模块加载状态、软件版本检查、资源可用性
- **作业执行结果**：作业提交状态、运行日志、输出文件

## 流程节点

### 节点 1：SSH 连接建立
- **操作**：使用 SSH 协议连接到远程 HPC 集群
- **关键参数**：
  - 主机地址：如 `login.scnet.cn`
  - 端口：默认 22，或指定端口
  - 认证方式：SSH 密钥（推荐）或密码
  - 连接超时：建议 30-60 秒
- **质量门禁**：连接成功，能执行 `hostname` 命令

### 节点 2：连接超时处理与重试策略
- **操作**：处理连接超时错误，实施重试机制
- **超时原因分析**：
  - 网络延迟或中断
  - 目标主机负载过高
  - 防火墙规则阻止
  - SSH 服务未运行
- **重试策略**：
  - 指数退避（exponential backoff）：初始等待 1s，倍增至 30s [Hanada & Ishibashi, 2024]
  - 最大重试次数：3-5 次
  - 抖动（jitter）：避免重试风暴
- **质量门禁**：重试后连接成功，或明确报告失败原因

### 节点 3：模块加载与环境配置
- **操作**：加载计算所需的软件模块
- **SLURM 模块系统**：
  - `module avail`：查看可用模块
  - `module load <name>`：加载模块
  - `module list`：查看已加载模块
  - `module purge`：清除所有模块（慎用）
- **常见模块**：
  - `gcc`/`intel`：编译器
  - `openmpi`/`mpich`：MPI 库
  - `python`/`anaconda`：Python 环境
  - `netcdf`/`hdf5`：科学数据格式库
- **质量门禁**：所需模块加载成功，版本符合要求

### 节点 4：SLURM 作业提交与管理
- **操作**：使用 SLURM 命令提交和管理计算作业
- **关键命令**：
  - `sbatch <script.sh>`：提交批处理作业
  - `srun <command>`：交互式运行
  - `squeue`：查看作业队列
  - `scancel <jobid>`：取消作业
  - `sinfo`：查看集群状态
- **作业脚本示例**：
  ```bash
  #!/bin/bash
  #SBATCH --job-name=climate_downscaling
  #SBATCH --partition=gpu
  #SBATCH --nodes=1
  #SBATCH --ntasks-per-node=4
  #SBATCH --gres=gpu:1
  #SBATCH --time=24:00:00
  #SBATCH --output=downscaling_%j.out
  #SBATCH --error=downscaling_%j.err
  
  module load python/3.9
  module load netcdf/4.8
  
  python downscaling_script.py
  ```
- **质量门禁**：作业成功提交，状态为 PENDING 或 RUNNING

### 节点 5：本地与远程环境一致性校验
- **操作**：验证本地开发环境与远程计算环境的兼容性
- **校验项目**：
  - Python 版本一致性
  - 关键包版本（如 xarray, netCDF4, dask）
  - 数据格式兼容性（NetCDF4/HDF5）
  - 文件路径格式（Linux vs Windows）
- **校验方法**：
  - 本地导出 `pip freeze > requirements.txt`
  - 远程安装：`pip install -r requirements.txt --dry-run`
  - 比较关键包版本
- **质量门禁**：关键依赖版本匹配，无冲突

### 节点 6：预检执行与就绪性检查
- **操作**：在正式计算前执行预检脚本
- **预检内容**：
  - 磁盘空间检查（`df -h`）
  - 内存可用性（`free -h`）
  - GPU 状态（`nvidia-smi`）
  - 数据文件完整性
  - 网络连接（如需要下载数据）
- **预检脚本示例**：
  ```bash
  #!/bin/bash
  echo "=== 环境预检 ==="
  echo "主机: $(hostname)"
  echo "日期: $(date)"
  echo "Python: $(python --version)"
  echo "已加载模块:"
  module list
  echo "磁盘空间:"
  df -h $HOME
  echo "内存:"
  free -h
  echo "=== 预检完成 ==="
  ```
- **质量门禁**：预检通过，无阻塞性错误

## 关键参数

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| SSH 连接超时 | 30-60 秒 | [Gao et al., 2020] | 平衡连接速度和容错性 |
| 重试最大次数 | 3-5 次 | [Hanada & Ishibashi, 2024] | 避免无限重试 |
| 重试退避策略 | 指数退避 + 抖动 | [Ramaswamy, 2024] | 减少重试风暴 |
| SLURM 作业时间限制 | 根据任务规模 | [Springborg et al., 2023] | 预留缓冲时间 |
| 模块加载顺序 | 编译器 → MPI → 依赖库 | [Fortmann-Grote, 2020] | 确保依赖关系正确 |
| 环境校验频率 | 每次环境变更后 | 最佳实践 | 避免环境漂移 |

## 边界与分流

- **连接失败**：
  - 网络问题：检查本机网络、VPN 连接
  - 认证问题：检查 SSH 密钥、用户名
  - 主机问题：联系 HPC 管理员确认主机状态
- **模块加载失败**：
  - 模块不存在：检查模块名拼写，使用 `module avail` 搜索
  - 版本冲突：尝试加载其他版本，或使用 conda 环境
- **SLURM 作业被拒**：
  - 资源不足：调整资源请求（减少节点数、缩短时间）
  - 分区不可用：检查 `sinfo`，尝试其他分区
  - 配额用尽：联系管理员确认账户配额
- **环境不一致**：
  - 版本差异：使用 conda 环境导出/导入
  - 路径问题：使用相对路径，避免硬编码

## 质量检查

| 检查点 | 阈值 | 失败处理 |
|--------|------|----------|
| SSH 连接成功 | 连接时间 < 60s | 检查网络和认证配置 |
| 模块加载成功率 | 100% | 检查模块名和版本 |
| SLURM 作业提交 | 状态 PENDING/RUNNING | 检查资源请求和队列状态 |
| 环境一致性 | 关键包版本匹配 | 同步环境配置 |
| 预检通过 | 无阻塞错误 | 修复预检发现的问题 |

## 回退策略

1. **SSH 连接完全失败**：使用本地计算模式（如本地 Docker 容器模拟 HPC 环境）
2. **SLURM 不可用**：尝试其他作业调度系统（如 PBS、LSF）或本地批处理
3. **模块加载冲突**：使用 conda 虚拟环境隔离依赖
4. **环境不一致无法解决**：在远程环境重新安装所有依赖

## 资源召回建议

- **召回时机**：执行远程 HPC 计算任务前、遇到连接超时错误时、环境配置问题时
- **配套资源**：
  - `climate-cmip6-statistical-downscaling`：CMIP6 降尺度计算任务
  - `onescience-runtime`：统一运行与诊断技能
  - `onescience-installer`：环境安装与验证技能

## 证据来源

[1] Gao Y, Basney J, Withers A. SciTokens SSH: Token-based Authentication for Remote Login to Scientific Computing Environments. *PEARC '20*, 2020. DOI: 10.1145/3311790.3399613
[2] Springborg AA, Albano M, Xavier-de-Souza S. Automatic Energy-Efficient Job Scheduling in HPC: A Novel SLURM Plugin Approach. *SC-W 2023*, 2023. DOI: 10.1145/3624062.3624265
[3] Schmitz M. Moving to a Multi-cluster HPC Slurm Environment. *JOWOG-34 Plenary*, 2021. DOI: 10.2172/1884078
[4] Hanada H, Ishibashi K. Empirical Study on Request Timeout and Retry for Microservices Communication. *IEEE PRDC 2024*, 2024. DOI: 10.1109/prdc63035.2024.00037
[5] Fortmann-Grote C. Running matlab code on HPC with SLURM. *SciComp Blog*, 2020. DOI: 10.59350/0pps7-f7a86