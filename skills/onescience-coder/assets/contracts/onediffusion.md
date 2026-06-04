# Contract: OneDiffusion

## 基本信息

- 组件名：`OneDiffusion`
- 所属模块族：`diffusion`
- 统一入口：`direct_import`
- 注册名：`style="<DiffusionStyle>"`

## 组件职责

为 diffusion 类模块提供统一入口，当前同时包含通用 diffusion module 和 Protenix diffusion 模块。

补充说明：

- Protenix 中使用 `style="ProtenixDiffusionModule"`
- `ProtenixDiffusionConditioning` 与 `ProtenixDiffusionSchedule` 也在 registry 中，但主模型调用的是 module
- wrapper 不处理采样循环，采样循环在 Protenix generator / model 中组织

## 支持输入

- 2D 输入：`depends_on_style`
- 3D 输入：`depends_on_style`
- Protenix diffusion 输入：
  - `x_noisy`: `[..., N_sample, N_atom, 3]`
  - `t_hat_noise_level`: `[..., N_sample]`
  - `input_feature_dict`
  - `s_inputs`: `[..., N_token, c_s_inputs]`
  - `s_trunk`: `[..., N_token, c_s]`
  - `z_trunk`: `[..., N_token, N_token, c_z]`

内部统一做法：

- 检查 `style` 并实例化具体 diffusion 类
- forward 时透传所有参数

## 构造参数

- `style`
  - `DiffusionModule`
  - `ProtenixDiffusionConditioning`
  - `ProtenixDiffusionSchedule`
  - `ProtenixDiffusionModule`
- `**kwargs`
  - 由具体实现决定

## 输出约定

- `ProtenixDiffusionModule.forward` 输出 denoised coordinates：
  - `[..., N_sample, N_atom, 3]`

如果有明确边界条件，也写在这里：

- 采样步数、noise schedule、`N_sample` 不在 `OneDiffusion` wrapper 内配置
- 原子坐标尺度会经过 `sigma_data` 相关缩放

## 典型调用位置

- Protenix inference loop 中的 `sample_diffusion`
- Protenix training loop 中的 `sample_diffusion_training`

## 典型参数

- Protenix diffusion module
  - `style="ProtenixDiffusionModule"`
  - `sigma_data=16.0`
  - `c_atom=128`
  - `c_atompair=16`
  - `c_token=768`
  - `c_s=384`
  - `c_z=128`
  - `c_s_inputs=449`

## 风险点

- `OneDiffusion` 只是模块入口，不是完整 diffusion sampler
- `ProtenixDiffusionModule` 同时依赖 atom attention encoder、diffusion transformer 和 atom attention decoder，缺任一特征都会在深层报错
- `N_atom` 和 `N_token` 通过 `atom_to_token_idx` 等字段耦合，不能只检查坐标 shape

## 源码锚点

- `{onescience_path}/onescience/src/onescience/modules/diffusion/onediffusion.py`
- `{onescience_path}/onescience/src/onescience/modules/diffusion/protenixdiffusion.py`
- `{onescience_path}/onescience/src/onescience/models/protenix/generator.py`
