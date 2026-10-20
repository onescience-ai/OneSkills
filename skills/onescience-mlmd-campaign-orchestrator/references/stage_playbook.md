# 阶段手册（自包含）：每一步怎么做、门限、停放点

命名固定，上游交付即下游输入。任一阶段 FAIL → 停在该阶段报告，不进下一阶段。
所有交付都过“契约 + 硬门限 + sha256 绑定”。

## S0 需求归一化 + 站点解析

- 把用户一句话填进 `assets/campaign_spec.example.json` → `campaign_spec.json`。
- 关键项与用户确认：中性/恒电位、固定层、切分策略与块大小、验收门限、时长。
- 站点：从 `onescience.json`（`runtime.ssh`/`partition`/`module`/`remote_work_dir`）读取；
  缺失先补（runsite）。探测命令：
  ```bash
  ssh <alias> "sinfo -o '%20P %a %10l %6D %6c %8m %12G'; module avail 2>&1 | head; which vasp_std"
  ```
- 停放点：spec 或站点未确认 → ask_user。

## S1 DFT 结构优化

**建初始模型**（`scripts/build_interface_example.py` 为参考实现）：
1. fcc(111) slab：`a∥=a/√2`、层间距 `a/√3`、ABC 偏移 `(a1+a2)/3`；bottom N 层 `F F F`。
2. 吸附物高度由 `mode` 决定（physisorbed ≥ 0.90·(r_vdw 和)）。
3. 溶剂层：全局供体-受体匹配 + 取向搜索（**不要**逐分子投最近邻）；层间距=层间距离；
   分子数由 `N=A·ρ·t` 反算。
4. 离子：造 4–6 个配位 O（K⁺–O≈2.8 Å）；冲突判据一律用**周期最小镜像**。
5. 真空 = z_max(含外侧 H) + 目标（15–20 Å）。

**跑松弛**（`assets/submit.vasp.example.slurm` + `assets/INCAR.relax.example`）。

**门限**（由兄弟技能 `onescience-dft-model-gate` 承接）：
```bash
python3 .opencode/skills/onescience-dft-model-gate/scripts/check_geometry.py \
        structures/POSCAR --contract model_contract.json --json /tmp/gate.json
python3 .opencode/skills/onescience-dft-model-gate/scripts/check_vasp_inputs.py \
        --poscar structures/POSCAR --delivery-dir structures
```
若 I11 报 FAIL（缺 `view.html`），先调 structure-viewer 出图再重跑门限：
```bash
python3 .opencode/skills/onescience-structure-viewer/scripts/render_structure.py \
        structures/POSCAR --contract model_contract.json --outdir structures
```
门限全 PASS 后**原样贴输出 + sha256 到报告**。
- 力收敛：可动原子最大力 ≤ `|EDIFFG|`（读 `OUTCAR` 的 `TOTAL-FORCE` 末块）。
- 交付：`POSCAR`（Selective dynamics）、`CONTCAR`、契约、门限原始输出、**`view.html`**。

## S2 AIMD 出轨迹（**中性**）

1. `INCAR`：在 S1 电子结构基础上叠加 MD（见 `assets/INCAR.nvt.example`）。
2. **速度初始化检查**（见 `references/velocity_block_pitfall.md`）：截断起始 `POSCAR` 的全零速度块。
3. 提交并监控（`assets/submit.vasp.example.slurm`）。

**门限（全满足）**：
- **中性守卫**：`INCAR/OUTCAR` 无 `LSOL/LCEP`、无 `CPM-ion`；否则与 `mode=neutral` 矛盾 → FAIL。
- 温度稳定（去瞬态后围绕目标波动）；电子步收敛；`I REFUSE TO CONTINUE` 计数 0。
- 交付：`INCAR`、`vasprun.xml`、`XDATCAR`、`OSZICAR`、健康判定。

## S3 轨迹 → 数据集（时间块切分）

```bash
python scripts/probe_traj.py <aimd_dir>/vasprun.xml
python scripts/vasp2mace_dataset.py --traj <aimd_dir>/vasprun.xml --out-dir <ds_dir> \
    --prefix aimd --split-policy time-block --block-frames 100
python scripts/validate_dataset.py --prefix aimd --out-dir <ds_dir>
```
产出 `aimd_train/valid/test.extxyz` + `aimd_meta.json`（键 `REF_energy/REF_forces/REF_stress`）。

**门限**：键为真值（非 None）、计数一致、**切分=time-block 且 shuffle=false**（见 `split_policy.md`）；
可选：被冻结原子 mask。交付含三集合帧区间。

## S4 训练 MACE

```bash
# 用 assets/submit.mace.example.slurm 提交（DCU/GPU 单卡）
python -m onescience.utils.mace.cli.run_train --name <name> \
  --train_file aimd_train.extxyz --valid_file aimd_valid.extxyz \
  --E0s average --device cuda --default_dtype float32 \
  --r_max 6.0 --num_interactions 2 --hidden_irreps "128x0e + 128x1o" \
  --batch_size 2 --max_num_epochs 500 --forces_weight 1000 --energy_weight 10 --seed 2026
```
**门限**：验证集力 RMSE ≤ `train.acceptance.forces_rmse_meV_per_A`（默认 10 meV/Å）；
同时报 `RMSE_E/atom`。不达标 → 停并报告（见 `acceptance.md`），不擅自改。

**图表**：训练曲线（loss / energy RMSE / force RMSE vs epoch）出图后，**必须**用
`onescience-structure-viewer` 的 `render_chart.py mace_training.png --outdir <交付目录>`
包成同名 HTML 再交付（OneCode 只渲染 HTML，裸 PNG 会被 I12 拦下）。

## S5 导出 LAMMPS

```bash
bash scripts/create_lammps_model.example.sh <model_dir>/<name>_stagetwo.model libtorch
```
**门限**：`*-lammps.pt` 可 `jit.load`；元素顺序 = `export.elements`；**导出代码 == 训练代码**
（否则 `cp_readout` 之类属性不匹配）。

## S6 长时 MD（LAMMPS）

```
pair_style mace no_domain_decomposition
pair_coeff  * * /abs/path/mace_<system>_lammps.pt H C O K Cu
```
**门限（建议）**：先 `run 0`/数百步确认能量守恒量级，再放长到目标 ns；
记录长轨迹与分析埋点（用于比 AIMD ps 级与 MLMD ns 级的界面动力学）。

**图表**：能量/温度随时间演化曲线出图后，同样用 `render_chart.py md_energy_temp.png
--outdir <交付目录>` 包成同名 HTML 交付；不要只交裸 PNG，也不要因"界面不支持图片"而放弃出图。

## 贯穿要求

- **可视化一律出 HTML**：OneCode 平台只渲染 HTML，不渲染裸 PNG/JPG。三维结构用
  `render_structure.py`→`view.html`（I11）；二维数据图表用 `render_chart.py`→同名
  `.html`（I12）。任何"给我看图表"的需求都走这两条路，绝不交裸光栅图。
- 交付统一 `sha256 + 命令行` 证据；结构/数据一变就重跑门限。
- 基础设施重试（坏节点/QOS 记账/网络）需留痕；科学参数改动必须先问。
