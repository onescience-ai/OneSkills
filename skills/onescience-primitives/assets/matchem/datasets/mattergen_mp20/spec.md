## content_principle
描述 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/mattergen/cache/mp_20` 的 MatterGen MP20 缓存，面向周期晶体生成和属性条件化。2026-11-05 读取全部数组的形状/属性有效数并检查 split ID；此缓存不含已确认的总势能、forces 或 stress 标签，不将其描述为完整原子势训练集。

## data_schema
| 文件 | dtype/形状 | 语义 |
| --- | --- | --- |
| `num_atoms.npy` | int64 `(S,)` | 每结构原子数 |
| `structure_id.npy` | Unicode `<U10` `(S,)` | 与结构顺序对齐的来源 ID |
| `cell.npy` | float64 `(S,3,3)` | 晶胞矩阵 |
| `pos.npy` | float64 `(sumN,3)` | 按结构连接的原子分数坐标 |
| `atomic_numbers.npy` | int64 `(sumN,)` | 与坐标同顺序的 atomic numbers |
| 四类属性 JSON | `{values,property_source_doc_id,origins}` | values 长度 S，origins 可为 null，values 可含 NaN |

结构 i 的原子段由 `offsets = [0] + cumsum(num_atoms)` 给出，切片为 `[offsets[i]:offsets[i+1]]`。`pos` 已与 sibling raw `mattergen/raw/mp_20/val.csv` 同 ID CIF 的元素/分数坐标集合和 cell metric 交叉核实，不能当作笛卡尔 Å 坐标；行向量约定下转换为 `cart = frac @ cell`。原始 CIF 与缓存的原子顺序可能不同。

## directory_layout
```text
mattergen/cache/mp_20/
  train/
  val/
  test/
    # 每个 split 均有以下文件
    pos.npy
    atomic_numbers.npy
    num_atoms.npy
    cell.npy
    structure_id.npy
    formation_energy_per_atom.json
    dft_band_gap.json
    dft_bulk_modulus.json
    dft_mag_density.json
```

## storage_format
数值数组为 NumPy NPY，推荐 `np.load(..., mmap_mode='r', allow_pickle=False)`。属性文件为含裸 NaN 的本地 JSON，严格 JSON 消费者须在中间产物中显式转换为 null 并保留有效性 mask，不能修改源文件。JSON values 通过结构索引对齐，不通过扁平原子索引对齐。

## scale_spec
| split | 结构数 S | 原子总数 sumN |
| --- | ---: | ---: |
| train | 27,136 | 279,553 |
| val | 9,047 | 92,454 |
| test | 9,046 | 92,085 |
| 合计 | 45,229 | 464,092 |
每结构 1–20 原子。各 split 的 structure_id 集合两两交集均为 0；这不替代进一步的对称等价/近重复结构审计。

## coverage_spec
覆盖 MP20 小晶胞晶体及 formation energy、band gap、bulk modulus、magnetic density 条件属性。元素覆盖和筛选来源以实际数组与 `property_source_doc_id` 为准；不等同 Materials Project 全库或 MatterGen 所有数据版本。

## label_spec
`formation_energy_per_atom`、`dft_band_gap` 在各 split 均为有限值。`dft_bulk_modulus` 有效数为 train 3,418、val 1,152、test 1,166；`dft_mag_density` 为 train 26,117、val 8,694、test 8,716。缺失值使用条件 mask，不能填零作为测量标签。形成能/原子不能直接乘 N 作为 MLIP 总势能；具体属性单位、计算方法需依据 property_source_doc_id 与模型协议确认，缓存没有完整单位声明。

## split_strategy
保持 train/val/test 官方缓存视图及 structure_id，不重新混洗三份数据。生成模型统计和条件缩放只从 train 估计，test 仅用于最终评估。抽取条件子集时记录有效值筛选规则和保留 ID，分别报告属性缺失覆盖。

## constraints
- 原子扁平数组必须按 num_atoms 累积切片，不能一行当一结构。
- 分数坐标局部可略小于 0 或大于 1，必要时按周期映射处理，不直接裁剪。
- 不从空缺属性生成零标签，不凭属性名称假定单位；数据许可需核对上游 MatterGen/MP20 条款。
- 未提供 force/stress 的缓存不能直接启用对应监督或声称可用于完整 MLIP 训练。
