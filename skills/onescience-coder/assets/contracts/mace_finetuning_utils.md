# Contract: MACE Fine-Tuning Utilities

## 基本信息

- 组件名：`MACE Fine-Tuning Utilities`
- 所属模块族：`materials / mace / tools`
- 统一入口：`examples/matchem/mace/train.py`
- 注册名：`not_applicable`
- 主源码：
  - `./onescience/src/onescience/utils/mace/tools/finetuning_utils.py`
  - `./onescience/src/onescience/utils/mace/tools/model_script_utils.py`
  - `./onescience/src/onescience/utils/mace/tools/scripts_utils.py`

## 组件职责

负责从 foundation checkpoint 提取配置、构建 fine-tuning 模型、迁移可复用权重、处理元素筛选、多头配置、参考能和 scale/shift。

## 输入契约

- `foundation_model`: MACE `.model` 或已加载 torch 模型
- `train_loader`: 用于统计 mean/std、avg_num_neighbors
- `atomic_energies`: E0s 数组或 dict
- `heads`: `["Default"]` 或多头任务列表
- `z_table`: 目标数据元素表
- YAML/CLI 参数：`foundation_model`、`E0s`、`r_max`、`scaling`、`foundation_filter_elements`

## 输出契约

- 已构建并迁移权重的 `MACE` / `ScaleShiftMACE`
- `output_args`: 是否报告 energy/forces/stress/virials/dipoles
- 更新后的训练参数：`args.model="FoundationMACE"`、`args.max_L` 等

## 关键参数

- `foundation_model`
- `foundation_filter_elements`
- `foundation_model_elements`
- `E0s`
- `scaling`
- `num_samples_pt`
- `r_max`
- `num_interactions`
- `correlation`
- `max_L`

## 典型调用位置

- `examples/matchem/mace/train.py`
- demo YAML 中的 `foundation_model` fine-tuning 配置
- MACE tutorial 的 foundation fine-tuning 流程

## 常见修改点

- 元素筛选：检查 `indices_weights` 与 foundation 元素表。
- contraction 权重迁移：按实际 `len(weights)` 和 `len(products)` 动态复制，不能写死。
- readout 迁移：多头任务要按 `heads` 重复或重建输出维度。
- E0s 策略：小数据或 DFT 设置不同优先使用 isolated atom E0s。
- checkpoint 兼容：保留 legacy `mace.*` module alias。

## 风险点

- foundation `r_max` 与目标模型不一致会触发断言或隐性构图不一致。
- `correlation=2` 模型每个 contraction 可能只有 1 个 weight，硬编码 2 会越界。
- `E0s=average` 是便捷入口，不是高精度默认。
- YAML 中的 `num_channels/max_L/correlation` 在 foundation 模式下可能被 checkpoint 配置覆盖。

## 下钻关系

- product basis 权重：`./mace_symmetric_contraction.md`
- 主干结构：`./mace_block.md`
- 数据/E0s：`../datapipes/materials_mace.md`
- loss 权重：`./mace_loss.md`

## 源码锚点

- `./onescience/src/onescience/utils/mace/tools/finetuning_utils.py`
- `./onescience/src/onescience/utils/mace/tools/model_script_utils.py`
- `./onescience/src/onescience/utils/mace/tools/scripts_utils.py`
- `./onescience/src/onescience/utils/mace/tools/multihead_tools.py`
- `./onescience/examples/matchem/mace/train.py`
