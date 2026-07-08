# launch

无条件结构生成示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/laproteina/infer_laproteina.py --config_name inference_ucond_tri --job_id 0 --data_path "$ONESCIENCE_DATASETS_DIR/la-proteina/dataset"
```

使用脚本包装器启动，未传 `--config_name` 时默认使用 `inference_ucond_tri`：

```sh
cd "$ONESCIENCE_DIR" && bash examples/biosciences/laproteina/scripts/run_generate.sh --job_id 0
```

训练主生成模型示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/laproteina/train_laproteina.py
```

# input_schema

- CLI 默认参数：
  - `--config_name=inference_base`
  - `--config_number=-1`
  - `--job_id=0`
  - `--config_subdir=None`
  - `--data_path=None`
- 常用无条件配置：
  - `run_name_=laproteina_ucond_tri`
  - `ckpt_path=${ONESCIENCE_DATASETS_DIR}/la-proteina/checkpoints_laproteina`
  - `ckpt_name=LD2_ucond_tri_512.ckpt`
  - `autoencoder_ckpt_path=${ONESCIENCE_DATASETS_DIR}/la-proteina/checkpoints_laproteina/AE1_ucond_512.ckpt`
  - `generation.args.nsteps=20`
  - `generation.args.self_cond=false`
  - `generation.args.guidance_w=1.0`
  - `generation.args.ag_ratio=0.0`
  - `generation.dataset.nlens_cfg.nres_lens=[100]`
  - `generation.dataset.nsamples=2`
  - `generation.dataset.max_nsamples_per_batch=1`
- motif 配置需要额外准备：
  - motif PDB
  - contig 或 atom-level motif specification
  - `motif_task_name`
  - atom selection mode，如 `ca_only`、`all`、`backbone`、`sidechain`、`tip_atoms`、`random`

# runtime_interfaces

- `parse_args_and_cfg`: 解析 CLI 并加载 Hydra 配置。
- `setup`: 检查 CUDA、创建输出目录、设置随机种子。
- `load_ckpt_n_configure_inference`: 加载 `Proteina` checkpoint 和 autoguidance 模型。
- `Proteina.configure_inference`: 设置推理配置与 guidance 模型。
- `Proteina.predict_step`: 调用 flow matching 采样并返回结构样本。
- `Proteina.sample_formatting`: 将 product-space 样本转换为 atom37/PDB 友好格式。
- `save_predictions`: 保存无条件生成 PDB。
- `save_motif_predictions`: 保存 motif 条件生成 PDB。

# main_functions

- `configure_inference`
- `predict_for_sampling`
- `predict_step`
- `sample_formatting`
- `save_predictions`
- `save_motif_predictions`
- `load_ckpt_n_configure_inference`

# execution_resources

- 需要 GPU；源码 setup 中断言 CUDA 可用。
- 需要模型 checkpoint、autoencoder checkpoint 和可访问的数据目录。
- motif 任务需要 motif PDB 和配置中指定的 motif 信息。
- designability/codesignability 指标需要额外折叠模型，通常显著增加运行时间。
- 多 GPU 环境中 wrapper 会设置 `CUDA_VISIBLE_DEVICES`，Lightning 推理可使用所有可见 GPU。

# operation_limits

- LaProteina 生成结构候选，不是给定 FASTA 的结构预测模型。
- 部分输出 residue type 可能是生成过程中的占位或与 backbone 共设计相关，后续仍需要序列设计和结构验证。
- `ag_ratio>0` 需要提供有效的 autoguidance checkpoint，否则配置检查会失败。
- motif scaffolding 的成功取决于 motif 原子选择和链/残基编号映射。
- 指标中 designability 与 FID 不能在同一推理配置中同时启用。
