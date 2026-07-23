# launch

DiffDock 的模型入口位于 `onescience.models.diffdock`。模型目录、checkpoint 与设备均由调用方显式传入：

```sh
python -c "from onescience.models.diffdock import build_score_model, load_model_args, load_score_model; from onescience.models.diffdock.cg_model import CGModel; import inspect; print(inspect.signature(load_model_args)); print(inspect.signature(build_score_model)); print(inspect.signature(load_score_model)); print(inspect.signature(CGModel.forward))"
```

# input_schema

- `model_dir`：包含 `model_parameters.yml` 的目录；`checkpoint_name` 为该目录下的 score 权重。
- `complex_batch`：DiffDock datapipe 生成的 PyG complex batch，至少包含 ligand/receptor 节点、坐标、边、batch、时间噪声特征与可选 LM embedding。
- 模型参数控制 `sigma_embed_dim`、`sh_lmax`、卷积层数、cross-distance cutoff、torsion 与 confidence 分支等结构。
- `CGModel.forward` 返回平移 score `(B, 3)`、旋转 score `(B, 3)` 和按可旋转键排列的 torsion score；confidence 配置可产生不同输出。

# runtime_interfaces

- `load_model_args(model_dir)`：读取模型配置。
- `model_uses_lm_embeddings(model_args)`：检查 datapipe 是否必须提供语言模型表征。
- `build_score_model(model_args, device, t_to_sigma, ...)`：构建未加载权重的 score 网络，供训练使用。
- `load_score_model(model_dir, ckpt, device, ...)`：构建、加载权重并切换到 eval。
- `CGModel.forward(data)`：粗粒度 score 入口。
- `CGModel.torsional_forward(data)`：仅计算扭转相关输出。

# main_functions

- `load_model_args`
- `model_uses_lm_embeddings`
- `build_score_model`
- `load_score_model`
- `forward`
- `torsional_forward`

# execution_resources

- 需要 PyTorch、PyG/e3nn 相关依赖、score checkpoint 和已构图的蛋白-配体 batch。
- 训练或推理代码需要数据构图知识时，召回 datapipe 资源 `biology_diffdock_dataset`；不要从 examples 查找数据入口。
- 推理采样还需由后续代码实现噪声 schedule、迭代更新、候选保存和可选 confidence 重排。
- 训练代码应使用 `build_score_model`，并从 datapipe 提供时间步、目标 score 和 loss 所需字段。

# operation_limits

- 模型只预测对接扩散 score，不负责读取 PDB/SDF、构图或完整采样循环。
- 适用于小分子-蛋白对接，不适用于蛋白-蛋白或从头分子生成。
- 配置中的 LM embedding、全原子/粗粒度和 torsion 选项必须与数据字段及 checkpoint 一致。
- 无可旋转键时 torsion 输出为空是合法结果。
