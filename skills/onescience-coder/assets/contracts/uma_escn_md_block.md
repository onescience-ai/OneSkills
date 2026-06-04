# Contract: uma_escn_md_block.py

## 基本信息

- 组件名：`eSCNMD_Block`
- 所属模块族：`materials / uma / block`
- 统一入口：`direct_import`
- 注册名：`not_applicable`
- 主源码：`./onescience/src/onescience/modules/block/uma_escn_md_block.py`

## 组件职责

实现 UMA eSCNMD 主干的单层等变消息传递，通常按 `norm -> edgewise -> residual -> norm -> atomwise -> residual` 更新节点球谐表示。

覆盖组件：

- `Edgewise`
- `SpectralAtomwise`
- `GridAtomwise`
- `eSCNMD_Block`
- `set_mole_ac_start_index`

## 输入契约

- 节点球谐特征：`(NumAtoms, SphFeatureSize, SphereChannels)`
- 边特征：`(NumEdges, EdgeChannels)`
- `edge_index`: `(2, NumEdges)`
- `edge_distance`: `(NumEdges,)`
- Wigner / SO3 mapping / rotation matrices
- 可选 activation checkpoint chunk 信息

## 输出契约

- 输出节点球谐特征，shape 与输入节点特征一致
- block 内完成边消息、原子前馈、残差更新和必要的归一化

## 关键参数

- `sphere_channels`
- `hidden_channels`
- `lmax`
- `mmax`
- `edge_channels_list`
- `cutoff`
- `norm_type`
- `act_type`
- `ff_type`
- `activation_checkpoint_chunk_size`

## 典型调用位置

- `eSCNMDBackbone.blocks`
- `eSCNMDMoeBackbone` 中的共享或专家 block
- UMA fine-tuning 和推理 forward

## 常见修改点

- 切换 `ff_type`: `spectral` 与 `grid` 对 SO3 grid 依赖和显存行为不同。
- 开启 activation checkpoint：确认边 chunk 与 MoE 起始索引维护正确。
- 改 `lmax/mmax/sphere_channels`: 同步检查 embedding、head、Jd 常量和 checkpoint。

## 风险点

- Wigner mapping、edge index、SO3 rotation 信息不一致会造成隐性数值错误。
- `ff_type` 切换会改变显存、速度和数值行为，不只是精度参数。
- MoE 混用时要正确维护 `ac_start_idx`。
- backbone 结构参数改动通常不能直接加载旧 checkpoint。

## 源码锚点

- `./onescience/src/onescience/modules/block/uma_escn_md_block.py`
- `./onescience/src/onescience/models/UMA/uma_escn_md.py`
- `./onescience/src/onescience/models/UMA/uma_escn_moe.py`

## 下钻关系

- 嵌入：`./uma_embedding.md`
- 径向：`./uma_radial.md`
- MoE：`./uma_moe.md`
- 主模型：`./uma_hydra_model.md`
