# Contract: MACE Calculator and Deployment

## 基本信息

- 组件名：`MACE Calculator and Deployment`
- 所属模块族：`materials / mace / calculator`
- 统一入口：`MACECalculator` / CLI scripts
- 注册名：`not_applicable`
- 主源码：
  - `./onescience/src/onescience/utils/mace/calculators/mace.py`
  - `./onescience/src/onescience/utils/mace/calculators/lammps_mace.py`
  - `./onescience/src/onescience/utils/mace/calculators/lammps_mliap_mace.py`

## 组件职责

把训练好的 MACE 模型用于 ASE 单点、结构弛豫、MD、descriptor 提取和 LAMMPS 部署。

## 输入契约

- ASE `Atoms`，必须包含正确 `positions`、`cell`、`pbc`
- MACE `.model` checkpoint 或模型列表
- 计算属性：`energy`、`forces`、`stress`、`free_energy`
- 可选：`device`、`default_dtype`、`charges_key`、`model_type`

## 输出契约

- ASE calculator results：
  - `energy`
  - `free_energy`
  - `forces`
  - `stress`
  - 可选 descriptor / node features
- LAMMPS 导出模型：供 `pair_style mace` 或 MLIAP 路径使用

## 关键参数

- `model_paths`
- `device`
- `default_dtype`
- `energy_units_to_eV`
- `length_units_to_A`
- `stress_units_to_eV_A3`
- `compute_stress`
- `enable_cueq`

## 典型调用位置

- `examples/matchem/mace/scripts/run_md.py`
- `examples/matchem/mace/scripts/eval_configs.py`
- `examples/matchem/mace/scripts/create_lammps_model.py`
- ASE relaxation / MD workflows

## 常见修改点

- MD 稳定性：选择验证集误差和短 MD 都稳定的 checkpoint。
- LAMMPS 导出：确认模型 dtype、device、cuEquivariance 转换和元素顺序。
- 多模型 ensemble：用于主动学习、不确定性和 OOD 筛选。
- stress 输出：ASE Voigt 与 3x3 tensor 约定要核对。

## 风险点

- 模型训练元素顺序和 ASE `Atoms` 元素不一致会导致错误 one-hot。
- `default_dtype=float32` 速度快，但高精度力/应力可能需要检查。
- 长时间 MD 不能只凭验证 RMSE 判断，必须做能量漂移、温度和结构稳定性检查。
- LAMMPS 部署前必须确认单位制。

## 下钻关系

- 模型输出/autograd：`./mace_func_utils.md`
- 数据和 checkpoint：`../datapipes/materials_mace.md`
- fine-tuning 选择：`./mace_finetuning_utils.md`

## 源码锚点

- `./onescience/src/onescience/utils/mace/calculators/mace.py`
- `./onescience/src/onescience/utils/mace/calculators/lammps_mace.py`
- `./onescience/src/onescience/utils/mace/calculators/lammps_mliap_mace.py`
- `./onescience/src/onescience/utils/mace/cli/create_lammps_model.py`
- `./onescience/examples/matchem/mace/scripts/run_md.py`
- `./onescience/examples/matchem/mace/scripts/eval_configs.py`
