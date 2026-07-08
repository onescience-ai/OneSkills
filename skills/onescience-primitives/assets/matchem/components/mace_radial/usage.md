# launch
该组件以 Python API 作为 MACE 边特征构造的一部分使用：

``` python
import torch
from onescience.modules.layer.mace_radial import BesselBasis, PolynomialCutoff

edge_lengths = torch.rand(16, 1)
radial = BesselBasis(r_max=6.0, num_basis=8, trainable=False)
cutoff = PolynomialCutoff(r_max=6.0, p=6)
edge_feats = radial(edge_lengths) * cutoff(edge_lengths).unsqueeze(-1)
```

在完整模型中通过训练命令指定 cutoff：

``` sh
python examples/matchem/mace/train.py --model=MACE --r_max=6.0 --num_bessel=8 --num_polynomial_cutoff=6 --radial_type=bessel --num_interactions=2 --num_channels=64 --max_L=0 --correlation=3 --train_file="${ONESCIENCE_DATASETS_DIR}/matchem/mace/water/water_train.xyz" --valid_fraction=0.05 --test_file="${ONESCIENCE_DATASETS_DIR}/matchem/mace/water/water_test.xyz" --energy_key=TolEnergy --forces_key=force --E0s=isolated --batch_size=2 --max_num_epochs=10 --device=cuda
```

# input_schema
距离输入组织：

边几何
  positions + edge_index + shifts
    -> edge_vectors: (NumEdges, 3)
    -> edge_lengths: (NumEdges,)

径向展开
  edge_lengths
    -> Bessel/Gaussian/Chebychev basis
    -> radial_basis: (NumEdges, NumBasis)

平滑截断
  edge_lengths
    -> PolynomialCutoff
    -> cutoff_weight
    -> edge_feats = radial_basis * cutoff_weight

ZBL 分支
  edge_lengths + edge_index + node_attrs + atomic_numbers
    -> pair_node_energy

# runtime_interfaces
- `BesselBasis.forward(x)`：Bessel 径向基展开。
- `GaussianBasis.forward(x)`：Gaussian 径向基展开。
- `ChebychevBasis.forward(x)`：Chebychev 径向基展开。
- `PolynomialCutoff.forward(x)`：生成平滑 cutoff envelope。
- `ZBLBasis.forward(r, node_attrs, edge_index, atomic_numbers)`：计算短程排斥贡献。
- `AgnesiTransform.forward(x)`：执行 Agnesi 距离变换。
- `SoftTransform.compute_r_0(...)`：计算 soft transform 的参考距离。
- `SoftTransform.forward(...)`：执行 soft 距离变换。

# main_functions
- `forward`
- `compute_r_0`

# execution_resources
- 资源需求较轻，通常不是 MACE 的主要显存瓶颈。
- ZBL 分支依赖边数和元素映射，边数很大时会增加额外聚合开销。
- 需要与 MACE 构图、元素表和边特征管线保持一致。

# operation_limits
- `r_max` 与构图 cutoff 不一致会导致训练和推理邻域语义不一致。
- foundation fine-tuning 时改变 cutoff 会改变 receptive field，通常应避免。
- ZBL 只处理短程排斥贡献，不能替代完整相互作用模型。
- 输入距离为 0 或非常接近 0 时需要防止数值异常。
