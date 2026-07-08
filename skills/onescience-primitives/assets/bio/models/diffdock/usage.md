# launch

DiffDock 通常通过 examples 中的采样脚本启动，配置文件中显式指定受体、配体、score 模型和采样参数：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/diffdock/scripts/sample_diffdock.py --config examples/biosciences/diffdock/configs/sampling.yml
```

训练 score 模型时使用训练脚本和 YAML 配置：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/diffdock/scripts/train_diffdock.py --config examples/biosciences/diffdock/configs/training.yml
```

Python API 加载 score 模型示例：

```python
from onescience.models.diffdock.score_wrapper import load_score_model

model, model_args, t_to_sigma = load_score_model(
    model_dir="${ONESCIENCE_DATASETS_DIR}/diffdock/score_model",
    ckpt="best_ema_inference_epoch_model.pt",
    no_parallel=True,
)
```

# input_schema

- 单复合物采样：
  - `input.complex_name`: 复合物名称，默认示例为 `6o5u_test`
  - `input.protein_path`: 受体 PDB 路径
  - `input.ligand_description`: 配体 SDF/MOL2 路径或 SMILES
  - `input.protein_sequence`: 可选蛋白序列
  - `input.lm_embeddings`: 可选语言模型嵌入
- CSV 批量采样：
  - `input.protein_ligand_csv`: CSV 路径
  - CSV 字段：`complex_name`、`protein_path`、`ligand_description`、`protein_sequence`
- 模型参数默认值：
  - `model.ckpt=best_ema_inference_epoch_model.pt`
  - `model.old_score_model=false`
  - `confidence.confidence_ckpt=best_model_epoch75.pt`
  - `sampling.samples_per_complex=10`
  - `sampling.batch_size=10`
  - `sampling.inference_steps=20`
  - `sampling.sigma_schedule=expbeta`
  - `sampling.no_final_step_noise=true`
  - `sampling.initial_noise_std_proportion=1.0`
  - `runtime.device=auto`

# runtime_interfaces

- `load_model_args`: 从模型目录读取 `model_parameters.yml`。
- `model_uses_lm_embeddings`: 判断模型参数是否依赖 ESM/语言模型嵌入。
- `build_score_model`: 根据模型参数构建 score 模型和噪声调度函数。
- `load_score_model`: 加载 checkpoint、EMA 权重并切换到 eval 模式。
- `CGModel.forward`: 默认粗粒度 score 预测入口。
- `AAModel.forward`: 全原子 score 预测入口。
- `CGModel.torsional_forward`: 仅计算扭转 score 的入口。

# main_functions

- `forward`
- `torsional_forward`
- `load_model_args`
- `model_uses_lm_embeddings`
- `build_score_model`
- `load_score_model`

# execution_resources

- 推荐 GPU；`samples_per_complex`、`batch_size`、交叉边数量和是否启用 confidence 模型会直接影响显存。
- 需要可读的 score 模型目录、checkpoint、`model_parameters.yml`、受体 PDB 和配体文件。
- 若配置中启用 ESM 嵌入，需要准备 ESM 依赖、缓存或预计算 embedding。
- 输出目录需要可写，采样会写入候选 pose、日志和可能的重排序结果。
- CPU 可用于小规模 smoke 测试，但实际采样通常会很慢。

# operation_limits

- 适用于小分子-蛋白对接，不适用于蛋白-蛋白、蛋白-核酸或从头药物生成。
- 采样质量依赖输入受体构象和口袋定义；未处理的全蛋白、大量异质原子或异常链编号可能导致图构建失败。
- confidence 重排序只能辅助筛选 pose，不能等同于实验亲和力验证。
- `AAModel` 部分高级分支未完整实现，默认优先走 `CGModel`。
- 配体无可旋转键时扭转输出为空，这是合法情况。
