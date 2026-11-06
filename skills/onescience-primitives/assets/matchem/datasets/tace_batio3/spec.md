## content_principle
描述 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/TACE/BaTiO3.xyz` 的局部 BaTiO3 结构及电响应数据。2026-11-05 全量扫描帧数、原子数、元素及 Properties，ASE 抽样前三帧。该文件适合能量/力与电响应多目标接入，不代表 TACE 所有训练数据或已覆盖全部相、温度与电场强度。

## data_schema
| 粒度 | 原始字段 | 抽样 shape/语义 |
| --- | --- | --- |
| 原子级 | `species`, `pos`, `forces` | `(N,)`, `(N,3)`, `(N,3)` |
| 原子级 | `born_effective_charges` | `(N,9)`，每原子二阶响应张量的展平表示 |
| 结构级 | `Lattice`, `pbc`, `energy`, `stress` | 晶胞、三向周期、标量能量、头部 9 分量应力 |
| 结构级 | `polarization` | `(3,)` 极化向量 |
| 结构级 | `polarizability` | `(9,)` 展平张量 |
| 结构级 | `electric_field` | `(3,)` 电场向量 |
| 来源级 | `original_dataset_index` | 标量来源索引，非 split 标签 |

Properties 全文件一致为 `species:S:1:pos:R:3:born_effective_charges:R:9:forces:R:3`。当前 ASE 抽样将 energy/forces/stress、born_effective_charges、polarization 识别到 `atoms.calc.results`，polarizability/electric_field/original_dataset_index 在 info；不能只遍历 arrays/info 判断标签是否缺失。ASE 将头部 9 分量 stress 转为 6 分量，需保留并核对表示约定。

## directory_layout
```text
matchem/TACE/
  BaTiO3.xyz
```
目录/文件名大小写敏感，原语目录名可规范为 `tace_batio3`，不改变源路径。

## storage_format
多帧扩展 XYZ，用 ASE 的 extxyz reader。9 分量张量应先按源序保存，确定行列及空间/响应轴定义后再 reshape `(3,3)`；原子级 Born 张量按每原子独立处理，不能当 9 个不同标量电荷。

## scale_spec
全量 **59 帧**，每帧 **135 原子**，元素 Ba、Ti、O，文件 2,098,046 bytes。前三帧化学计数为 `Ba27Ti27O81`；所有帧原子数一致不等于已逐帧核实相结构/化学计数和响应张量有效性。

## coverage_spec
周期 BaTiO3 的结构和电响应小样本，前三帧三向 PBC。首帧 electric_field 为 `[0,0,0]`，不能以此判定全文件均为零场；温度、晶相、场强/方向、极化分支及响应来源需补充实际元数据后才能给出覆盖结论。

## label_spec
联合目标可包括 energy、forces、stress、born_effective_charges、polarization、polarizability；electric_field 是条件量，不默认当预测标签。Born 有效电荷不等于 Bader/标量原子电荷，polarization 不等于 dipole，polarizability 不等于介电常数。文件未充分定义物理单位、Born 张量轴序、极化分支/极化量子、有限电场下能量定义与响应边界条件；启用对应监督前必须落实这些协议，不据标签名自动换算。

## split_strategy
单文件没有确认的 train/val/test。保留 original_dataset_index 追踪来源，不能当作 split 或假设时间顺序。优先按原始轨迹、场条件或构型组划分，防近邻构型泄漏；59 帧时可按组交叉验证，但每折重新只从训练部分拟合统计，保存分配与有效样本量。

## constraints
- 保留电场条件、坐标基、极化分支及张量变换关系；旋转结构时必须按物理协议同步旋转向量/张量，不能只旋转 positions。
- 不能把 Born 张量压成标量电荷、把极化率称介电常数或把缺失响应补零。
- stress 的六/九分量互换、virial 换算、周期极化处理均需固定协议并回验。
- 数据很小，不宣称跨相/强场或长时动力学泛化；使用前核对 TACE 数据实际来源和许可。
