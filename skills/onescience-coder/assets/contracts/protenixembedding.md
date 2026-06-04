# Contract: ProtenixEmbedding

## 基本信息

- 组件名：`ProtenixInputFeatureEmbedder / ProtenixTemplateEmbedder / ProtenixFourierEmbedding`
- 所属模块族：`embedding`
- 统一入口：`OneEmbedding`
- 注册名：`style="ProtenixInputFeatureEmbedder"`, `style="ProtenixTemplateEmbedder"`, `style="ProtenixFourierEmbedding"`

## 组件职责

Protenix embedding 组件负责把 AF3 / Protenix 风格输入特征投影为 token single 输入、template pair 更新或 diffusion noise 条件。

补充说明：

- `ProtenixInputFeatureEmbedder` 是主模型开头的 token 输入构造模块
- `ProtenixTemplateEmbedder` 是 template pair 表征模块，当前源码中无 template 或 `n_blocks < 1` 时返回 `0`
- `ProtenixFourierEmbedding` 用于 diffusion noise level 的 Fourier 条件编码

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- `ProtenixInputFeatureEmbedder` 输入：
  - `input_feature_dict`
  - 必需 atom 特征：`ref_pos`, `ref_charge`, `ref_mask`, `ref_element`, `ref_atom_name_chars`, `atom_to_token_idx`, `ref_space_uid`
  - 必需 token 特征：`restype`, `profile`, `deletion_mean`
- `ProtenixTemplateEmbedder` 输入：
  - `input_feature_dict`
  - `z`: `[..., N_token, N_token, c_z]`
- `ProtenixFourierEmbedding` 输入：
  - `t_hat_noise_level`: `[..., N_sample]`

内部统一做法：

- input feature embedder 先经 `ProtenixAtomAttentionEncoder` 得到 atom-to-token 表征
- 再拼接 `restype(32) + profile(32) + deletion_mean(1)`
- Fourier embedding 用固定随机 `w/b` 计算 cos embedding

## 构造参数

- `ProtenixInputFeatureEmbedder`
  - `c_atom=128`
  - `c_atompair=16`
  - `c_token=384`
- `ProtenixTemplateEmbedder`
  - `n_blocks=2`
  - `c=64`
  - `c_z=128`
  - `dropout=0.25`
  - `blocks_per_ckpt=None`
- `ProtenixFourierEmbedding`
  - `c`
  - `seed=42`

## 输出约定

- `ProtenixInputFeatureEmbedder` 输出：
  - `[..., N_token, 449]`，其中 `449 = c_token(384) + 32 + 32 + 1`
- `ProtenixTemplateEmbedder` 输出：
  - template feature `[..., N_token, N_token, c_z]` 或 `0`
- `ProtenixFourierEmbedding` 输出：
  - `[..., N_sample, c]`

## 典型调用位置

- Protenix `get_pairformer_output` 的 input embedder
- Protenix recycling loop 的 template 分支
- Protenix diffusion conditioning 的 noise embedding

## 典型参数

- Protenix 主模型输入
  - `OneEmbedding(style="ProtenixInputFeatureEmbedder", **configs.model.input_embedder)`
- Protenix template
  - `OneEmbedding(style="ProtenixTemplateEmbedder", **configs.model.template_embedder)`
- Protenix diffusion noise
  - `ProtenixFourierEmbedding(c=256)`

## 风险点

- `ProtenixInputFeatureEmbedder` 输出维度会影响 `configs.c_s_inputs`，二者必须一致
- template 分支当前实现偏占位，不能假设只开 `n_blocks` 就有完整模板贡献
- Fourier embedding 的 `w/b` 是不可训练参数，改变 seed 会改变 noise 条件基底

## 源码锚点

- `./onescience/src/onescience/modules/embedding/oneembedding.py`
- `./onescience/src/onescience/modules/embedding/protenixembedding.py`
- `./onescience/src/onescience/modules/encoder/protenixencoding.py`
