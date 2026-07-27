## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/matchem/dp`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/dp`。主要入口为 `water/data_0..data_3` 和 `dpa3_finetune/{train_data,val_data}`。

## data_schema
每个 DeepMD system 目录以 `type.raw`、`type_map.raw` 和 `set.000/{coord.npy, box.npy, energy.npy, force.npy}` 描述多帧结构。`coord.npy` 与 `force.npy` 是扁平坐标/力数组，需要按原子数 reshape。

## task_usage
适用于 Deep Potential、DPA3 类模型的能量/力联合训练、微调、验证集 loss 评估和小规模 pipeline 调试。`water` 可用于水体系势能面训练；`dpa3_finetune` 可用于 CH 体系微调。

## integration_paths
优先实现 DeepMD raw/npy adapter，再输出 OneScience materials datapipe 兼容的 AtomicData 字段。接入流程为：枚举 system -> 读取 `type.raw/type_map.raw` -> mmap 加载 `npy` -> reshape 坐标/力 -> 补 `cell/pbc/atomic_numbers` -> 构造 batch。

## preparation_requirements
训练前应检查每个 system 的 `coord`、`box`、`energy`、`force` 帧数一致；检查 `coord.shape[1]` 是否等于 `len(type.raw) * 3`；确认 `type_map.raw` 与模型元素表一致；若使用 `dpa3_ch_stat.hdf5`，需确认统计文件对应同一数据版本。

## consumption_interfaces
可供 DeepMD/DPA3 训练脚本直接读取，也可转换为 `matchem/datapipes/materials` 的 AtomicData batch。下游模型通常消费 `pos`、`atomic_numbers`、`cell`、`pbc`、`energy`、`forces`、`natoms`、`batch`。

## evaluation_protocol
报告能量 MAE/RMSE、力 MAE/RMSE，并按 system 或水/CH 子集拆分统计。微调任务应固定 train/val 目录，不要每次评测重新随机划分。

## resource_profile
`npy` 文件适合 mmap 或按帧切片读取；不要一次性把所有 system 加载进内存。变长 system batch 应限制最大原子数或按原子数分桶。

## operation_limits
- 不要把 `dpa3_finetune/train_data` 和 `val_data` 混合作为同一个无 split 数据池。
- 没有 stress/virial 文件时不要启用应力 loss。
- 不同 system 的元素映射和 dtype 需要逐目录确认。
- 只读访问共享数据目录，训练产物写到任务输出目录。
