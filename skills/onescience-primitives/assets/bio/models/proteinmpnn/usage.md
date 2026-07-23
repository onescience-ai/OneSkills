# launch

ProteinMPNN 是给定蛋白骨架的序列设计模型。完整设计接口位于 `protein_mpnn_utils.ProteinMPNN`，训练调用 `forward` 得到残基 log-probability，推理调用 `sample` 或 `tied_sample` 生成序列。

```sh
python -c "from onescience.models.proteinmpnn.protein_mpnn_utils import ProteinMPNN; import inspect; print(inspect.signature(ProteinMPNN)); print(inspect.signature(ProteinMPNN.forward)); print(inspect.signature(ProteinMPNN.sample)); print(inspect.signature(ProteinMPNN.tied_sample))"
```

# input_schema

- `X`：骨架坐标，通常为 `[batch, residues, atoms, 3]`；`ca_only=True` 时使用 CA 表示。
- `S`/`S_true`：残基 token；`mask` 为有效残基；`chain_M`/`chain_mask` 标记待设计位置。
- `residue_idx` 与 `chain_encoding_all` 编码链内位置和链身份；`randn` 决定自回归解码顺序。
- 可选约束包括 omit/bias amino acids、逐位 mask、PSSM、固定位置、同位点 tied constraints。
- `forward` 返回 `[batch, residues, num_letters]` 的 log-probability；`sample` 返回含生成序列、概率和解码顺序的字典。

# runtime_interfaces

- `ProteinMPNN(...)`：完整骨架条件序列模型。
- `ProteinMPNN.forward(X, S, mask, chain_M, residue_idx, chain_encoding_all, randn, ...)`：训练/序列评分入口。
- `ProteinMPNN.sample(...)`：常规序列采样。
- `ProteinMPNN.tied_sample(...)`：带 tied-position 约束的采样。
- `ProteinFeatures`：从骨架坐标构造邻接图和几何边特征。

# main_functions

- `ProteinMPNN.forward`
- `ProteinMPNN.sample`
- `ProteinMPNN.tied_sample`
- `ProteinFeatures.forward`

# execution_resources

- 依赖 PyTorch；上游需把结构解析成坐标、链 mask、残基编号和固定/设计位点。
- GPU 适合批量设计，单个短链可使用 CPU；`k_neighbors`、链长和 batch size 决定显存。
- checkpoint 必须和 `ca_only`、隐藏宽度、层数、邻居数及词表一致。

# operation_limits

- ProteinMPNN 设计序列，不预测或优化输入骨架坐标。
- 固定链、固定残基和 tied-position mask 错误会改变实际设计空间。
- 输出概率不是折叠稳定性或结合亲和力的直接测量，候选仍需结构预测和实验验证。
- 缺失骨架原子需通过 `mask` 明确处理，不能当作零坐标有效残基。
