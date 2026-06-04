# Contract: uma_loss.py

## 基本信息

- 组件名：`UMA Loss Family`
- 所属模块族：`materials / uma / loss`
- 统一入口：`registry / Hydra class path`
- 注册名：`mae / mse / per_atom_mae / l2norm / ddpmt`
- 主源码：`./onescience/src/onescience/modules/loss/uma_loss.py`

## 组件职责

提供 UMA 多任务训练中的基础损失、per-atom 损失、向量范数损失和 DDP 多任务封装。

覆盖组件：

- `DDPMTLoss`
- `MAELoss`
- `MSELoss`
- `PerAtomMAELoss`
- `L2NormLoss`
- `DDPLoss`

## 输入契约

- `pred`: 预测张量
- `target`: 标签张量
- `natoms`: `(NumGraphs,)`
- `mult_mask`: 任务 mask
- normalizer / element reference 后处理结果
- DDP 上下文：全局样本数或原子数修正

## 输出契约

- 单任务标量 loss
- `DDPMTLoss` 输出经 DDP 修正后的标量
- 可由训练 unit 聚合为多任务 loss dict

## 关键参数

- `coefficient`
- `reduction`
- `loss_fn`
- `normalizer`
- `element_references`

## 典型调用位置

- UMA Hydra `tasks_list`
- `MLIPTrainEvalUnit.compute_loss`
- energy / forces / stress 多任务训练

## 常见修改点

- 新增任务：同步 task `property`、head 输出、normalizer 和 metrics。
- 调整 loss 系数：按物性目标设置，不只按数值尺度。
- DDP 训练：保持 `DDPMTLoss` 封装，避免各 rank 原子数不同导致偏差。

## 风险点

- `natoms` 缺失或错误会污染 per-atom loss。
- force 向量 loss 的 reduction 与任务目标不匹配会改变训练行为。
- normalizer/element reference 不匹配会造成 energy 偏移。
- 多任务 loss key 与 head output key 不一致会在训练首步失败。

## 源码锚点

- `./onescience/src/onescience/modules/loss/uma_loss.py`
- `./onescience/src/onescience/utils/uma/units/mlip_unit/mlip_unit.py`

## 下钻关系

- 训练 unit：`./uma_mlip_unit.md`
- head 输出：`./uma_head.md`
- 归一化：`./uma_normalization.md`
- 数据字段：`../datapipes/materials_uma.md`
