# Contract: UMA HydraModel

## 基本信息

- 组件名：`HydraModel / HydraModelV2`
- 所属模块族：`materials / uma / model`
- 统一入口：`HydraModel`
- 注册名：`hydra`
- 主源码：`./onescience/src/onescience/models/UMA/base.py`

## 组件职责

用共享 backbone 和多个 head 组织 UMA 多任务模型。backbone 生成原子结构表征，head 根据任务输出 energy、forces、stress 等属性。

## 输入契约

- `AtomicData` 或 batch dict
- 必要字段：`atomic_numbers`、`pos`、`batch`、`natoms`
- 周期体系：`cell`、`pbc`
- 多任务条件：`dataset`、`charge`、`spin`
- 可选外部图：`edge_index`、`cell_offsets`、`nedges`

## 输出契约

- dict，key 由 head/task/property 配置决定
- 常见输出：`energy`、`forces`、`stress`
- 可配置 pass-through head outputs

## 关键参数

- `backbone`
- `heads`
- `pass_through_head_outputs`
- `otf_graph`
- `max_neighbors`
- `regress_stress`
- `always_use_pbc`

## 典型调用位置

- `initialize_finetuning_model`
- UMA Hydra train config
- UMA inference / calculator predict unit
- `examples/matchem/uma/train.py`

## 常见修改点

- 新增 head：同步 `data.heads`、`tasks_list`、loss、metric 和 checkpoint 初始化。
- 改 backbone override：同步 checkpoint 兼容和 inference 配置。
- 开启 stress/force 任务：检查 head 与 task property 名称一致。
- 切换普通 eSCNMD 与 MoE：确认 backbone class、dataset embedding 和 checkpoint 同源。

## 风险点

- checkpoint 的 backbone/head key 与 Hydra 配置不匹配会加载失败。
- `pass_through_head_outputs` 改变输出 dict 结构，loss/metric 需同步。
- `always_use_pbc` 对分子和晶体语义不同，不能默认套用。
- 对预训练 checkpoint 做结构性改动通常需要迁移脚本或重新训练。

## 源码锚点

- `./onescience/src/onescience/models/UMA/base.py`
- `./onescience/src/onescience/models/UMA/uma_escn_md.py`
- `./onescience/src/onescience/models/UMA/uma_escn_moe.py`
- `./onescience/src/onescience/utils/uma/units/mlip_unit/mlip_unit.py`

## 下钻关系

- backbone：`./uma_escn_md_block.md`
- MoE：`./uma_moe.md`
- heads：`./uma_head.md`
- training unit：`./uma_mlip_unit.md`
- calculator：`./uma_calculator.md`
