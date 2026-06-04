# Contract: UMA Calculator and Inference

## 基本信息

- 组件名：`UMA Calculator and Inference`
- 所属模块族：`materials / uma / calculator`
- 统一入口：`FAIRChemCalculator`
- 注册名：`not_applicable`
- 主源码：
  - `./onescience/src/onescience/utils/uma/calculate/ase_calculator.py`
  - `./onescience/src/onescience/utils/uma/calculate/pretrained_mlip.py`

## 组件职责

将 UMA checkpoint 用于 ASE 单点、弛豫、吸附体系、晶体结构、分子 MD、spin gap 和批推理。

## 输入契约

- ASE `Atoms`
- checkpoint/model name
- `task_name`
- charge / spin / dataset 信息
- `cell` / `pbc`
- calculator 配置：device、dtype、max_neighbors、`Jd.pt` 路径

## 输出契约

- ASE calculator results：`energy`、`forces`、`stress`
- relaxation / MD trajectory
- batch inference prediction dict

## 关键参数

- `checkpoint_path`
- `model_name`
- `task_name`
- `device`
- `max_neighbors`
- `charge`
- `spin`
- `dataset`
- `jd_path`

## 典型调用位置

- `examples/matchem/uma/inference/relax_inorganic_crystal.py`
- `examples/matchem/uma/inference/relax_adsorbate_on_slab.py`
- `examples/matchem/uma/inference/run_molecular_md.py`
- `examples/matchem/uma/inference/calculate_spin_gap.py`
- `examples/matchem/uma/inference/batch_inference_with_dataloader.py`

## 常见修改点

- 切换预训练模型：同步 isolated atomic energies、task name 和 normalizer。
- 分子 vs 晶体：确认 PBC、cell、charge 和 spin。
- 吸附体系：确认 slab/adsorbate tags、约束和是否固定原子。
- MD：先做短时稳定性检查，再跑长时间模拟。

## 风险点

- `Jd.pt` 缺失会阻断初始化。
- mixed PBC 或 zero cell 可能触发 calculator 错误。
- task/dataset 不匹配会导致 head 或 normalizer 不正确。
- 预训练 checkpoint 下载、转换或路径解析失败时，不能假装可推理。

## 源码锚点

- `./onescience/src/onescience/utils/uma/calculate/ase_calculator.py`
- `./onescience/src/onescience/utils/uma/calculate/pretrained_mlip.py`
- `./onescience/examples/matchem/uma/inference/*.py`

## 下钻关系

- Hydra 模型：`./uma_hydra_model.md`
- 图构建：`./uma_graph_compute.md`
- 路径：`./uma_path_utils.md`
- normalizer/reference：`./uma_normalization.md`
- 数据：`../datapipes/materials_uma.md`
