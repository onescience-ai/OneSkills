## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/matchem/mace`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/mace`。入口包括 `ani1x`、`water`、`DMC` 和 `nanotube` 四类子集。

## data_schema
extxyz 文件通过 ASE 读取多帧结构，字段通常包括元素、坐标、能量、力、晶胞和 PBC。ANI1x 还提供 HDF5 train/val/test 分片与统计 JSON，接入前需探测 HDF5 内部键。

## task_usage
适用于 MACE 模型训练、分子势能面拟合、能量/力联合监督、不同体系迁移微调和小样本测试。`water`、`DMC`、`nanotube` 可作为单体系实验；ANI1x 适合作为量化化学 split。

## integration_paths
extxyz 优先走 ASE -> AtomicData -> MACE dataloader；HDF5 需要 dataset-specific reader，再映射到同一 AtomicData 字段协议。混合多个子集时，应为每个子集添加 dataset 标识并配置采样比例。

## preparation_requirements
需要统计每个 extxyz 的帧数、元素集合、能量/力字段名、是否有有效 cell/PBC。HDF5 需要检查 group 结构、数组 shape、单位和 train/val/test shard 是否完整。MACE 训练前应生成元素表、均值/标准差或元素参考能量。

## consumption_interfaces
主要消费端为 MACE 势模型，也可通过 `matchem/datapipes/materials` 适配其它原子势模型。batch 字段包括 `pos`、`atomic_numbers`、`cell`、`pbc`、`energy`、`forces`、`batch`、`natoms`。

## evaluation_protocol
按子集和 split 分别报告 energy/force MAE/RMSE。混合训练时至少区分 ANI1x、water、DMC、nanotube 的误差，避免整体平均掩盖跨域退化。

## resource_profile
extxyz 适合流式逐帧读取或预转换缓存；HDF5 分片适合按 shard 并行索引。大分子或 nanotube 样本应设置最大原子数、邻居截断和 batch size 上限。

## operation_limits
- 不同子集的单位和能量零点可能不同，不能无统计校准直接合并。
- HDF5 字段名不能凭文件名猜测。
- 没有 stress 标签时不要启用应力 head。
- 非周期分子要显式处理 cell/PBC。
