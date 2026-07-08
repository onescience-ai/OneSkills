# launch
该组件以 Python API 方式由 MACE 模型或统计脚本调用：

``` python
from onescience.modules.func_utils.mace_func_utils import get_edge_vectors_and_lengths, get_outputs

edge_vectors, lengths = get_edge_vectors_and_lengths(
    positions=data["positions"],
    edge_index=data["edge_index"],
    shifts=data["shifts"],
)
outputs = get_outputs(
    energy=energy,
    positions=data["positions"],
    displacement=displacement,
    cell=data["cell"],
    training=False,
    compute_force=True,
    compute_virials=False,
    compute_stress=False,
    compute_hessian=False,
)
```

完整训练中由模型 forward 间接触发：

``` sh
python examples/matchem/mace/train.py --model=MACE --compute_forces=True --compute_stress=False --compute_virials=False --num_interactions=2 --num_channels=64 --max_L=0 --correlation=3 --r_max=6.0 --train_file="${ONESCIENCE_DATASETS_DIR}/matchem/mace/water/water_train.xyz" --valid_fraction=0.05 --test_file="${ONESCIENCE_DATASETS_DIR}/matchem/mace/water/water_test.xyz" --energy_key=TolEnergy --forces_key=force --E0s=isolated --batch_size=2 --device=cuda
```

# input_schema
运行输入准备：

图字段
  positions: (NumAtoms, 3)
    需要 forces 时保留梯度
  edge_index: (2, NumEdges)
    有向邻接边
  shifts / unit_shifts: (NumEdges, 3)
    周期边偏移
  batch: (NumAtoms,)
    原子到构型映射
  cell: (NumGraphs, 3, 3)
    stress / virial 需要

能量导数
  energy: (NumGraphs,) 或 (NumGraphs, NumHeads)
    -> compute_forces
    -> compute_virials / compute_stress
    -> compute_hessians

统计输入
  data_loader
    -> AtomicEnergiesBlock
    -> mean/std/rms/avg_num_neighbors

# runtime_interfaces
- `prepare_graph(data, compute_virials, compute_stress, compute_displacement, ...)`：生成图上下文与导数所需 displacement。
- `get_edge_vectors_and_lengths(positions, edge_index, shifts, normalize=False, eps=...)`：计算边向量和距离。
- `get_outputs(energy, positions, displacement, cell, training, ...)`：从能量导出物理量。
- `compute_forces(energy, positions, training=False)`：计算力。
- `compute_forces_virials(energy, positions, displacement, training=False)`：计算力和 virial。
- `get_symmetric_displacement(...)`：构造对称晶胞扰动。
- `compute_hessians_vmap` / `compute_hessians_loop`：计算 Hessian。
- `get_atomic_virials_stresses(...)`：计算逐原子 virial/stress。
- `compute_statistics(...)`：计算训练统计量。
- `compute_avg_num_neighbors(data_loader)`：计算平均邻居数。

# main_functions
- `prepare_graph`
- `get_edge_vectors_and_lengths`
- `get_outputs`
- `compute_forces`
- `compute_forces_virials`
- `get_symmetric_displacement`
- `compute_hessians_vmap`
- `compute_hessians_loop`
- `get_atomic_virials_stresses`
- `compute_statistics`
- `compute_avg_num_neighbors`
- `extract_invariant`
- `compute_fixed_charge_dipole`

# execution_resources
- forces 需要一阶自动微分，显存高于 energy-only。
- stress/virial 需要 displacement 或 cell 梯度，显存和计算时间进一步增加。
- Hessian 是二阶导，通常只适合小体系或离线分析。
- 统计量计算可在 CPU 或 GPU 上执行，但大数据集建议分批运行。
- LAMMPS/MLIAP 路径需要与部署端 batch 和 ghost atom 语义一致。

# operation_limits
- 输入图必须已构建完成，该组件不负责邻居搜索。
- `positions` 不可在求力前断开 autograd。
- PBC 偏移和 cell 必须同源，否则 stress/virial 物理含义错误。
- 多头能量求导时需要确认选择的 energy 与 head 语义一致。
- Hessian 和逐原子 stress 不适合默认训练循环。
