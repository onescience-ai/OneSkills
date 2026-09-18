# DFT软件在HPC环境中的安装与配置

## 适用范围
本卡片适用于在高性能计算（HPC）环境中安装和配置密度泛函理论（DFT）软件，包括VASP、Quantum ESPRESSO等第一性原理计算工具。涵盖从依赖库准备、编译器配置、许可证处理到安装验证的完整流程，确保计算环境可用，为电子结构计算、材料模拟等任务提供软件支持。

## 输入
- 安装需求：操作系统类型、HPC集群架构、DFT软件版本
- 环境信息：编译器版本、数学库、MPI库、许可证文件
- 集群信息：模块系统、作业调度器、存储路径

## 输出
- 安装脚本：DFT软件编译命令、环境配置脚本
- 模块文件：Lmod/Tcl模块文件
- 验证报告：安装验证结果、示例计算测试

## 流程节点
1. 安装需求分析 → 2. 依赖库准备 → 3. 许可证配置 → 4. 编译安装 → 5. 环境配置 → 6. 验证测试

## 关键参数
### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 编译器 | Intel/GCC/NVIDIA HPC SDK | [D1][D2] | 需支持F2008标准 |
| 数学库 | MKL/OpenBLAS+FFTW+SCALAPACK | [D1][D2] | 必需依赖 |
| MPI库 | Intel MPI/OpenMPI/MPICH | [D1][D2] | 并行计算必需 |
| 构建系统 | makefile.include/CMake | [D1][D2] | 根据软件选择 |
| 验证方法 | 运行测试套件/示例计算 | [D1][D2] | 确认安装成功 |

### 校准数值
以下数值来自VASP 6.x.x和Quantum ESPRESSO 7.x安装实践，供量级校准；其他体系需以自身证据重新锚定。
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| VASP依赖 | BLAS/LAPACK/ScaLAPACK/FFTW | [D1] | 必需数学库 |
| QE依赖 | BLAS/LAPACK/FFTW/MPI | [D2] | 必需依赖 |
| GPU支持 | NVIDIA HPC SDK ≥21.2 | [D1] | VASP GPU端口 |
| 测试命令 | make test / ctest | [D1][D2] | 验证安装 |

## 边界与分流
- 编译器不兼容：检查编译器版本，使用validated toolchains
- 数学库缺失：安装MKL或OpenBLAS+FFTW组合
- MPI配置错误：确保MPI环境正确设置
- 许可证问题：检查许可证文件路径和有效性
- 内存不足：调整ulimit和OMP_STACKSIZE设置

## 质量检查
- DFT软件必须成功编译
- 测试套件必须通过
- 示例计算必须能运行
- 并行计算必须正常工作
- 模块加载必须成功

## 回退策略
- 编译失败：使用官方预编译版本或conda安装
- 依赖缺失：使用包管理器安装或容器化方案
- 许可证问题：联系软件供应商或使用开源替代（如Quantum ESPRESSO）
- 集群不可用：使用本地计算资源或云HPC服务

## 资源召回建议
当需要执行第一性原理计算任务，且本地未安装DFT软件或需要配置HPC计算环境时，应召回本卡片。配套资源包括伪势库、输入文件生成工具、可视化软件等。

## 补充证据（开源文档/用户自有，可选）
[D1] Installing VASP.6.X.X, VASP, release, URL: https://www.vasp.at/wiki/index.php/Installing_VASP.6.X.X (accessed_at 2026-09-17, 单源参考)
[D2] Quantum ESPRESSO Installation Guide, Quantum ESPRESSO Foundation, release, URL: https://www.quantum-espresso.org/Doc/user_guide/node7.html (accessed_at 2026-09-17, 单源参考)

## 证据来源
[1] VASP官方文档，安装指南，2026年
[2] Quantum ESPRESSO官方文档，用户指南，2026年
[3] 根据归因报告任务323，DFT软件安装配置知识缺失，需要补充