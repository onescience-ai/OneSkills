# DFT软件HPC安装配置（VASP/Quantum ESPRESSO）

## 适用范围

面向在高性能计算（HPC）环境中部署密度泛函理论（DFT）计算软件的需求，提供VASP和Quantum ESPRESSO的完整安装配置指南。适用于需要进行第一性原理计算、材料电子结构分析、吸附能计算、反应路径研究等计算材料科学任务的场景。

**适用场景**：
- 在HPC集群上安装VASP或Quantum ESPRESSO
- 配置DFT软件的编译环境和依赖库
- 设置模块加载和作业提交脚本
- 验证DFT软件安装是否成功

**不适用场景**：
- 仅需使用预装DFT软件的环境（直接加载模块即可）
- 进行DFT计算的具体操作指南（那是另一类知识）
- 分子动力学软件（如LAMMPS、GROMACS）的安装

## 输入

**输入数据**：
- HPC集群访问权限和编译环境
- 操作系统信息（Linux发行版、内核版本）
- 已安装的编译器（GCC、Intel oneAPI、AOCC等）
- 已安装的数学库（Intel MKL、OpenBLAS、FFTW等）

**来源**：
- 系统管理员提供的集群配置信息
- DFT软件官方文档

## 输出

**输出产物**：
- 可执行的DFT软件二进制文件
- 模块加载脚本
- 验证计算结果

**验证标准**：
- 软件版本信息正确输出
- 示例计算正常完成
- 计算结果与文献值一致

## 流程节点

### 步骤1：环境检查

**操作**：检查HPC集群的编译环境和依赖库

**检查项**：
- 编译器版本（GCC ≥ 7.0，Intel oneAPI ≥ 2021.0）
- 数学库（Intel MKL、OpenBLAS、FFTW3）
- MPI实现（OpenMPI、MPICH、Intel MPI）
- 磁盘空间（≥ 10 GB）
- 内存（≥ 16 GB）

**工具**：`module list`、`mpif90 --version`、`ldconfig -p | grep mkl`

**质量门禁**：所有依赖库版本满足DFT软件要求

### 步骤2：VASP安装配置

**操作**：编译安装VASP

**前置条件**：
- 获得VASP商业许可证（需向VASP公司申请）
- 下载VASP源代码包（vasp.x.x.tar.gz）

**编译步骤**：
```bash
# 1. 解压源代码
tar -xzf vasp.6.x.tar.gz
cd vasp.6.x

# 2. 配置makefile.include
cp arch/makefile.include.linux_intel makefile.include

# 3. 编辑makefile.include，配置编译器和库路径
# 关键配置项：
# - FC = ifort 或 mpif90
# - FFLAGS = -O2 -free
# - BLAS = -lmkl_intel_lp64 -lmkl_sequential -lmkl_core
# - LAPACK = -lmkl_intel_lp64
# - FFTW = -lmkl_intel_lp64

# 4. 编译
make all

# 5. 验证
bin/vasp_std --version
```

**关键参数**：
| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 截断能 | 400-600 eV | 取决于体系，平面波基组 |
| K点网格 | 根据体系大小 | Monkhorst-Pack网格 |
| 电子步收敛 | 1E-6 eV | 电荷密度收敛标准 |
| 离子步收敛 | 0.01-0.03 eV/Å | 力收敛标准 |

**质量门禁**：`vasp_std --version` 正确输出版本信息

### 步骤3：Quantum ESPRESSO安装配置

**操作**：编译安装Quantum ESPRESSO

**前置条件**：
- Quantum ESPRESSO为开源软件，无需许可证
- 下载源代码（qe-x.x.tar.gz）

**编译步骤**：
```bash
# 1. 解压源代码
tar -xzf qe-7.2.tar.gz
cd qe-7.2

# 2. 配置
./configure --with-scalapack --with-fftw=/path/to/fftw

# 3. 编译
make all

# 4. 验证
bin/pw.x --version
```

