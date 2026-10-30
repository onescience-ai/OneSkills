---
name: onescience-mlmd-campaign-orchestrator
description: 端到端编排“DFT 结构优化 → AIMD 出轨迹 → MACE 数据集 → MACE 势函数训练 → LAMMPS 长时 MD”的机器学习分子动力学流水线。当用户用一句话要求“给 <界面体系> 做一套 MLMD：先 VASP 做 DFT 优化，再跑 VASP AIMD 出轨迹，转成带能量/力的 MACE extxyz 数据集（按时间块切 train/valid/test，不要随机打散），训一个 MACE 势函数（力误差达标），最后导出 LAMMPS 模型跑长时 MD，把皮秒 AIMD 推到纳秒”时加载。负责把自然语言变成结构化 campaign 规格、逐阶段执行并设硬门限、不达标即停并报告。
type: executor
capabilities:
  owns:
    - MLMD流水线编排
    - DFT优化
    - AIMD出轨迹
    - MACE数据集
    - MACE训练
    - LAMMPS长时MD
    - 硬门限管理
  not_owns:
    - 通用代码生成
    - 环境安装
  inputs:
    - campaign_description
    - interface_system
  outputs:
    - campaign_spec
    - stage_results
    - md_trajectory
  downstream:
    - onescience-dft-model-gate
    - onescience-runtime
    - onescience-trainer
  prereq:
    - 界面体系已描述
  intent_aspects:
    - mlmd_campaign
    - pipeline_orchestration
  operation_types:
    - create
    - run
  artifact_types:
    - model
    - dataset
    - log
    - report
  domains:
    - materials
  trigger_keywords:
    - MLMD
    - 机器学习分子动力学
    - MACE
    - LAMMPS
    - AIMD
    - 势函数
    - campaign
---

# Skill: onescience-mlmd-campaign-orchestrator

## 这个技能解决什么

把“给我做一套 MLMD”这类**一句话需求**，变成一条**可复现、带门限、可交接**的流水线，
并把科研要害固化为默认规则：**中性 vs 恒电位**、**时间块切分（防泄漏）**、**误差验收门限**、
以及“**不达标就停、不擅自改科学参数**”。

## When to Use

用户提出类似（不限于此）：

> “我需要你帮我给 CO₂/Cu(111)/水/K⁺ 界面（188 原子，底部两层 32 个 Cu 固定）
> 做一套机器学习分子动力学：先 VASP 做 DFT 结构优化，再跑 VASP AIMD 出轨迹，
> 然后转成带能量和力的 MACE extxyz 数据集（按 100 帧时间块切 train/valid/test，**千万别随机打散**），
> 训一个 MACE 势函数（验收标准力误差 ≲10 meV/Å），最后导出成 LAMMPS 能加载的模型跑长时 MD——
> 目的就是把只能跑皮秒的 AIMD 推到纳秒，用来研究 CO₂ 的界面动力学；走**中性** AIMD。”

## 一句话 → 结构化规格

先把需求填进 `assets/campaign_spec.example.json`，与用户确认后落 `campaign_spec.json`。本场景默认：

- `electrochemistry.mode = "neutral"`（禁 VASPsol/CP）。
- `slab.fix_bottom_layers = 2`（188 原子中底部 **32 个 Cu 固定**）。
- `dataset.split = {policy:"time-block", block_frames:100, shuffle:false}`（**绝不随机打散**）。
- `train.acceptance.forces_rmse_meV_per_A = 10.0`。
- `aimd = {NVT, Nose-Hoover, 300 K, 1 fs, 6 ps, velocity_init:"fresh-MB"}`。
- `export = {libtorch, elements:["H","C","O","K","Cu"]}`。

## 阶段、门限与交接（自包含）

| 阶段 | 做什么 | 本 skill 内对应 | 交付 | 门限（不达标即停） |
|---|---|---|---|---|
| S0 | 归一化需求 + 站点解析 | `assets/campaign_spec.example.json`；`references/environment_notes.md` | spec + 站点画像 | 必备字段齐全；站点连通 |
| S1 | DFT 结构优化 | `scripts/build_interface_example.py` + `assets/INCAR.relax.example` + `assets/submit.vasp.example.slurm`；门限 → `onescience-dft-model-gate` (`check_vasp_inputs.py --delivery-dir`, I10+I11) | `POSCAR/CONTCAR/契约/view.html` | `check_geometry` + `check_vasp_inputs --delivery-dir` PASS（I11 含 view.html）；力收敛 ≤ \|EDIFFG\| |
| S2 | 中性 AIMD 出轨迹 | `assets/INCAR.nvt.example` + `references/velocity_block_pitfall.md` + 提交模板 | `vasprun.xml/XDATCAR/OSZICAR` | 温度稳定、SCF 收敛、无 refuse、**速度块已处理**、**中性守卫** |
| S3 | 轨迹 → 数据集 | `scripts/probe_traj.py` + `scripts/vasp2mace_dataset.py` + `scripts/validate_dataset.py` + `references/split_policy.md` | `*_train/valid/test.extxyz`(+h5) | 键为真值、计数一致、**time-block 且 shuffle=false** |
| S4 | 训练 MACE | `assets/submit.mace.example.slurm` + `references/environment_notes.md` | `*_stagetwo.model` + 误差曲线 | **验证力 RMSE ≤ 门限（默认 10 meV/Å）** |
| S5 | 导出 LAMMPS | `scripts/create_lammps_model.example.sh` | `mace_*_lammps.pt` + 用法 | 可 `jit.load`、元素顺序一致、导出代码=训练代码 |
| S6 | 长时 MD | LAMMPS 输入（`pair_style mace`/`mliap`） | 长轨迹 + 分析 | 能量守恒量级合理；无飞散/穿层 |

