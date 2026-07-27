## content_principle
MatPL 数据集原语描述 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/matpl` 下的材料势训练数据和 PWMLFF/PWdata 工作流文件。该集合服务于 AuAg、Cu、HfO2、LiSiC 等体系的力场拟合、验证和分子动力学联动。

## data_schema
数据组织混合了结构数据、训练配置和力场运行文件：

- `extxyz`：如 `AuAg-5762.xyz`，可作为 ASE 多帧结构输入。
- `pwdata/<composition_or_case>/`：按组分、初始结构或构型目录组织的 PWdata 数据。
- `MOVEMENT`：PWmat/PWMLFF 常见轨迹文件，包含多帧结构、能量、力和可能的 virial 信息。
- `nn_train.json`、`nn_test.json`：Cu 子集中的训练/测试配置或索引。
- `nn_lmps/`：LAMMPS 相关力场、输入和作业脚本。

## directory_layout
```text
/matchem/matpl
├── AuAg
│   ├── AuAg-5762.xyz
│   └── pwdata
│       ├── Ag10Au22
│       ├── Ag10Au38
│       ├── Ag10Au6
│       ├── Ag11Au21
│       ├── Ag11Au37
│       ├── Ag11Au5
│       └── Ag12
├── Cu
│   └── pwdata
│       ├── 0_300_MOVEMENT
│       ├── 1_500_MOVEMENT
│       ├── valid_movement
│       ├── nn_train.json
│       ├── nn_test.json
│       └── nn_lmps/{forcefield.ff, in.lammps, lmp.config, *.job}
├── HfO2
│   └── pwdata/init_*
└── LiSiC
    └── pwdata/{C2, C448, C448Li75, C64Si32, Li1Si24, Li3Si8, Li8, Li88Si20, Si1, Si217}
```

## storage_format
该集合不是单一格式数据集。接入时应先按子目录判断格式：`*.xyz` 用 ASE 读取；`*_MOVEMENT` 与 `valid_movement` 用 PWMLFF/PWmat parser；`pwdata` 组分目录按 MatPL/PWMLFF 数据接口读取；`nn_lmps` 是推理或 MD 运行资产，不应作为训练样本枚举。

## scale_spec
AuAg 按多个 Ag/Au 组分目录组织，并有 `AuAg-5762.xyz` 多帧文件；Cu 有两个 MOVEMENT 训练文件和一个 valid movement；HfO2、LiSiC 按多个初始构型或组分目录组织。实际样本数必须通过对应 parser 统计 frame 数。

## coverage_spec
覆盖合金、单质铜、氧化物和锂硅碳体系，适用于材料势多体系训练、PWMLFF 力场构建、LAMMPS 联动验证和跨组分泛化实验。

## label_spec
可用标签通常包括总能量、原子力和 virial/stress；具体字段取决于 `MOVEMENT` 或 PWdata 子目录内容。使用 extxyz 时需读取 properties 行确认是否包含 `forces`、`energy`、`stress`。

## split_strategy
若子目录提供 `nn_train.json`、`nn_test.json` 或 `valid_movement`，应优先使用这些显式划分。其它子集可按组分目录划分训练/验证/测试，以测试跨组分泛化；不建议在同一轨迹内随机打散相邻帧后同时进入训练和测试。

## constraints
- `nn_lmps` 下的 `forcefield.ff`、LAMMPS 输入和 job 文件是运行产物或部署资产，不属于监督训练样本。
- 不同材料体系元素集合差异大，混合训练要显式声明元素表。
- MOVEMENT 解析时要保持能量、力、virial 单位一致。
- 按轨迹帧随机划分可能造成构型泄漏，评测应优先按组分、温度或轨迹文件隔离。
