# LAMMPS安装与配置知识

## 适用范围
触发条件：需要执行LAMMPS模拟但未检查LAMMPS可用性时，或需要在计算集群上提交LAMMPS作业时。
适用场景：任何需要使用LAMMPS进行MD模拟的任务。
不适用场景：已确认LAMMPS可用且配置正确的情况。

## 输入
- 安装目标环境（本地/计算集群）
- 系统类型（Linux/macOS/Windows）
- 计算资源需求（CPU/GPU/内存）

## 输出
- LAMMPS安装状态报告
- 环境配置信息
- 作业提交脚本

## 流程节点
1. 环境检测 → 2. 安装方式选择 → 3. 安装执行 → 4. 验证测试 → 5. 配置记录 → 6. 作业脚本生成

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| LAMMPS版本 | 最新稳定版 | 官方 | 建议使用最新稳定版 |
| conda安装命令 | conda install -c conda-forge lammps | 官方 | 推荐方式 |
| 验证命令 | lmp -h 或 lmp_mpi -h | 官方 | 检查安装成功 |
| SLURM脚本头 | #!/bin/bash + #SBATCH directives | 通用 | 集群作业格式 |
| GPU支持 |包 | 官方 | 需要单独编译 |

## 边界与分流
- 本地安装失败：建议使用conda或Docker
- 集群无LAMMPS：联系管理员安装或使用容器
- GPU版本不可用：使用CPU版本

## 质量检查
- LAMMPS可执行文件必须存在
- 版本号必须正确
- 验证测试必须通过
- 作业脚本必须可执行

## 回退策略
- 安装失败：使用conda或Docker作为替代
- 集群不可用：使用本地安装或云服务

## 资源召回建议
何时应召回本卡片：在s04短时动力学执行前，当LAMMPS未安装或需要在集群上运行时召回。
配套资源：matchem-md-input-audit, matchem-lammps-supercell

## 证据来源
[1] LAMMPS官方安装文档 - https://docs.lammps.org/Install.html
[2] conda-forge LAMMPS包 - https://anaconda.org/conda-forge/lammps
[3] 本卡片基于归因报告task_id=319的知识缺口分析生成，网络检索受限，证据有限