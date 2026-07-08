# launch
Python API 直接加载预训练模型并运行一个结构前向：

``` sh
python -c "import torch; from pymatgen.core import Lattice, Structure; from onescience.models.matris import MatRIS; device='cuda' if torch.cuda.is_available() else 'cpu'; model=MatRIS.load(model_name='matris_10m_oam', device=device); structure=Structure(Lattice.cubic(5.43), ['Si','Si'], [[0,0,0],[0.25,0.25,0.25]]); graph=model.graph_converter(structure).to(device); out=model([graph], task='efsm', is_training=False); print({k: type(v).__name__ for k,v in out.items()})"
```

Python API 从默认参数实例化轻量模型做 smoke test：

``` sh
python -c "from pymatgen.core import Lattice, Structure; from onescience.models.matris import MatRIS; model=MatRIS(num_layers=2, node_feat_dim=64, edge_feat_dim=64, three_body_feat_dim=64, mlp_hidden_dims=(64,64), dropout=0.0, use_bias=False, distance_expansion='Bessel', three_body_expansion='SH', num_radial=5, num_angular=5, max_l=4, max_n=4, envelope_exponent=8, graph_conv_mlp='GateMLP', activation_type='silu', norm_type='rms', pairwise_cutoff=5.0, three_body_cutoff=3.0, use_smoothed_for_delta_edge=False, learnable_basis=True, is_intensive=True, is_conservation=True, reference_energy=None); structure=Structure(Lattice.cubic(5.43), ['Si','Si'], [[0,0,0],[0.25,0.25,0.25]]); graph=model.graph_converter(structure); out=model([graph], task='efsm', is_training=False); print(out.keys())"
```

ASE calculator 方式适合能量、力、应力、磁矩调用：

``` sh
python -c "import torch; from ase.build import bulk; from onescience.utils.matris import MatRISCalculator; device='cuda' if torch.cuda.is_available() else 'cpu'; atoms=bulk('Cu', a=5.43, cubic=True); atoms.calc=MatRISCalculator(model='matris_10m_oam', task='efsm', device=device); print(atoms.get_potential_energy()); print(atoms.get_forces().shape); print(atoms.get_stress().shape); print(atoms.get_magnetic_moments().shape)"
```

# input_schema
结构输入准备：

- 推荐输入为 `pymatgen.core.Structure` 或 `ase.Atoms`。
- 直接调用模型时，先使用 `model.graph_converter(structure)` 或 `GraphConverter(atom_graph_cutoff, line_graph_cutoff)` 转为 `RadiusGraph`。
- 传给模型的是 `graphs: Sequence[RadiusGraph]`，即使只有一个结构也使用 `[graph]`。
- ASE 调用由 `MatRISCalculator` 自动将 `ase.Atoms` 转为 `pymatgen.Structure`，再转为 `RadiusGraph`。

forward 默认参数：

- `task="ef"`：默认输出能量和力。
- `is_training=False`：默认推理模式，不为高阶训练梯度保留计算图。

模型默认参数：

- `num_layers=6`
- `node_feat_dim=128`
- `edge_feat_dim=128`
- `three_body_feat_dim=128`
- `mlp_hidden_dims=(128, 128)`
- `dropout=0.0`
- `use_bias=False`
- `distance_expansion="Bessel"`
- `three_body_expansion="SH"`
- `num_radial=7`
- `num_angular=7`
- `max_l=4`
- `max_n=4`
- `envelope_exponent=8`
- `graph_conv_mlp="GateMLP"`
- `activation_type="silu"`
- `norm_type="rms"`
- `pairwise_cutoff=6`
- `three_body_cutoff=4`
- `use_smoothed_for_delta_edge=False`
- `learnable_basis=True`
- `is_intensive=True`
- `is_conservation=True`
- `reference_energy=None`

预训练加载默认参数：

- `MatRIS.load(model_name="matris_10m_oam", device=None)`。
- `device=None` 时自动选择 `"cuda"` 或 `"cpu"`。
- 本地权重路径优先级：`ONESCIENCE_MODELS_DIR/matris/<checkpoint_file>` 高于 `~/.cache/matris/<checkpoint_file>`。

任务字段：

- `task="e"`：只输出能量。
- `task="em"`：输出能量和磁矩。
- `task="ef"`：输出能量和力。
- `task="efs"`：输出能量、力、应力。
- `task="efsm"`：输出能量、力、应力、磁矩。

# runtime_interfaces
- `MatRIS(...)`：按结构参数构造模型和内部 `GraphConverter`。
- `MatRIS.forward(graphs, task="ef", is_training=False)`：主推理接口，返回预测字典。
- `MatRIS.load(model_name="matris_10m_oam", device=None)`：加载预训练 checkpoint。
- `MatRIS.from_dict(dct)`：从包含 `config` 和 `state_dict` 的 checkpoint 字典恢复模型。
- `MatRIS.get_params()`：返回模型参数量。
- `MatRISCalculator(model="matris_10m_oam", task="efs", device="cpu")`：ASE calculator 接口。
- `StructOptimizer(model, task, optimizer, device)`：结构弛豫封装。

# main_functions
- `forward`
- `load`
- `from_dict`
- `get_params`

# execution_resources
- CPU 可用于导入、实例化、单结构小规模 smoke test。
- 预训练模型和 `efsm` 推理建议使用 GPU；三体 line graph 较大时显存开销会快速增长。
- `task` 包含 `s` 时需要应变张量和能量梯度，资源需求高于 `e` 或 `ef`。
- `is_conservation=True` 时力和应力来自自动微分，需确保坐标和应变梯度链路完整。
- 运行预训练加载需要本地 checkpoint 或可访问下载地址；建议设置 `ONESCIENCE_MODELS_DIR` 管理模型文件。
- 典型依赖包括结构对象与 ASE 生态：`ase>=3.23.0`、`numpy>=2.0.0`、`pymatgen>2024.9.10`。

# operation_limits
- 模型输入不是裸 CIF/XYZ 文件；文件需先读成 `Structure` 或 `Atoms`，再转图。
- 当前 `MatRIS.load` 只接受 `matris_10m_oam` 和 `matris_10m_mp`。
- `matris_10m_omat` 在说明和字典中出现，但源码加载入口暂未开放支持。
- 非周期结构在 calculator 中会扩展 cell；直接使用 `GraphConverter` 时需要自行处理周期边界和 cell 合理性。
- `is_intensive=True` 时 `forward` 的 `e` 是每原子能量，ASE calculator 输出会换算成总能。
- 极端近邻、空邻接图或超大三体角图可能导致除零、空 line graph、显存不足或时间过长。
- 磁矩输出只在 `task` 包含 `m` 时计算，且由节点头直接预测，不等价于电子结构自洽求解。
