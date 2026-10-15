# 环境与工具链注意事项（实战沉淀）

> 站点相关常量（分区、module 名、路径、DTK 版本）一律来自运行站点配置，不写死。

## onescience-MACE
- 内置 CLI：
  - `python -m onescience.utils.mace.cli.preprocess_data`（extxyz → HDF5）
  - `python -m onescience.utils.mace.cli.run_train`
  - `python -m onescience.utils.mace.cli.create_lammps_model`
- `DefaultKeys`：`REF_energy` / `REF_forces` / `REF_stress`。**extxyz 必须用这三个键**，
  否则加载器走 `get_potential_energy()` 会得到 `None`，数据集全空。
- `run_train` 默认 `--device cpu`、`--default_dtype float64`；上加速器需显式
  `--device cuda`（DCU 也映射为 cuda）并常改 `float32`。
- 无孤立原子能量时用 `--E0s average`（避免某些版本 `E0s=None` 触发的 `len(None)` 崩溃）。

## torch / DCU
- 报 `libgalaxyhip.so.5: cannot open shared object file` → 未加载 DCU 运行时：
  `module load compiler/dtk/<匹配 torch 的版本>`。
- 报 `libtorch_hip.so: undefined symbol: ncclCommRegister` → dtk/NCCL 与 torch 构建不匹配，
  换与 torch（版本串含 `dtkXXXXX`）一致的 dtk。
- 设备自检：`python -c "import torch; print(torch.cuda.is_available(), torch.cuda.device_count())"`
  应为 `True, >=1`。

## onescience 有两份代码
- 安装副本（`site-packages`）与源码树（如 `~/onescience`）。二者可能不同。
- **训练与导出必须用同一份**，否则模型属性不匹配（例：源码树较新、含 `cp_readout`，
  而权重是旧版训出 → `object has no attribute 'cp_readout'`）。
- 用源码树：`export PYTHONPATH=<onescience 的父目录>`。
- 安装副本可能缺模块（`pyg_stack/core/configuration.py`）导致 `import onescience.utils.mace.data` 失败。

## SLURM / 启动器
- 生产不在登录节点跑；一律 `sbatch`。
- 提交后必须 `squeue`/`sacct` 回读状态；失败很快的作业用 `sacct` 查历史。
- Intel MPI `-configfile`：`-genv …` 必须与首个 `-host … -n 1 <exe>` **同一行**
  （多一个换行 → `no executable specified` / exit 127）。
- 反复 0 秒失败且落同一节点 → 坏节点，用 `--exclude=<node>` 临时规避。
- `Reason=QOSMaxCpuPerUserLimit` → 并发/机时被同账号其它作业占满，等其结束或用
  `--dependency=afterok:<jobid>`。
- 提交前 `sbatch --test-only` 预演；输入一致性用 `check_inputs.py`。

## 计算语义（务必声明）
- 中性（固定电子数）vs 恒电位/隐式溶剂（VASPsol/CP-VASP，`LSOL/LCEP`、`CPM-ion`、变 `N_ele`）。
- 后者用于常规 ML 势会产生系统偏差；spec 的 `electrochemistry.mode` 必须与输入自洽，
  不一致则 S2 守卫 FAIL。