详细的每步命令见 **`references/stage_playbook.md`**（自包含，含建模型/AIMD/数据集/训练/导出/长 MD）。

## 控制流

```
S0（确认 spec）→ S1 →gate→ S2 →gate→ S3 →gate→ S4 →gate(误差)→ S5 →gate→ S6
```
- 每个 gate 输出 **PASS/FAIL + 实测值/门限值 + `sha256`**；FAIL → **停止并报告**。
- 允许的“自动重试”仅限**基础设施层**（坏节点、QOS 记账、网络），且记录原因。
- 需要改科学参数（时间步、温度、切分、超参）时，**先问用户**。
- **todo 同步（界面状态）**：campaign 启动时必须用 `todowrite` 将 S0–S6 登记为 todo 列表；
  阶段**开始**时将当前阶段置 `in_progress`，该阶段 gate **PASS 后立刻**再次调用 `todowrite`
  置 `completed` 并将下一阶段置 `in_progress`；gate FAIL 置 `cancelled` 并停止。
  todo 面板只随 `todowrite` 调用刷新，正文中“S0 完成”之类散文陈述**不会**更新面板，
  阶段状态流转一律以 `todowrite` 工具调用落地。

## 三条不可动摇的规则

1. **中性守卫**：S2 开始前查 `INCAR/OUTCAR`；出现 `LSOL/LCEP` 或 `CPM-ion`
   （恒电位/隐式溶剂、变 `N_ele`）→ 与 `mode=neutral` 矛盾，**FAIL 并停下**。
2. **时间块切分**：`dataset.split.policy="time-block"`、`block_frames=100`、`shuffle=false`；
   随机打散会造成相邻帧跨集合泄漏。实现见 `scripts/vasp2mace_dataset.py`、判据见 `references/split_policy.md`。
3. **验收门限**：S4 用验证集算力 RMSE；`≤ 10 meV/Å` 才 PASS，否则报告差距与建议，
   不擅自加数据/改超参。见 `references/acceptance.md`。

## 硬性规则

1. 不跳过门限：任一阶段 FAIL 不得进入下一阶段。
2. 不擅自改科学参数；基础设施重试要留痕。
3. 交付统一 **契约 + 硬门限 + 证据绑定（sha256 + 命令行）**；文件一变就重跑门限。
4. 站点相关常量（分区/module/路径/DTK 版本）只从配置取，不写死。
5. 交付必须声明计算语义（中性/恒电位、泛函、色散、溶剂），供下游判断适用性。

## 文件

| 文件 | 作用 |
|---|---|
| `assets/campaign_spec.example.json` | campaign 规格（本场景已填好） |
| `assets/model_contract.example.json` | 初始模型契约模板 |
| `assets/INCAR.relax.example` / `assets/INCAR.nvt.example` | 松弛 / NVT AIMD 输入示例 |
| `assets/submit.vasp.example.slurm` / `assets/submit.mace.example.slurm` | 提交模板 |
| `assets/configfile.template` | Intel MPI `-configfile` 范式（含换行坑） |
| `scripts/build_interface_example.py` | 参考构图脚本（fcc111 + 水膜 + CO2 + K） |
| `scripts/probe_traj.py` | 轨迹探测（帧数/元素/能量/力/应力） |
| `scripts/vasp2mace_dataset.py` | 轨迹 → extxyz（REF_* 键 + **time-block 切分**） |
| `scripts/validate_dataset.py` | 数据集校验（含切分策略核对） |
| `scripts/create_lammps_model.example.sh` | 模型 → LAMMPS 力场文件 |
| `references/stage_playbook.md` | 各阶段逐步命令 |
| `references/velocity_block_pitfall.md` | AIMD 速度块陷阱 |
| `references/split_policy.md` | 时间块切分定义与实现 |
| `references/acceptance.md` | 力误差门限与“不达标怎么办” |
| `references/environment_notes.md` | onescience/torch/DCU/SLURM 环境排错 |

## 依赖的兄弟技能

- **`onescience-dft-model-gate`**：S1 建模几何门限（`check_geometry.py`）与交付门限（`check_vasp_inputs.py --delivery-dir` 含 I10 形态 + I11 三维视图）。
- **`onescience-structure-viewer`**：S1 交付视图 `view.html`（I11 硬门限要求），缺图 check_vasp_inputs 会 FAIL(exit 1)，必须渲染后重跑门限。
