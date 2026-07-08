# component_info
`mace_radial` 是 MACE layer 族中的径向基与截断组件，定位为原子图边距离到径向特征的转换层。它通过 `RadialEmbeddingBlock` 或 pair repulsion 分支被 MACE 主干使用，关键特征是用可训练或固定基函数描述局部距离，并保证 cutoff 附近平滑衰减。

# purpose
- 用途：把边距离 `r` 展开为径向基特征，生成平滑 cutoff envelope，并可计算 ZBL 短程排斥能。
- 解决问题：为等变消息传递提供距离依赖的标量边特征，减少 cutoff 处不连续带来的训练和 MD 风险。
- 适用场景：MACE 边特征构造、ZBL pair repulsion、高压/碰撞构型的短程稳定性增强。
- 不适用场景：直接构图、球谐方向特征生成、能量聚合或 loss 计算。

# input_schema
- `r` / `x`: 边距离，形态通常为 `(NumEdges, 1)` 或 `(NumEdges,)`。
- `edge_index`: `(2, NumEdges)`，ZBL 分支用于定位原子对。
- `node_attrs`: `(NumAtoms, NumElements)`，ZBL 分支用于元素 one-hot。
- `atomic_numbers`: 元素表原子序数，需与 `node_attrs` 列顺序一致。
- 约束：距离单位按 Angstrom 语义使用，`r_max` 必须与构图 cutoff 保持一致。

# output_schema
- `BesselBasis` / `GaussianBasis` / `ChebychevBasis`: `(NumEdges, NumBasis)`。
- `PolynomialCutoff`: 可广播到边特征的 cutoff 权重，通常为 `(NumEdges,)` 或 `(NumEdges, 1)`。
- `ZBLBasis`: 逐原子短程排斥能贡献。
- `AgnesiTransform` / `SoftTransform`: 变换后的距离或距离特征。

# parameters
- `r_max`: 径向截断半径，必须与构图 cutoff 对齐。
- `num_basis`: 径向基数量。
- `num_bessel`: Bessel 基数量，demo 常见 `8`。
- `num_polynomial_cutoff`: 多项式 cutoff 阶数，常见 `5` 或 `6`。
- `p`: cutoff 平滑阶数。
- `trainable`: 基函数频率或中心是否可训练。
- `radial_type`: 径向基类型，常见 `"bessel"`。
- `distance_transform`: 距离变换类型，可用于短程数值调整。
- 典型值：`r_max=4.0~6.0`，`num_bessel=8`，`radial_type="bessel"`。

# key_dependencies
- `mace_block.py`
- `mace_func_utils.py`
- `scatter.py`
- `mace.py`

# usage_and_risks
- 典型使用：由 `RadialEmbeddingBlock` 在 MACE 边特征阶段调用，或在 `pair_repulsion=True` 时启用 `ZBLBasis`。
- 改 cutoff 时，需要同时修改数据构图 cutoff、训练配置和 checkpoint 兼容策略。
- 改径向基类型时，旧 checkpoint 的径向权重通常不能直接兼容。
- 启用 ZBL 时，必须确认元素 one-hot 与原子序数映射无错位。
- 距离接近 0 时可能出现数值不稳定，需要对高能近邻样本做额外验证。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/layer/mace_radial.py`
- `{onescience_path}/onescience/src/onescience/modules/block/mace_block.py`
