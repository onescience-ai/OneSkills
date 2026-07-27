## content_principle
MatRIS 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/matris` 下的声子和热力学参考表。它不是原子结构轨迹集合，而是以材料 ID 为主键的性质回归/评测表。

## data_schema
CSV 表字段如下：

```text
mp_id, nsites, energy_pa, volume_pa, entropy, heat_capacity,
free_energy, max_freq, avg_freq, stable
```

字段含义：

- `mp_id`：Materials Project 风格材料 ID。
- `nsites`：结构中的原子位点数。
- `energy_pa`：每原子能量。
- `volume_pa`：每原子体积。
- `entropy`：熵相关标量。
- `heat_capacity`：热容相关标量。
- `free_energy`：自由能。
- `max_freq`：最大声子频率。
- `avg_freq`：平均声子频率。
- `stable`：稳定性布尔标签。

## directory_layout
```text
/matchem/matris
├── pbe_phonon_ref.csv
└── pbesol_phonon_ref.csv
```

## storage_format
主格式为 CSV。每行对应一个材料 ID 的性质记录，不直接包含原子坐标、晶胞矩阵或元素组成。若训练 MatRIS 结构模型，需要通过 `mp_id` 关联外部结构库或模型输入特征。

## scale_spec
规模按 CSV 行数统计；PBE 与 PBEsol 是两套计算泛函口径。训练前应分别统计行数、缺失值、`stable` 类别比例、目标分布和 `mp_id` 重合情况。

## coverage_spec
覆盖材料声子与热力学标量性质，可用于 MatRIS 预测头评测、性质回归、稳定性分类、PBE/PBEsol 口径比较和声子统计 benchmark。

## label_spec
回归标签包括 `energy_pa`、`volume_pa`、`entropy`、`heat_capacity`、`free_energy`、`max_freq`、`avg_freq`；分类标签为 `stable`。如果某列存在空值，训练时需要构造字段级 mask。

## split_strategy
建议按 `mp_id` 做材料级划分，确保同一材料不会同时出现在训练和测试。比较 PBE 与 PBEsol 时，应先确认同一 `mp_id` 是否同时存在于两张表，再决定是否做 paired evaluation。

## constraints
- CSV 不能直接作为 MACE/UMA 这类原子势模型的结构输入。
- `energy_pa` 是每原子能量，不能与结构级总能量损失混用。
- PBE 与 PBEsol 的计算口径不同，归一化统计和评测结果应分开记录。
- 缺失值和布尔字段类型需要在 datapipe 中显式处理。
