# Contract: UMA MoE

## 基本信息

- 组件名：`UMA MoE Backbone`
- 所属模块族：`materials / uma / moe`
- 统一入口：`eSCNMDMoeBackbone`
- 注册名：`not_applicable`
- 主源码：
  - `./onescience/src/onescience/models/UMA/uma_escn_moe.py`
  - `./onescience/src/onescience/modules/block/uma_mole_block.py`

## 组件职责

在 UMA eSCNMD backbone 中引入 Mixture-of-Experts 路由，按 dataset/task 条件选择或组合专家参数。

覆盖组件：

- `eSCNMDMoeBackbone`
- `MOLE`
- `MOLEDGL`
- `MOLEGlobals`

## 输入契约

- 普通 UMA `AtomicData` batch
- dataset/task 条件
- MoE routing 参数
- block 内专家权重和 gating 信息

## 输出契约

- 与 `eSCNMDBackbone` 相同的节点球谐表示
- 额外内部路由或专家选择状态，通常不作为外部 API 依赖

## 关键参数

- `num_experts`
- `moe_type`
- `moe_dropout`
- `gate`
- `dataset_embedding`
- `activation_checkpoint_chunk_size`

## 典型调用位置

- UMA MoE checkpoint 初始化
- 多数据集 foundation 模型推理
- dataset-specific heads 配合使用

## 常见修改点

- 改专家数：checkpoint 通常不兼容，需重新训练或写迁移逻辑。
- 改 routing 条件：同步 dataset embedding、heads 和 normalizer。
- activation checkpoint：检查 `set_mole_ac_start_index`。

## 风险点

- MoE 参数与普通 eSCNMD checkpoint 不兼容。
- dataset key 漏项会造成路由错误。
- 多卡训练中专家负载不均可能造成性能和稳定性问题。
- 把 MoE 当作普通 block 局部替换时容易漏掉全局 gating 状态。

## 源码锚点

- `./onescience/src/onescience/models/UMA/uma_escn_moe.py`
- `./onescience/src/onescience/modules/block/uma_mole_block.py`
- `./onescience/src/onescience/modules/block/uma_escn_md_block.py`

## 下钻关系

- eSCNMD block：`./uma_escn_md_block.md`
- embedding：`./uma_embedding.md`
- Hydra model：`./uma_hydra_model.md`
- head：`./uma_head.md`
