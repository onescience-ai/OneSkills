# Model Card: Protenix

## 基本信息

- 模型名：`Protenix`
- 任务类型：`蛋白质 / 复合物 / 多分子结构预测`
- 当前状态：`stable`
- 主实现文件：`./onescience/src/onescience/models/protenix/protenix.py`

## 模型定位

Protenix 是 OneScience 中的 AlphaFold3 风格结构预测模型，面向蛋白、核酸、配体、离子等复杂生物分子体系，核心链路是 input feature embedder、relative position、template/MSA、Pairformer、diffusion structure module 和 confidence heads。

补充说明：

- 这是生信侧最明确复用 OneScience `One*` 组件入口的模型
- 输入不是普通 FASTA tensor，而是 Protenix / AF3 风格的 feature dict
- example 中推荐的统一推理入口是 `examples/biosciences/protenix/runner/inference_unified.py`

## 输入定义

- 主输入：`input_feature_dict: dict[str, Tensor]`
- 训练额外输入：
  - `label_full_dict`
  - `label_dict`
  - `mode="train"` 时需要 `symmetric_permutation`
- 关键 token / pair 特征：
  - `residue_index`, `token_index`, `token_bonds`
  - `asym_id`, `entity_id`, `sym_id`
  - `restype`, `profile`, `deletion_mean`
  - `msa`, `has_deletion`, `deletion_value`
- 关键 atom 特征：
  - `ref_pos`, `ref_mask`, `ref_charge`, `ref_element`
  - `ref_atom_name_chars`, `atom_to_token_idx`, `ref_space_uid`
  - `has_frame`, `is_ligand`

## 输出定义

- 推理主输出：
  - `coordinate`: `[..., N_sample, N_atom, 3]`
  - `summary_confidence`: 每个 sample 的汇总置信度列表
  - `full_data`: 置信度明细列表
  - `plddt`, `pae`, `pde`, `resolved`
  - `contact_probs`: `[N_token, N_token]`
- 训练主输出：
  - `coordinate` / `coordinate_mini`
  - `noise_level`
  - `distogram`
  - confidence head logits

## 主干结构

- `OneEmbedding(style="ProtenixInputFeatureEmbedder")`
  - atom attention encoder 生成 token single input，拼接 `restype/profile/deletion_mean`
- `OneEncoder(style="ProtenixRelativePositionEncoding")`
  - 生成 pair relative position encoding
- `OneLinear(style="ProtenixLinearNoBias")`
  - 初始化 `s_init`、`z_init`、token bond、recycling residual
- recycling 循环：
  - `OneEmbedding(style="ProtenixTemplateEmbedder")`
  - `OneMSA(style="ProtenixMSAModule")`
  - `OnePairformer(style="ProtenixPairformerStack")`
- `OneDiffusion(style="ProtenixDiffusionModule")`
  - 采样原子坐标
- `DistogramHead` 与 `ConfidenceHead`
  - 输出 contact、pLDDT、PAE、PDE、resolved 和 summary confidence

## 主要依赖组件

- `ProtenixInputFeatureEmbedder`
- `ProtenixRelativePositionEncoding`
- `ProtenixAtomAttentionEncoder`
- `ProtenixMSAModule`
- `ProtenixPairformerStack`
- `ProtenixDiffusionModule`
- `ProtenixAtomAttentionDecoder`
- `ProtenixAttentionPairBias / ProtenixAttentionPairBiasWithLocalAttn`
- `ProtenixDiffusionTransformer / ProtenixAtomTransformer`
- `ProtenixLinearNoBias`

## 主要 Shape 变化

- `s_inputs`: `[..., N_token, c_s_inputs]`，默认语义为 `[..., N_token, 449]`
- `s_init`: `[..., N_token, c_s]`
- `z_init`: `[..., N_token, N_token, c_z]`
- MSA sample: `[..., N_msa_sampled, N_token, c_m]`
- Pairformer 输出：
  - `s`: `[..., N_token, c_s]`
  - `z`: `[..., N_token, N_token, c_z]`
- diffusion 输出坐标：`[..., N_sample, N_atom, 3]`

## 默认关键参数

- `configs.model.N_cycle`
- `configs.model.N_model_seed`
- `configs.diffusion_batch_size`
- `sample_diffusion.N_sample`
- `sample_diffusion.N_step`
- `configs.c_s`
- `configs.c_z`
- `configs.c_s_inputs`
- example 推理常见值：`N_sample=5`, `N_step=200`, `N_cycle=10`, `dtype=bf16`

## 常见修改点

- 新增输入特征时，先判断属于 token、pair、atom 还是 label，不要直接塞进模型 forward
- 改 `c_s/c_z/c_s_inputs` 时，要同步检查 input embedder、MSA、Pairformer、diffusion 和 linear 初始化层
- 改 MSA 策略时，优先改 `configs.data.msa` 与 `ProtenixMSAModule` 配置
- 若只做推理适配，优先接 `ProtenixInferAdapter` 和 `input_json_path`，不要改模型主体

## 风险点

- `ProtenixInferAdapter` 注册名是 `protenix_infer_adapter`，不是 `protenix`
- JSON 推理路径依赖 `onescience.datapipes.protenix.*`、CCD/RDKit 相关资源和 Protenix featurizer，缺依赖时 adapter 会显式报错
- `TemplateEmbedder` 当前源码中 `n_blocks < 1` 或无 template 特征时直接返回 `0`，不要假设模板分支一定参与
- `OneMSA` 在缺少 `msa` 或 MSA 维度不足时会直接返回原 `z`
- `N_token <= 16` 时 deepspeed evo attention 会被关闭
- atom attention encoder / decoder 依赖 `atom_to_token_idx`、`ref_space_uid` 与局部 atom window 配置，不能只按普通 token transformer 理解
- diffusion transformer 只更新 token / atom 表征，最终坐标更新由 atom decoder 输出

## 推荐检索顺序

1. 先看本模型卡
2. 再看 `protenixembedding.md`、`protenixrelativepositionencoding.md`
3. 再看 `protenixatomattentionencoder.md`、`protenixmsa.md`、`protenixpairformer.md`
4. 再看 `protenixattention.md`、`protenixtransformer.md`
5. 最后看 `protenixdiffusion.md`、`protenixdecoder.md` 与 datapipe 的 `biology_protein.md`

## 组件契约入口

- `../contracts/protenixembedding.md`
- `../contracts/protenixrelativepositionencoding.md`
- `../contracts/protenixatomattentionencoder.md`
- `../contracts/protenixmsa.md`
- `../contracts/protenixpairformer.md`
- `../contracts/protenixattention.md`
- `../contracts/protenixtransformer.md`
- `../contracts/protenixdiffusion.md`
- `../contracts/protenixdecoder.md`
- `../contracts/protenixlinear.md`

## 源码锚点

- `./onescience/src/onescience/models/protenix/protenix.py`
- `./onescience/src/onescience/modules/embedding/protenixembedding.py`
- `./onescience/src/onescience/modules/encoder/protenixencoding.py`
- `./onescience/src/onescience/modules/msa/protenixmsa.py`
- `./onescience/src/onescience/modules/pairformer/protenixpairformer.py`
- `./onescience/src/onescience/modules/diffusion/protenixdiffusion.py`
- `./onescience/examples/biosciences/protenix/README.md`
