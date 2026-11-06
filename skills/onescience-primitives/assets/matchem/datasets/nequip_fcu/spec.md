## content_principle
描述 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/NequIP/fcu.xyz` 的本地扩展 XYZ 集合。2026-11-05 全文件扫描帧数、原子数、元素和 Properties，并用 ASE 解析前三帧。仅将其绑定为 NequIP 目录中的具体数据，不宣称是 NequIP 官方完整基准或纯铜 FCC 体相数据；本地没有足够证据确认其生成方法、源单位和轨迹分组。

## data_schema
原子行由 `Properties=species:S:1:pos:R:3:forces:R:3` 定义，包括元素字符串、三维坐标和三维原子力。帧头含 `Lattice`、`pbc='T T T'` 和标量 `energy`。ASE 读取后 species/pos 映射为 atomic numbers/positions，energy/forces 通常在 `atoms.calc.results`；前三帧未读到 stress，不能假定存在应力监督。

## directory_layout
```text
matchem/NequIP/
  fcu.xyz
```
目录大小写为 `NequIP`，文件名 `fcu.xyz` 不能按名称自动推断元素组成或结构类型。

## storage_format
后缀虽为 `.xyz`，内容是带晶胞和标签的多帧 extxyz，使用 `ase.io.iread(path, format='extxyz')`。每帧首行原子数、次行属性头，再跟对应原子行；不按普通无标签 XYZ 读入后丢失 energy/forces/PBC。

## scale_spec
全量计数 **6,855 帧**，所有帧均为 **52 原子**，文件大小 38,354,321 bytes。全部元素集合为 C、Cu、H、O；前三帧化学计数为 `CHCu48O2`，该抽样化学计数不替代全量组成核查。

## coverage_spec
含铜及 C/H/O 的周期构型，适合此局部化学体系的能量/力拟合和 NequIP 类等变势模型接入。前三帧晶胞为约 `10.638 x 10.03 x 30.0` 的对角晶胞且三向 PBC；不能仅据晶胞形状推断吸附位置、温度、动力学时间顺序或生成软件。

## label_spec
结构级 energy 和原子级 forces 为主要监督。首帧 energy 为 `-63893.06534742232`，这是原始数值记录，不作为单位或零点判断依据。文件头未显式声明源单位，本地未发现足够来源说明；坐标、能量和力的单位需核实，禁止凭数值量级换算或擅自校零。没有确认 stress/virial、电荷或磁性标签。

## split_strategy
单文件没有现成 train/val/test 标记。优先取得轨迹/计算来源并按轨迹或时间块划分；若时间语义不明，可按构型簇/指纹分组审计，记录方法、索引、种子和近重复处理。不能将相邻帧随机拆分后直接声称独立泛化测试。

## constraints
- 元素表必须覆盖 C/Cu/H/O；不能把该文件当纯 Cu 数据或删除非铜原子。
- 不根据 ASE 常见单位惯例假冒源单位证据；单位未定时只验证结构/标签读取。
- 无已确认 stress 不启用应力监督，缺失标签不得补零。
- 数据版本、生成方法、原始许可和轨迹关联需使用前核实；本地文件名不证明官方来源。
