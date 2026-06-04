# Contract: uma_head.py

## 基本信息

- 组件名：`UMA Head Family`
- 所属模块族：`materials / uma / head`
- 统一入口：`HydraModel heads`
- 注册名：`class_path / registry`
- 主源码：`./onescience/src/onescience/modules/head/uma_head.py`

## 组件职责

把 UMA backbone 的节点嵌入映射为 energy、forces、stress 等任务输出，并支持多数据集专用 head 包装。

覆盖组件：

- `MLP_EFS_Head`
- `MLP_Energy_Head`
- `Linear_Energy_Head`
- `Linear_Force_Head`
- `MLP_Stress_Head`
- `DatasetSpecificMoEWrapper`
- `DatasetSpecificSingleHeadWrapper`

## 输入契约

- `emb["node_embedding"]`: `(NumAtoms, SphFeatureSize, SphereChannels)`
- `data["batch"]`: `(NumAtoms,)`
- `data["natoms"]`: `(NumGraphs,)`
- `data["pos"]`: 需要力导数时必须可求导
- `data["cell"]`: 需要 stress 时必须可用
- `data["dataset"]`: 多数据集 wrapper 需要

## 输出契约

- `energy`: `(NumGraphs, 1)` 或 `(NumGraphs,)`
- `forces`: `(NumAtoms, 3)`
- `stress`: `(NumGraphs, 9)` 或配置约定张量
- wrapper 输出可能带 dataset/property 前缀，取决于 Hydra 配置

## 关键参数

- `hidden_dim`
- `num_layers`
- `direct_forces`
- `regress_stress`
- `wrap_property`
- `dataset_names`
- `heads`

## 典型调用位置

- UMA Hydra 配置 `data.heads`
- `initialize_finetuning_model`
- `HydraModel.forward`
- `MLIPTrainEvalUnit.compute_loss`

## 常见修改点

- 改任务输出：同步 task `property`、head 输出字段、loss 和 metric。
- 直接力 vs 能量导数力：检查 `direct_forces` 与 `pos.requires_grad`。
- 多数据集 head：确认 batch 内 dataset key、head key、normalizer key 覆盖完整。

## 风险点

- force head 配置错误会造成无力输出或梯度路径断裂。
- stress 输出 shape 与 loss 预期不一致会在首个 batch 崩溃。
- wrapper 的 dataset key 不一致会导致只在特定数据集报错。
- pass-through 输出会改变 loss/metric 读取的 dict key。

## 源码锚点

- `./onescience/src/onescience/modules/head/uma_head.py`
- `./onescience/src/onescience/models/UMA/base.py`
- `./onescience/src/onescience/utils/uma/units/mlip_unit/mlip_unit.py`

## 下钻关系

- Hydra 模型：`./uma_hydra_model.md`
- 训练 unit：`./uma_mlip_unit.md`
- loss：`./uma_loss.md`
- 数据字段：`../datapipes/materials_uma.md`
