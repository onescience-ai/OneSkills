# architecture_overview

SimpleFold 由 LightningModule `onescience.models.simplefold.simplefold.SimpleFold` 和 PyTorch 主干 `torch.architecture.FoldingDiT` 组成。`SimpleFold` 管理 flow-matching 训练、EMA、采样、pLDDT 分支与 checkpoint；`FoldingDiT` 将噪声原子坐标、时间和处理后的原子/残基/ESM 特征映射为速度场。

# parameter_scale

- `SimpleFold` 构造器接收 `architecture`、`processor`、`loss`、`path`、`sampler`，可选 optimizer、scheduler、pLDDT module，默认 `ema_decay=0.999`、`esm_model="esm2_3B"`。
- `FoldingDiT` 默认 `hidden_size=1152`、`num_heads=16`、`atom_num_heads=4`、`output_channels=3`，atom encoder/decoder hidden size 默认 256。
- 实际 block 数与组件规模由传入的 trunk、embedder 和 transformer 对象决定。

# architecture_structure

```text
processed feats + noised_pos + t
  -> atom/reference feature embedding
  -> atom encoder transformer
  -> atom-to-token aggregation
  -> ESM conditioning + residue trunk
  -> token-to-atom broadcast + skip
  -> atom decoder transformer
  -> predict_velocity

SimpleFold
  -> flow-matching training or sampler
  -> EMA/checkpoint and optional pLDDT
```

# input_schema

- `FoldingDiT.forward(noised_pos, t, feats, self_cond=None)`。
- `feats` 使用源码字段，包括 `ref_pos`、`mol_type`、`atom_to_token`、`atom_to_token_idx`、`ref_space_uid`、`res_type`、`pocket_feature`、`ref_charge`、`atom_pad_mask`、`ref_element`、`ref_atom_name_chars`、`esm_s`、`residue_index`、`entity_id`、`asym_id`、`sym_id` 和 `max_num_tokens`。
- `SimpleFold.training_step` 与 `predict_step` 接收 processor/datamodule 产生的 batch，字段必须与 architecture、path 和 sampler 匹配。

# output_schema

- `FoldingDiT.forward` 返回 `{"predict_velocity": Tensor, "latent": Tensor}`。
- `predict_velocity` 与输入原子坐标对应，末维由 `output_channels` 控制，默认是 3。
- `SimpleFold.training_step` 返回训练 loss；`predict_step` 执行采样和可选 pLDDT，并由该 LightningModule 的预测逻辑管理结构结果。
- 文件落盘属于 `SimpleFold.predict_step` 的上层行为，不是 `FoldingDiT` 返回协议。

# shape_transformations

1. 原子特征与噪声坐标分别嵌入到 hidden size。
2. atom encoder 处理 `(B, N_atom, D)`。
3. `atom_to_token` 聚合为 `(B, N_token, D)`，与加权 ESM 表征融合。
4. residue trunk 更新 token 表征后广播回 atoms。
5. atom decoder 输出 `(B, N_atom, output_channels)` 速度场。

# key_dependencies

- `simplefold_folding_dit`

# common_modification_points

- 替换 ESM 规格时同步修改 `esm_model_dict`、输入 `esm_s` 层数与通道。
- 调整局部 atom attention 时修改 encoder/decoder query/key window 参数。
- 修改 feature schema 时同步更新 processor 和 `FoldingDiT.forward` 的拼接维度。
- 训练通过 `SimpleFold.training_step`；仅测试主干时可直接调用 `FoldingDiT.forward`。

# implementation_risks

- 直接把 FASTA 字符串传给模型无效，必须先生成完整 `feats`。
- `atom_to_token`、atom 数和 token 数不一致会在 batch matrix multiplication 处失败。
- `esm_s` 的层数/通道必须与所选 `esm_model` 一致。
- `SimpleFold` 的 sampler、path、loss 与 architecture 是协作组件，不能只加载主模型权重而忽略其配置。

# code_references

- `{onescience_path}/onescience/src/onescience/models/simplefold/simplefold.py`
- `{onescience_path}/onescience/src/onescience/models/simplefold/torch/architecture.py`
- `{onescience_path}/onescience/src/onescience/models/simplefold/torch/sampler.py`
- `{onescience_path}/onescience/src/onescience/models/simplefold/flow.py`
