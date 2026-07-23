# architecture_overview

Protenix 的公开模型类是 `onescience.models.protenix.protenix.Protenix`。它按照 AF3 风格把输入特征嵌入、相对位置编码、template/MSA、Pairformer、扩散结构生成、distogram 与 confidence heads 组合成统一模型；`forward` 内部按 `train`、`inference` 或 `eval` 分派不同循环。

# parameter_scale

- `Protenix(configs)` 的所有网络规模来自 `configs`。
- `configs.model.N_cycle` 控制 recycling 次数，`configs.model.N_model_seed` 控制推理 seed 数。
- `configs.diffusion_batch_size` 控制扩散采样分批。
- 通道包括 `configs.c_s`、`configs.c_z`、`configs.c_s_inputs`；采样与噪声调度来自 `train_noise_sampler` 和 `inference_noise_scheduler` 配置。

# architecture_structure

```text
input_feature_dict
  -> ProtenixInputFeatureEmbedder
  -> relative position + template + MSA
  -> Pairformer recycling stack
  -> diffusion sampling / denoising
  -> coordinates
  -> DistogramHead + ConfidenceHead
  -> prediction dictionary
```

训练分支执行随机 recycling、扩散/置信度相关计算和对称置换；推理分支支持多 model seed 并合并样本预测。

# input_schema

- `forward(input_feature_dict, label_full_dict, label_dict, mode="inference", current_step=None, symmetric_permutation=None)`。
- `mode` 仅允许 `train`、`inference`、`eval`。
- inference 主要使用 `input_feature_dict`，标签参数可以为 `None`。
- train 要求模型处于 training 状态、`label_dict` 非空、`current_step` 可生成 recycling 随机状态，且 `symmetric_permutation` 非空。
- eval 可接受 label 以计算带真值的结果。

# output_schema

- `forward` 始终返回 `(pred_dict, label_dict, log_dict)`。
- inference `pred_dict` 包括 `coordinate`、`summary_confidence`、`contact_probs` 以及 pLDDT/PAE/PDE/resolved 等 confidence 结果。
- train `pred_dict` 包括训练阶段产生的 denoised coordinate、distogram 和损失所需中间预测；具体字段受配置和 `train_confidence_only` 影响。
- `log_dict` 包含耗时、置换或训练统计。

# shape_transformations

1. atom/token/pair 输入特征映射到 `s_inputs`、single 与 pair 表征。
2. template、MSA 与相对位置编码注入 pair 表征。
3. Pairformer 在 recycling 循环中更新 single/pair。
4. diffusion module 从噪声坐标生成 atom coordinate samples。
5. distogram 与 confidence heads 将 pair/single/coordinate 映射为接触和置信度输出。

# key_dependencies

- `protenix_embedding`
- `protenix_relative_position_encoding`
- `protenix_atom_attention_encoder`
- `protenix_msa`
- `protenix_pairformer`
- `protenix_diffusion`
- `protenix_decoder`
- `protenix_attention`
- `protenix_transformer`
- `protenix_linear`

# common_modification_points

- 调整分子类型或输入协议时先修改 feature builder，保持模型字典字段与 atom/token/pair 映射一致。
- 调整速度/显存时修改 `N_cycle`、model seeds、diffusion batch、chunk size 和采样 scheduler。
- 只训练 confidence head 时同步满足源码对 diffusion/distogram loss weight 的断言。
- 新模块应实现现有 OneScience modules 的输入输出契约后再替换。

# implementation_risks

- Protenix 不接受原始 FASTA、SMILES 或 JSON 字符串；必须先构造完整 feature dict。
- train 模式缺少 label 或 `SymmetricPermutation` 会立即失败。
- inference、eval 与 train 返回字段并非完全相同，下游代码必须按 mode 解析。
- 配置中的通道数、feature 维度和 checkpoint 必须一致。

# code_references

- `{onescience_path}/onescience/src/onescience/models/protenix/protenix.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/protenixembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/protenixencoding.py`
- `{onescience_path}/onescience/src/onescience/modules/msa/protenixmsa.py`
- `{onescience_path}/onescience/src/onescience/modules/pairformer/protenixpairformer.py`
- `{onescience_path}/onescience/src/onescience/modules/diffusion/protenixdiffusion.py`
- `{onescience_path}/onescience/src/onescience/metrics/confidence/confidencehead.py`
- `{onescience_path}/onescience/src/onescience/metrics/distogram/distogram_head.py`
