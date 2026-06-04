# Contract: ProtenixDiffusion

## 基本信息

- 组件名：`ProtenixDiffusionConditioning / ProtenixDiffusionSchedule / ProtenixDiffusionModule`
- 所属模块族：`diffusion`
- 统一入口：`OneDiffusion`
- 注册名：`style="ProtenixDiffusionConditioning"`, `style="ProtenixDiffusionSchedule"`, `style="ProtenixDiffusionModule"`

## 组件职责

Protenix diffusion 组件负责从 trunk 表征和噪声坐标中生成去噪后的原子坐标，是 Protenix 结构生成阶段的核心模块。

补充说明：

- `ProtenixDiffusionConditioning` 把 `s_inputs/s_trunk/z_trunk` 和 noise level 转成 diffusion 条件
- `ProtenixDiffusionSchedule` 定义训练和推理噪声 schedule
- `ProtenixDiffusionModule` 执行一次 denoising step，完整采样循环由 Protenix generator 调用

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`not_applicable`
- diffusion step 输入：
  - `x_noisy`: `[..., N_sample, N_atom, 3]`
  - `t_hat_noise_level`: `[..., N_sample]`
  - `input_feature_dict`
  - `s_inputs`: `[..., N_token, c_s_inputs]`
  - `s_trunk`: `[..., N_token, c_s]`
  - `z_trunk`: `[..., N_token, N_token, c_z]`

内部统一做法：

- 先按 `sigma_data` 缩放 noisy coordinates
- diffusion conditioning 构造 conditioned `single_s` 与 `pair_z`
- atom attention encoder 把 noisy atom 坐标和 trunk 条件变成 token 表征
- diffusion transformer 更新 token 表征
- atom attention decoder 输出 atom coordinate update
- 将 update 与输入坐标按 noise ratio 合成 denoised coordinates

## 构造参数

- `sigma_data=16.0`
- `c_atom=128`
- `c_atompair=16`
- `c_token=768`
- `c_s=384`
- `c_z=128`
- `c_s_inputs=449`
- `atom_encoder`
  - 默认 `{"n_blocks": 3, "n_heads": 4}`
- `transformer`
  - 默认 `{"n_blocks": 24, "n_heads": 16, "drop_path_rate": 0}`
- `atom_decoder`
  - 默认 `{"n_blocks": 3, "n_heads": 4}`
- `blocks_per_ckpt`
- `use_fine_grained_checkpoint`

## 输出约定

- `ProtenixDiffusionModule.forward` 输出：
  - `x_denoised`: `[..., N_sample, N_atom, 3]`
- `f_forward` 输出：
  - `r_update`: `[..., N_sample, N_atom, 3]`

如果有明确边界条件，也写在这里：

- `t_hat_noise_level.size(-1)` 必须等于 `N_sample`
- `input_feature_dict` 中的 atom-token 映射必须覆盖 `N_atom` 与 `N_token`

## 典型调用位置

- Protenix inference: `sample_diffusion(...)`
- Protenix training: `sample_diffusion_training(...)`
- Confidence head 前的 mini-rollout

## 典型参数

- Protenix 主模型：
  - `OneDiffusion(style="ProtenixDiffusionModule", **configs.model.diffusion_module)`
- 推理脚本常见：
  - `sample_diffusion.N_sample=5`
  - `sample_diffusion.N_step=200`

## 风险点

- diffusion module 不是完整采样器，不能只调用一次 forward 就等同完整结构预测
- atom encoder / decoder 需要 `ref_pos/ref_mask/ref_element/ref_atom_name_chars/ref_space_uid/atom_to_token_idx` 等 Protenix feature
- 关闭 conditioning 或丢弃 trunk embedding 会改变模型行为，通常只应由训练配置控制

## 源码锚点

- `./onescience/src/onescience/modules/diffusion/onediffusion.py`
- `./onescience/src/onescience/modules/diffusion/protenixdiffusion.py`
- `./onescience/src/onescience/models/protenix/generator.py`
- `./onescience/src/onescience/models/protenix/protenix.py`
