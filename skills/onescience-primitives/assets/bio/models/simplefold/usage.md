# launch

SimpleFold 是 Lightning 完整流匹配结构模型，内部架构为 `FoldingDiT`。训练器调用 `training_step`；推理器将原始 batch 交给 `predict_step`，由 processor、ESM 条件、sampler 和 EMA 模型共同完成采样。

```sh
python -c "from onescience.models.simplefold.simplefold import SimpleFold; from onescience.models.simplefold.torch.architecture import FoldingDiT; import inspect; print(inspect.signature(SimpleFold)); print(inspect.signature(SimpleFold.training_step)); print(inspect.signature(SimpleFold.predict_step)); print(inspect.signature(FoldingDiT)); print(inspect.signature(FoldingDiT.forward))"
```

# input_schema

- `SimpleFold` 构造需要 `architecture`、特征 `processor`、flow-matching `loss/path/sampler`；训练还需 optimizer/scheduler。
- `FoldingDiT.forward(noised_pos, t, feats, self_cond=None)` 接受 `[batch, atoms, 3]` 噪声坐标、扩散时间和特征字典。
- 核心特征包括 `ref_pos`、`ref_charge`、`ref_element`、`ref_atom_name_chars`、`atom_pad_mask`、atom-to-token 映射、残基/实体/链/对称索引及 `esm_s`。
- 推理 batch 还可包含 `num_repeats`；processor 负责把序列/结构记录转换为上述模型特征。
- 架构输出为坐标/速度预测；`predict_step` 返回并可保存 sampler 生成的结构候选与置信度相关结果。

# runtime_interfaces

- `SimpleFold(...)`：组合训练、EMA、ESM 条件和采样逻辑的完整 Lightning 模型。
- `SimpleFold.training_step(batch, batch_idx)`：flow matching 或 pLDDT 训练入口。
- `SimpleFold.predict_step(batch, batch_idx)`：完整推理采样入口。
- `SimpleFold.configure_optimizers()`：创建训练优化器和调度器。
- `FoldingDiT.forward(noised_pos, t, feats, self_cond=None)`：底层去噪网络接口。

# main_functions

- `SimpleFold.training_step`
- `SimpleFold.predict_step`
- `SimpleFold.configure_optimizers`
- `FoldingDiT.forward`

# execution_resources

- 依赖 PyTorch、Lightning、ESM 权重、processor、flow path/sampler 及训练 checkpoint。
- 从 mmCIF/PDB 或结构样本构造训练/推理 batch 时，召回 datapipe 资源 `simplefold_data_pipeline`。
- 原子数、重复采样数、ESM 规模和 Transformer 宽度决定 GPU/DCU 显存。
- 推理应优先使用 checkpoint 中同步的 EMA 参数；训练环境可使用 FSDP。

# operation_limits

- 底层 `FoldingDiT` 不读取 FASTA 或保存结构，完整数据转换与采样由 `SimpleFold` 负责。
- ESM 模型名称、嵌入层数/宽度必须和架构配置一致。
- atom-to-token 映射、mask、参考原子属性或链索引错误会导致形状错误或无效结构。
- 预测坐标需结合 pLDDT、几何检查和独立验证使用。
