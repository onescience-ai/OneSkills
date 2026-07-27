## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/Eagle`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/Eagle`。核心数据在 `Eagle_dataset/Cre`。

## data_schema
每个仿真目录包含 `sim.npz`、`triangles.npy` 和 `constrained_kmeans_*.npy`。`sim.npz` 包含点坐标、mask、速度 `VX/VY` 和压力 `PS/PG`。

## task_usage
适用于 Eagle、非结构网格 CFD 时序预测、cluster-aware graph learning 和 mesh trajectory 模型。

## integration_paths
优先使用 `cfd/datapipes/eagle`；需要额外提供 `splits_dir`，其中有 `train.txt/valid.txt/test.txt` 指向相对仿真目录。

## preparation_requirements
生成或确认 split 文件；抽检 `sim.npz` 键和 `triangles.npy` shape；确认 `n_cluster` 与存在的 kmeans 文件匹配。

## consumption_interfaces
样本字段包括 `mesh_pos`、`edges`、`velocity`、`pressure`、`node_type`、`mask`、可选 `cluster`；batch 阶段 padding。

## evaluation_protocol
按速度和压力通道报告单步/窗口误差；对变长网格还应统计空样本过滤比例。

## operation_limits
缺 split 文件时不能直接训练；坏样本会被过滤；窗口输入和预测步由训练脚本定义。
