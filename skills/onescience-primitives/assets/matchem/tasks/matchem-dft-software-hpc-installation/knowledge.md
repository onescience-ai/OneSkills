# DFT软件HPC安装配置

## 适用范围
在HPC环境（超算集群、工作站）中安装配置第一性原理计算软件（VASP、Quantum ESPRESSO），用于材料模拟、催化机理研究、吸附能计算等任务。适用于需要从源代码编译部署DFT软件的场景。

## 输入
- 操作系统：Linux（CentOS、Ubuntu、Rocky Linux等）
- 编译器：Fortran编译器（gcc、intel-oneapi、NVIDIA HPC-SDK、AOCC）
- 数值库：BLAS、LAPACK、ScaLAPACK、FFTW
- MPI实现：OpenMPI、Intel MPI、NVIDIA HPC-SDK内置MPI
- 许可证：VASP需要商业许可证；Quantum ESPRESSO开源免费

## 输出
- 可执行文件：vasp_std、vasp_gam、vasp_ncl（VASP）；pw.x、ph.x等（Quantum ESPRESSO）
- 验证结果：测试套件通过
- 环境配置：PATH、LD_LIBRARY_PATH、模块加载脚本

## 流程节点

### 1. 环境预检
- 检查操作系统版本和架构
- 确认编译器可用性：`which ifort`、`which gfortran`
- 确认数值库安装：`module avail`、`ldconfig -p | grep mkl`

### 2. 下载源代码
- VASP：从VASP Portal下载（需许可证）
- Quantum ESPRESSO：从官网下载或Git克隆

### 3. 准备编译配置
- VASP：复制`arch/makefile.include.*`模板，根据系统调整
- Quantum ESPRESSO：运行`./configure`自动生成make.inc

### 4. 编译
- VASP：`make DEPS=1 -jN std`（标准版本）
- Quantum ESPRESSO：`make all`

### 5. 测试验证
- VASP：`make test`
- Quantum ESPRESSO：`make test`

### 6. 安装部署
- 复制可执行文件到$PATH目录
- 设置环境变量：`ulimit -s unlimited`、`OMP_STACKSIZE=512m`

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Fortran编译器 | Intel oneAPI / GCC / NVIDIA HPC-SDK | [D1] | 需F2008标准支持 |
| BLAS/LAPACK | Intel MKL / OpenBLAS + ScaLAPACK | [D1] | VASP和QE均需要 |
| FFT库 | FFTW3 / Intel MKL | [D1] | 平面波展开必需 |
| MPI实现 | OpenMPI / Intel MPI | [D1] | 并行计算必需 |
| HDF5 | 推荐启用 | [D1] | 大规模I/O支持 |

## 边界与分流

### 编译失败处理
- 内部编译器错误：降低优化级别或更换编译器版本
- 链接错误（symbol not found）：检查库路径和名称匹配
- 共享库找不到：设置LD_LIBRARY_PATH

### 许可证问题
- VASP需要商业许可证，无许可证无法下载源代码
- Quantum ESPRESSO开源免费，可直接下载

### GPU加速配置
- VASP：需要NVIDIA HPC-SDK（>=21.2）或CCE（>=19.0）
- Quantum ESPRESSO：使用OpenACC指令，支持NVIDIA GPU

## 质量检查
1. 编译无错误和警告
2. 测试套件全部通过
3. 示例计算结果与文献一致
4. 并行效率验证（强缩放、弱缩放）

## 回退策略
- 编译失败：检查依赖版本兼容性，尝试不同工具链
- 测试失败：检查输入文件和伪势文件
- 性能不佳：调整并行参数（pool数量、MPI ranks）

## 资源召回建议
- 当任务需要执行DFT计算时召回本卡
- 配套资源：伪势数据库、POSCAR生成工具、结构优化脚本

## 补充证据（开源文档）
[D1] Installing VASP.6.X.X, VASP Software GmbH, 2025-07-20, URL: https://www.vasp.at/wiki/index.php/Installing_VASP.6.X.X（交叉验证）
[D2] Installation - Quantum Espresso, Quantum ESPRESSO Foundation, 2026, URL: https://www.quantum-espresso.org/Doc/installation/（交叉验证）

## 证据来源
[1] Quantum ESPRESSO: One Further Step toward the Exascale, Ivan Carnimeo et al., Journal of Chemical Theory and Computation, 2023, DOI: 10.1021/acs.jctc.3c00249
