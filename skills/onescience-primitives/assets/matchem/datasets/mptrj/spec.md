## content_principle
本原语描述用户指定的 `/work2/share/sugonhpcapp01/OneData/wangrui10/matchem/datasets/mptrj/` 本地 MPtrj 数据包。它同时保存 `MPtrj_2022.9_full.json` 和过滤后训练视图；各格式可能对应相同构型，不能合并计数为互不重复的新数据。适合材料原子势的能量、力及有效应力监督，不把文件名或字段存在当作标签完整性的证明。以下计数及 schema 于 2026-11-05 只读核查。

## data_schema
| 视图 | 已核实的原始字段与含义 |
| --- | --- |
| extxyz | 原子级 `species`, `pos(N,3)`, `forces(N,3)`，部分帧有 `magmoms(N,)`；结构级 `Lattice`, `pbc`, `energy`, `stress` |
| extxyz 附加信息 | `bandgap`, `e_per_atom_relaxed`, `mp_id`, `energy_per_atom`, `ef_per_atom_relaxed`, `corrected_total_energy`, `ef_per_atom`, `task_id`, `calc_id`, `ionic_step` |
| HDF5 构型 | `config_batch_0/config_<id>/{atomic_numbers,positions,cell,pbc,config_type,weight,properties,property_weights}`；前四者为 `(N,)`, `(N,3)`, `(3,3)`, `(3,)` |
| HDF5 properties | 子键 `charges,dipole,energy,forces,head,stress,virials`；有效数值与占位符须逐字段区分，并应用同名 `property_weights` |
| ASELMDB 解码记录 | `numbers,positions,pbc,cell,energy,forces,stress`，原始附加信息保存在 `data` 字典 |
| 原始 JSON | 抽样前缀为材料 `mp-...` 到计算/离子步记录的嵌套映射，`structure` 含 pymatgen lattice/sites；未全量解析原始 JSON |

ASE 可能将 `energy/forces/stress/magmoms` 放在 `atoms.calc.results`，不能只读 `atoms.info` 或 `atoms.arrays`。首个 HDF5 构型中 `charges,dipole,head,virials` 的值为字节串 `None`，其中 charges/dipole/virials 权重为 0；这些字段不能转成零值监督。

## directory_layout
```text
mptrj/
  MPtrj_2022.9_full.json
  train_filtered.extxyz
  val_filtered.extxyz
  train_smoke_1000_filtered.extxyz
  hdf5_filtered/
    train/train_0.h5 ... train_7.h5
    val/val_0.h5 ... val_7.h5
    test/                         # 核查时无 HDF5 分片
    statistics.json
  aselmdb_mptrj/
    train/data_00000.aselmdb ... data_00007.aselmdb
    val/data_00000.aselmdb ... data_00007.aselmdb
    train/metadata.json
    val/metadata.json
```

## storage_format
extxyz 用 ASE 逐帧读取；HDF5 用 h5py 按构型组访问。ASELMDB 是单文件 LMDB，`subdir=False`，样本 key 为十进制 ID 字符串，另有 `nextid`；value 为 zlib 压缩的 ASE JSON，解码链为 `ase.io.jsonio.decode(zlib.decompress(value).decode())`，不是 OMat24 的 MessagePack。key 的字典序不等于数值顺序或轨迹时间顺序。原始 JSON 约 12.19 GB，应流式解析。

## scale_spec
全部 16 个 HDF5 分片的构型组计数为 train **1,500,252**、val **78,194**，分别各 8 个 shard；ASELMDB 的 `structures_written` 与这两个总数一致。该一致性不等于逐构型内容对齐验证。`train_smoke_1000_filtered.extxyz` 完整扫描实为 **974 帧**。主 extxyz 文件约 5.90 GB 和 0.30 GB，未再全量逐帧验证其总数；不要从 HDF5 数字自动推断所有格式严格一一对应。

## coverage_spec
本地数据覆盖多元素周期材料及其构型/离子步信息；`mp_id/task_id/calc_id/ionic_step` 可辅助追踪来源和分组。原始完整包、过滤视图和 smoke 子集的覆盖范围不同，不能把 smoke 中元素集合视为全量元素表。

## label_spec
主要监督是 `energy`、`forces` 和有效 `stress`。必须区分 raw total energy、`corrected_total_energy`、`energy_per_atom`、形成能和 relaxed 属性。例如 val 首帧 4 原子的 `energy=-23.083601`，`corrected_total_energy=-22.941601`，`energy_per_atom=-5.73540025` 对应后者。训练与评测使用同一能量定义，不得交叉替代。单位和应力符号需与来源/adapter 协议核对；ASE 常用单位约定不能替代来源证明。

## split_strategy
保留本地 train/val 划分；空 `test/` 目录不代表已有测试集。进一步用材料 ID、计算 ID 或轨迹组检查离子步泄漏；若需独立测试集，从训练来源组重新制定、保存划分清单，并保留原 split。不同格式顺序不可假定一致，跨格式 join 必须使用可验证的来源 ID/结构指纹。

## constraints
- 不得将 `None` 占位、缺失属性或零权重项加入有效监督；`head` 也不是数值物理标签。
- stress 六分量与矩阵、virial 间的转换须固定 Voigt 顺序、符号和体积口径。
- `statistics.json` 的 `atomic_numbers/atomic_energies` 是字符串化内容，禁止直接 `eval`；`r_max=6.0` 等为该转换视图的统计配置，不能自动用于所有模型。
- 复用前核实 MPtrj/Materials Project 的实际来源版本与使用许可；本地可读不代表可再分发。
