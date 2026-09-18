# DFT计算工具调用任务

## 适用范围
适用于DFT计算工具的调用，包括VASP、Gaussian、CP2K的接口和脚本，计算资源申请流程。

## 输入
- 计算任务类型（结构优化、单点能、态密度）
- 输入文件（POSCAR、Gaussian输入文件）
- 计算资源（HPC集群、GPU）

## 输出
- 计算脚本（VASP输入文件、Gaussian脚本）
- 计算日志（收敛性、计算时间）
- 输出文件（OUTCAR、LOG文件）

## 操作步骤
1. 准备输入文件（POSCAR、INCAR、KPOINTS）
2. 申请计算资源（HPC作业提交）
3. 提交计算任务（sbatch、qsub）
4. 监控计算进度（tail -f stdout）
5. 收集输出文件（OUTCAR、DOSCAR）
6. 分析计算结果（吸附能、电子结构）

## 输出产物
- `vasp_input/`：VASP输入文件目录
- `gaussian_input/`：Gaussian输入文件目录
- `calculation_log.md`：计算日志
- `output_files/`：输出文件目录

## 质量门禁
- 验证输入文件格式正确
- 检查计算收敛性（能量变化<1e-4 eV）
- 确认计算资源充足

## 回退策略
- 若计算失败，检查输入文件和参数
- 若资源不足，申请更多资源或使用本地计算
- 若收敛困难，调整收敛标准或计算参数

## 资源召回建议
- 当需要VASP计算脚本时召回本任务
- 当需要Gaussian计算接口时召回本任务
- 当需要HPC作业提交方法时召回本任务

## 证据来源
[1] Construction of 1D perovskite nanowires by Urotropin passivation towards efficient and stable perovskite solar cell, Zardari et al., Solar Energy Materials and Solar Cells, 2021, DOI: 10.1016/j.solmat.2021.111119