**关键参数**：
| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 平面波截断 | 30-50 Ry | 取决于体系 |
| 关联泛函 | PBE/PBEsol | 根据研究需求 |
| 溶剂模型 | 隐式溶剂 | 电化学体系 |

**质量门禁**：`pw.x --version` 正确输出版本信息

### 步骤4：环境配置与验证

**操作**：配置模块加载和作业脚本

**模块加载脚本示例**（`/etc/modulefiles/vasp/6.4.1`）：
```tcl
#%Module1.0
proc ModulesHelp { } {
    puts stderr "VASP 6.4.1 - Vienna Ab initio Simulation Package"
}

module-whatis "VASP 6.4.1"

setenv VASP_HOME /opt/apps/vasp/6.4.1
prepend-path PATH $VASP_HOME/bin
prepend-path LD_LIBRARY_PATH $VASP_HOME/lib
```

**作业脚本示例**（SLURM）：
```bash
#!/bin/bash
#SBATCH --job-name=vasp_test
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32
#SBATCH --time=01:00:00

module load vasp/6.4.1
mpirun vasp_std < POSCAR > stdout
```

**验证计算**：
1. 运行Si晶体结构优化
2. 检查CONTCAR中晶格常数（实验值5.43 Å）
3. 检查OUTCAR中总能量收敛

**质量门禁**：
- 晶格常数误差 < 2%
- 总能量收敛到 1E-6 eV

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 平面波截断能 | 400 eV | [论文2] | CuSn体系DFT计算 |
| 交换关联泛函 | PBE | [论文2] | 通用选择 |
| k点网格 | 5×5×1 | [论文2] | 表面计算 |
| 力收敛标准 | 0.03 eV/Å | [论文2] | 几何优化 |
| 真空层厚度 | 15 Å | [论文2] | 表面模型 |
| PAW赝势 | VASP内置 | [论文2] | 离子-电子相互作用 |

## 边界与分流

**许可证限制**：
- VASP需要商业许可证，获取周期约2-4周
- 无许可证时使用Quantum ESPRESSO作为替代

**硬件限制**：
- 内存不足时减小超胞尺寸或K点密度
- 磁盘空间不足时清理中间文件

**编译失败处理**：
- 检查依赖库路径是否正确
- 确认编译器版本兼容性
- 查看编译日志中的错误信息

## 质量检查

| 检查点 | 验证方法 | 阈值 | 失败处理 |
|--------|----------|------|----------|
| 版本输出 | `--version` | 正确输出 | 重新编译 |
| 示例计算 | Si结构优化 | 晶格常数5.43±0.1 Å | 检查输入参数 |
| 能量收敛 | 电子步迭代 | < 1E-6 eV | 增加迭代步数 |
| 力收敛 | 离子步迭代 | < 0.03 eV/Å | 检查POTCAR |

## 回退策略

- VASP安装失败时切换到Quantum ESPRESSO
- 编译环境不满足时请求系统管理员协助
- 许可证未到位时使用开源替代方案

## 资源召回建议

**何时召回本卡片**：
- 任务需要进行DFT计算但环境未配置
- installer技能报告DFT软件不在支持列表中
- 需要验证DFT软件安装是否正确

**配套资源**：
- matchem-vasp-dft-workflow：VASP DFT计算工作流
- matchem-vasp-slurm-job-submission：VASP SLURM作业提交
- matchem-phonon-calculation-vasp-validation：VASP声子计算验证

## 补充证据（权威文档）

[D1] VASP Wiki - Getting Started, University of Vienna, current, URL: https://www.vasp.at/wiki/index.php/Getting_started（accessed_at 2026-09-16，官方安装指南）
[D2] Quantum ESPRESSO Documentation, Quantum ESPRESSO Team, current, URL: https://www.quantum-espresso.org/Doc/（accessed_at 2026-09-16，官方文档）

## 证据来源

[论文2] Engineering Surface Oxophilicity of Copper for Electrochemical CO2 Reduction to Ethanol, Li M et al., Advanced Science, 2023, DOI: 10.1002/advs.202204579（DFT计算参数和VASP配置）
