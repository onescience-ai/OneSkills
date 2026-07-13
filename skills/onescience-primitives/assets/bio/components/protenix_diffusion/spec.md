# component_info

`protenix_diffusion` 是 Protenix 坐标生成核心组件族，统一入口为 `OneDiffusion`，注册名包括 `ProtenixDiffusionConditioning`、`ProtenixDiffusionSchedule` 和 `ProtenixDiffusionModule`。

# purpose

执行一次 denoising step，将 noisy atom coordinates、trunk 表征和 feature dict 转为去噪坐标。完整采样循环由 Protenix generator 调用，不由单个 forward 完成。

# input_schema

```text
x_noisy: [..., N_sample, N_atom, 3]
t_hat_noise_level: [..., N_sample]
input_feature_dict: Protenix feature dict
s_inputs: [..., N_token, c_s_inputs]
s_trunk: [..., N_token, c_s]
z_trunk: [..., N_token, N_token, c_z]
```

# output_schema

```text
x_denoised: [..., N_sample, N_atom, 3]
r_update: [..., N_sample, N_atom, 3]
```

# parameters

- `sigma_data=16.0`
- `c_atom=128`, `c_atompair=16`, `c_token=768`
- `c_s=384`, `c_z=128`, `c_s_inputs=449`
- `atom_encoder`, `transformer`, `atom_decoder`
- `blocks_per_ckpt`, `use_fine_grained_checkpoint`

# key_dependencies

- `onediffusion.py`
- `protenixdiffusion.py`
- `protenixencoding.py`
- `protenixtransformer.py`
- `protenixdecoder.py`

# usage_and_risks

不能只调用一次 forward 就等同完整结构预测；`t_hat_noise_level.size(-1)` 必须等于 `N_sample`；atom encoder/decoder 依赖 Protenix atom reference 和 atom-token mapping。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/diffusion/onediffusion.py`
- `{onescience_path}/onescience/src/onescience/modules/diffusion/protenixdiffusion.py`
- `{onescience_path}/onescience/src/onescience/models/protenix/generator.py`
- `{onescience_path}/onescience/src/onescience/models/protenix/protenix.py`
