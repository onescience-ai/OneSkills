# launch

Protenix 是 PyTorch 的 AlphaFold3 风格完整生物分子结构模型，组合输入嵌入、MSA、Pairformer、扩散结构生成和置信度头。代码构建应直接实例化 `Protenix`，训练和推理都通过 `forward` 的 `mode` 区分。

```sh
python -c "from onescience.models.protenix.protenix import Protenix; import inspect; print(inspect.signature(Protenix)); print(inspect.signature(Protenix.forward)); print(inspect.signature(Protenix.get_pairformer_output)); print(inspect.signature(Protenix.sample_diffusion)); print(inspect.signature(Protenix.run_confidence_head))"
```

# input_schema

- `configs` 必须包含模型各子模块、`N_cycle`、扩散 batch、训练/推理噪声调度、损失开关、chunk 与低内存配置。
- `input_feature_dict` 是 token/atom 级特征字典，包括残基/分子类型、原子到 token 映射、参考构象、序列/链索引、MSA/模板及 mask。
- 训练时 `label_dict` 为裁剪标签，`label_full_dict` 为完整标签，并需 `SymmetricPermutation` 和可复现的 `current_step`。
- `mode` 只能为 `train`、`inference` 或 `eval`。
- 返回 `(pred_dict, label_dict, log_dict)`；预测包含扩散坐标、pLDDT、PAE、PDE、resolved、distogram 等当前模式启用的字段。

# runtime_interfaces

- `Protenix(configs)`：完整模型。
- `Protenix.forward(...)`：训练、评估与推理统一入口。
- `Protenix.get_pairformer_output(...)`：recycling、MSA 和 Pairformer 主干。
- `Protenix.sample_diffusion(...)`：按推理噪声日程生成坐标样本。
- `Protenix.run_confidence_head(...)`：生成置信度预测。
- `SymmetricPermutation`：训练/评估时处理等价原子和链标签。

# main_functions

- `Protenix.forward`
- `Protenix.get_pairformer_output`
- `Protenix.sample_diffusion`
- `Protenix.run_confidence_head`

# execution_resources

- 依赖 PyTorch、预处理后的 Protenix 特征、相容 checkpoint 和完整配置树。
- 处理 JSON、PDB/mmCIF、MSA、CCD 或构造训练 dataloader 时，召回 datapipe 资源 `protenix_data_pipeline`。
- 推理资源主要由 token/atom 数、扩散步数、样本数、recycling 次数和 Pairformer chunk 决定。
- 训练通常需多 GPU/DCU，并要求标签置换、扩散损失和置信度训练配置一致。

# operation_limits

- `Protenix.forward` 不解析原始 FASTA/CCD/结构文件，上游必须生成完整特征契约。
- 推理模式仍要求传入字典形式的标签参数；无真实标签时应由调用方按源码 runner 契约提供空/占位字典，而不是伪造监督值。
- 对称置换、原子映射和链/token 索引错误会使训练标签或置信度失真。
- 坐标候选需结合置信度、化学合理性和实验信息解释。
