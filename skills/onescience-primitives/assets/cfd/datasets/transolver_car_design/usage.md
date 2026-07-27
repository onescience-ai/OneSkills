## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/Transolver-Car-Design`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/Transolver-Car-Design`。主入口为 `mlcfd_data/preprocessed_data`。

## data_schema
每个样本目录含 `x.npy`、`y.npy`、`pos.npy`、`surf.npy`、`edge_index.npy`；`param0..param8` 是 fold 分组。

## task_usage
适用于 Transolver-Car、三维汽车外流场压力/速度预测、PyG 图代理模型和 fold 泛化评估。

## integration_paths
优先使用 `cfd/datapipes/shapenetcar` 的 preprocessed 模式；配置 data_dir、preprocessed_save_dir、stats_dir 和 fold_id。

## preparation_requirements
确认 9 个 param fold 完整；抽检样本节点数、边数和 `x/y` 通道；训练统计只从训练 fold 生成。

## consumption_interfaces
输出 PyG Data，字段为 `x,y,pos,surf,edge_index`；`surf` 和压力通道常用于 surface loss。

## evaluation_protocol
报告速度三通道、压力通道和表面点压力误差；按 fold 记录指标。

## operation_limits
图边数量大，先做小 batch 显存探测；xlsx/png/linear_regression_code 不是主训练样本；不要跨 fold 泄漏。
