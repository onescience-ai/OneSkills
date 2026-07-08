# launch

MolSculptor 可通过小分子 inference 脚本、training 脚本或具体 case 脚本启动。下面是 PI3K de novo 生成示例:

```sh
python onescience/examples/biosciences/molsculptor/inference/diff_evo_denovo_pi3k.py --config_path ./configs/molsculptor_config.py --params_path ./ckpts/molsculptor_dit.pkl --logger_path ./outputs/molsculptor_pi3k/log.txt --save_path ./outputs/molsculptor_pi3k --total_step 100 --device_batch_size 8 --vae_config_path ./configs/molsculptor_vae.py --vae_params_path ./ckpts/molsculptor_vae.pkl --alphabet_path ./assets/molsculptor_alphabet.pkl --init_molecule_path onescience/examples/biosciences/molsculptor/cases/case_pi3k/padding_molecule_propane.pkl --num_latent_tokens 16 --dim_latent 32 --eq_steps 10 --callback_step 10 --beam_size 5 --sampling_method beam --n_replicate 1 --diffusion_timesteps 500
```

预训练 autoencoder 示例:

```sh
bash onescience/examples/biosciences/molsculptor/training/scripts/pretrain_ae.sh
```

# input_schema

- 小分子输入: SMILES、初始分子 pickle、分子图特征或 case-local 配置。
- docking case 输入: PDBQT receptor、DSDP 脚本、缓存路径和 reward 配置。
- 常用默认/显式参数:
  - `n_padding_atom=64` 用于图 padding。
  - `sampling_method` 可选 `greedy`、`beam`、`top_p`、`top_k`、`nucleus`。
  - `diffusion_timesteps` 来自 diffusion config。
  - `beam_size`、`top_k`、`top_p` 控制 SMILES 解码策略。

# runtime_interfaces

- `diff_evo_denovo_pi3k.py`: PI3K de novo 小分子生成入口。
- `diff_evo_opt_dual.py`: dual inhibitor 优化入口。
- `Inferencer`: 图编码与序列采样入口。
- `smi2graph_features`: SMILES 到 padded graph features。
- `GaussianDiffusion`: latent diffusion 调度。
- `dsdp_reward`: docking reward 计算。
- `NSGA_II`: 多目标候选选择。

# main_functions

- `infer`
- `smi2graph_features`
- `standardize`
- `encoding_graphs`
- `make_graph_feature`
- `tokens2smiles`
- `LogP_reward`
- `QED_reward`
- `SA_reward`
- `tanimoto_sim`
- `dsdp_reward`
- `NSGA_II`

# execution_resources

- 需要 JAX/Flax、RDKit、训练或推理 checkpoint、case 配置。
- docking reward 还依赖外部 docking 二进制、PDBQT 文件和 case 脚本。
- 批量生成和 diffusion sampling 推荐 GPU；reward 筛选可能偏 CPU/外部程序密集。

# operation_limits

- 不处理蛋白结构预测、蛋白 backbone 生成或 DNA/RNA 序列建模。
- SMILES 无效、sanitize 失败或图超出 padding 上限时需要过滤。
- docking case 的外部依赖不可在通用环境中假设存在。
- 生成分子不等于已验证药物候选，必须经过化学有效性和下游筛选。
