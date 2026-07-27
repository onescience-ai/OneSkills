## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/matchem/mattersim`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/mattersim`。当前入口文件为 `high_level_water.xyz`。

## data_schema
`high_level_water.xyz` 为 extxyz 多帧文件，样例单帧包含 192 个原子，properties 中包含 `species`、`pos`、`forces`，结构级属性包含 `energy`、`Lattice`、`pbc`、`cutoff` 和 `nneightol`。

## task_usage
适用于 MatterSim 微调、水体系势能面训练、能量/力联合评估、周期构图测试和 materials datapipe 的 extxyz smoke test。

## integration_paths
使用 ASE 逐帧读取 extxyz，映射为 AtomicData：元素符号转原子序数，`pos` 作为坐标，`forces` 作为原子级标签，`energy` 作为结构级标签，`Lattice/pbc` 用于周期邻接构图。

## preparation_requirements
训练前统计帧数、能量范围、力范数范围、元素集合和所有帧的原子数是否固定。若按帧划分 train/val/test，应记录帧索引范围或随机种子。

## consumption_interfaces
可供 MatterSim、MACE、UMA 或 OneScience materials datapipe 消费。batch 至少包含 `atomic_numbers`、`pos`、`cell`、`pbc`、`energy`、`forces`、`natoms`、`batch`。

## evaluation_protocol
报告 energy MAE/RMSE 和 force MAE/RMSE；水体系还可按 O/H 原子类型分别统计 force 误差。若用于 MD 前验证，应检查能量漂移和力分布。

## resource_profile
单帧原子数 192，周期构图会产生较多邻接边；建议先用小 batch 做显存探测，再扩大训练。

## operation_limits
- 不要默认存在 stress 标签。
- 相邻帧强相关时，不要把连续轨迹随机打散后做过于乐观的测试结论。
- 与其它水数据混合前要核对能量零点、单位和 cutoff 口径。
