## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/matchem/matpl`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/matpl`。主要子目录为 `AuAg`、`Cu`、`HfO2`、`LiSiC`。

## data_schema
该集合混合 extxyz、PWdata、MOVEMENT、JSON 配置和 LAMMPS 运行资产。训练样本通常来自 `AuAg-5762.xyz`、`pwdata/<case>`、`*_MOVEMENT` 或 `valid_movement`；`nn_lmps` 中的力场和 job 文件用于运行验证，不是监督样本。

## task_usage
适用于 PWMLFF/MatPL 力场训练、材料势拟合、合金/氧化物/锂硅碳体系泛化评估、LAMMPS 力场验证和 MOVEMENT 轨迹解析测试。

## integration_paths
按格式选择 parser：extxyz 用 ASE；MOVEMENT 用 PWMLFF/PWmat 解析器；PWdata 组分目录用 MatPL/PWMLFF 数据接口。解析后统一映射为结构、能量、力、可选 virial/stress 的 AtomicData 或模型专用 batch。

## preparation_requirements
训练前需要枚举每个材料体系的元素表、frame 数、能量单位、力单位和是否存在 virial/stress。Cu 子集优先读取 `nn_train.json`、`nn_test.json` 和 `valid_movement` 确认划分。

## consumption_interfaces
可供 PWMLFF/MatPL 训练入口直接消费，也可转换为 OneScience materials datapipe。统一输出字段应至少包含 `atomic_numbers/species`、`pos`、`cell`、`pbc`、`energy`、`forces`，若存在 virial/stress 则单独标注单位和 shape。

## evaluation_protocol
按材料体系和 split 报告 energy、force、virial/stress 指标。跨组分任务应按留出组分或留出轨迹文件评测，不只报告随机帧划分误差。

## resource_profile
MOVEMENT 和 PWdata 解析成本高于 CSV，建议先转换索引缓存再训练。LAMMPS 验证需要单独的运行目录，不应写回共享数据路径。

## operation_limits
- 不要把 `nn_lmps` 作为训练数据枚举。
- 不同体系不能共享未确认的元素表和能量标尺。
- 轨迹相邻帧强相关，随机帧划分会导致评测偏乐观。
- parser 不支持某个 PWdata 子格式时，应记录失败目录并跳过，不要静默丢样本。
