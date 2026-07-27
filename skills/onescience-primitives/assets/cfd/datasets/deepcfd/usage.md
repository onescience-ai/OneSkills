## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/DeepCFD`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/DeepCFD`。入口文件为 `dataX.pkl` 和 `dataY.pkl`。

## data_schema
`dataX.pkl` 是输入张量，`dataY.pkl` 是目标张量；当前均为 981 个样本、3 通道、`172 x 79` 网格。

## task_usage
适用于 DeepCFD、CNN/UNet 规则网格回归、二维流场 surrogate 和通道加权损失测试。

## integration_paths
使用 `cfd/datapipes/deepcfd` 直接读取 pickle；自定义 reader 应保持 `x/y` 样本顺序一致，并按 split_ratio 划分。

## preparation_requirements
检查 pickle 可读、样本数一致、输出通道数为 3；训练前估算内存，因为 datapipe 会全量加载。

## consumption_interfaces
batch 为 `{"x": tensor, "y": tensor}`；可调用 `get_loss_weights()` 获得目标通道权重。

## evaluation_protocol
报告逐通道 MAE/RMSE、整体相对 L2 和加权 loss；如果使用 val，需要从剩余段再显式拆分。

## operation_limits
无坐标、mask、case 参数；val 不是独立 split；大规模扩展时需改为懒加载。
