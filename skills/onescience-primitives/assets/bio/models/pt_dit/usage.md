# launch

de novo 蛋白序列-结构协同生成示例:

```sh
python onescience/examples/biosciences/pt_dit/example_scripts/de_novo_design.py --nres 256 --nsample_per_device 8 --output_dir ./outputs/pt_dit --embeddings_dir onescience/examples/biosciences/pt_dit/embeddings --ckpt_path ./ckpts/PT_DiT_params_2000000.pkl --protoken_ckpt_path ./ckpts/protoken_params_100000.pkl --seed 8888 --n_eq_steps 50 --phasing_time 250 --decode_structures
```

# input_schema

- 常用默认/显式参数:
  - `nres=256`。
  - `nsample_per_device=8`。
  - `num_diffusion_timesteps=500`。
  - `PT_DiT_params_2000000.pkl`。
  - `protoken_params_100000.pkl`。
- 必需资源:
  - `protoken_emb.pkl`。
  - `aatype_emb.pkl`。
  - PT-DiT checkpoint。
  - ProToken checkpoint。
- 可选:
  - 是否 `decode_structures`。
  - RePaint / latent interpolation 相关 notebook 配置。

# runtime_interfaces

- `de_novo_design.py`: de novo co-design 示例入口。
- `DeNovoDesign`: 加载模型、采样和索引恢复封装。
- `DiffusionTransformer`: denoise 网络。
- `GaussianDiffusion`: diffusion scheduler。
- ProToken decode: token indexes 到 PDB。

# main_functions

- `main`
- `q_sample`
- `p_mean_variance`
- `ddim_sample`
- `apply_rope`

# execution_resources

- 需要 JAX/Flax、PT-DiT checkpoint、ProToken checkpoint、embedding pickle。
- 推荐 GPU；多设备 pmap 时 batch 需和设备数匹配。
- 解码结构还需要 ProToken decoder 资源。

# operation_limits

- 不能脱离 ProToken embedding 和 checkpoint 独立使用。
- `nres` 与 flash attention、ProToken padding 和 checkpoint config 要一致。
- 输出 token/latent 需要后续结构解码与质量评估。
- 不替代 AlphaFold/AlphaFold3 的结构预测，也不替代 ProteinMPNN 的条件序列设计。
