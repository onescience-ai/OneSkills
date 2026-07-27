## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/matchem/dpa3`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/matchem/dpa3`。核心数据在 `CH_3787/train_CH` 和 `CH_3787/val_CH`。

## data_schema
`sys_*` 目录包含 `type.raw` 与 `set.000/{coord.npy, box.npy, energy.npy, force.npy}`。样例 `sys_100` 的 `coord.npy` 为 `(45, 300)`，即 45 帧、每帧 100 个原子。

## task_usage
适用于 DPA3 微调、CH 碳氢体系势能面训练、能量-力联合 loss 验证和 DeepMD 数据读取调试。该集合不适合作为 CSV 性质回归任务输入。

## integration_paths
以 `CH_3787/train_CH` 构建训练 datapipe，以 `CH_3787/val_CH` 构建验证 datapipe。adapter 负责把 DeepMD 扁平数组转换为 `pos`、`forces`、`cell` 和结构级 `energy`，并把 `type.raw` 映射到元素编号。

## preparation_requirements
需要确认 `type.raw` 对应的元素顺序；若目录缺少 `type_map.raw`，应从 DPA3 配置或同源数据说明中补充元素映射。训练前抽检多个 `sys_*` 的原子数、帧数、dtype 和能量范围。

## consumption_interfaces
消费端可以是 DPA3/Deep Potential 训练脚本，也可以是 OneScience materials datapipe。统一 batch 应包含 `atomic_numbers`、`pos`、`cell`、`pbc`、`energy`、`forces`、`natoms`。

## evaluation_protocol
验证集使用 `val_CH`，指标为 energy MAE/RMSE 和 force MAE/RMSE。建议额外按原子数或 system id 分桶查看误差，避免少数大 system 掩盖问题。

## resource_profile
DeepMD `npy` 数据可按 system 和 frame 流式读取；若转换为缓存数据库，应保留源 system id 和 frame id 便于回溯。

## operation_limits
- 不要默认存在 stress、virial、电荷或自旋标签。
- 不要凭 `sys_*` 编号推断训练/验证划分；以目录名为准。
- 混合其它 CH 或 water 数据时，要独立记录数据来源和采样比例。
