# Contract: UMA MLIP Unit

## 基本信息

- 组件名：`UMA MLIPTrainEvalUnit`
- 所属模块族：`materials / uma / train_unit`
- 统一入口：`MLIPTrainEvalUnit`
- 注册名：`not_applicable`
- 主源码：`./onescience/src/onescience/utils/uma/units/mlip_unit/mlip_unit.py`

## 组件职责

封装 UMA fine-tuning 和 evaluation 的任务定义、collate adapter、模型初始化、loss、metrics、scheduler 和训练循环接口。

覆盖内容：

- `Task`
- `OutputSpec`
- `initialize_finetuning_model`
- `mt_collater_adapter`
- `compute_loss`
- `compute_metrics`
- `MLIPTrainEvalUnit`
- `MLIPEvalUnit`

## 输入契约

- Hydra config 中的 `tasks_list`
- `train_dataloader` / `eval_dataloader`
- `checkpoint_location`
- `optimizer_fn`
- `cosine_lr_scheduler_fn`
- batch: `AtomicData`

## 输出契约

- train step loss dict
- eval metrics dict
- checkpoint callbacks
- inference-ready model state

## 关键参数

- `tasks`
- `checkpoint_location`
- `batch_size`
- `epochs` / `steps`
- `lr`
- `weight_decay`
- `evaluate_every_n_steps`
- `checkpoint_every_n_steps`
- `clip_grad_norm`

## 典型调用位置

- `examples/matchem/uma/train.py`
- `configs/uma_sm_finetune_template.yaml`
- demo `oc20_ef_*dcu.yaml`
- UMA batch inference / evaluation scripts

## 常见修改点

- energy-only / EF / EFS：通过 `tasks_list`、heads 和 loss 同步控制。
- 自定义 normalizer：修改 task normalizer 和 element references。
- DDP：确认 sampler、collate、checkpoint path 在所有 rank 一致。
- scheduler：`epochs` 和 `steps` 选择一种主控语义，避免互相覆盖。

## 风险点

- task `property` 与 head 输出 key 不一致会在 loss 阶段失败。
- `checkpoint_every_n_steps` 在某些 torchrun local 场景可能造成 rank 目录不一致。
- `collate_fn` 忽略关键字段会导致首个 batch 崩溃。
- DDP 中各 rank 原子数差异较大时，loss 归约必须使用对应封装。

## 源码锚点

- `./onescience/src/onescience/utils/uma/units/mlip_unit/mlip_unit.py`
- `./onescience/src/onescience/utils/uma/components/train/train_runner.py`
- `./onescience/examples/matchem/uma/train.py`
- `./onescience/examples/matchem/uma/configs/uma_sm_finetune_template.yaml`

## 下钻关系

- 模型：`./uma_hydra_model.md`
- head：`./uma_head.md`
- loss：`./uma_loss.md`
- normalizer：`./uma_normalization.md`
- data：`../datapipes/materials_uma.md`
