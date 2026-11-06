## content_principle
描述 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/esen/oxides/` 的 eSEN 氧化物本地小样本微调集合。2026-11-05 只读核查全部 295 行的 oxide/polymorph 分组与 manifest 一致；它不等同 eSEN 的完整预训练语料。卡片保留本地转换后字段和既有分组测试协议。

## data_schema
结构存于 ASE SQLite `systems` 表，包含 `numbers(N,)`、`positions(N,3)`、`cell(3,3)`、`pbc`、标量 `energy`、`forces(N,3)` 和 `stress`。抽样 stress 为 6 分量，应通过 ASE 接口解码，不把 SQLite blob 直接当无结构数组。`key_value_pairs` 含 `oxide`, `polymorph`, `xc`，首条 `xc='PBE'`；这些列用于分组和方法溯源，不是预测标签。表存在 charges/dipole 等可选列不代表其有有效值。

## directory_layout
```text
esen/oxides/
  manifest.json
  train.db
  val.db
  test.db
```
manifest 记录 counts、groups、seed、split_strategy、stress_source_unit、stress_output_unit 和本地来源路径。

## storage_format
`.db` 是 ASE SQLite 数据库，不是 LMDB。ASE 消费端可用 `ase.db` 按 row 读取；底层核查可用 `sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)` 强制只读。`pbc` 在 SQLite 原始列中为编码值，须解码为三个方向的布尔量。

## scale_spec
train **238**、val **28**、test **29**，合计 **295** 条。30 个 oxide/polymorph 组被分为 24/3/3 组，manifest 的策略字符串为 `oxide-polymorph grouped 80/10/10`、seed 为 42；这是按组比例，不要求每份样本数恰好 80/10/10。

## coverage_spec
五种氧化物 `IrO2,RuO2,SnO2,TiO2,VO2`，六种多晶型 `anatase,brookite,columbite,fluorite,pyrite,rutile`。用于氧化物微调与未见 oxide/polymorph 组合泛化；不代表未见元素或全新氧化物化学式测试，因为同一 oxide 可出现在多个 split。

## label_spec
核心为 energy、forces、stress。manifest 明确 `stress_source_unit='GPa'`、`stress_output_unit='eV/Angstrom^3'`，本库使用已转换输出，不重复从 GPa 换算。能量/力源单位、应力符号和六分量 Voigt 顺序仍需与实际转换/消费协议核对，不能只因 ASE 格式推断来源已完成所有规范化。

## split_strategy
严格保留 manifest 的组分配。val 组为 `RuO2/brookite`、`RuO2/columbite`、`TiO2/rutile`；test 组为 `IrO2/anatase`、`IrO2/fluorite`、`TiO2/columbite`；其它 24 组为 train。本次逐行验证未发现组分配不符。新增样本必须按组归入对应 split，不随机拆散相同组来提高分数。

## constraints
- 不把小样本氧化物微调包描述为 eSEN 全量或独立元素外推基准。
- 不因 SQLite 可选列存在就启用缺失的电荷、磁矩等监督；转换后应力不可二次缩放。
- manifest.source 指向生成时引用的 supporting-information.json，不代表该外部路径在当前环境一定可读或为本次新增数据。
- 不改写源库或 split；使用许可与来源版本需复用前核实。
