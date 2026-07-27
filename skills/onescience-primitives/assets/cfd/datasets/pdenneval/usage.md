## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/PDENNEval`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/PDENNEval`。主入口为 `pdebench_data`，生成数据在 `generated_data`。

## data_schema
HDF5/H5 内部可能是单文件 tensor，也可能是 seed group 和 grid；变量可能包括 density、pressure、Vx/Vy/Vz 或标量解场。

## task_usage
适用于 PDEBench、PDENNEval、FNO、DeepONet、MPNN、UNet、UNO、PINO 和 PDE residual benchmark。

## integration_paths
优先使用 `cfd/datapipes/pdenneval`；按模型族选择对应 datapipe 类，并设置 initial_step、reduced_resolution、reduced_resolution_t、test_ratio。

## preparation_requirements
先探测目标 HDF5 文件内部键和 shape；确认单文件/多文件模式；生成数据 zip 使用前先解压并记录版本。

## consumption_interfaces
FNO/DeepONet/UNO/PINO 输出 `(history,target,grid)`；UNet 输出 `(history,target)`；MPNN 输出 flatten datapoints、coordinates、variables。

## evaluation_protocol
按 PDE 文件、变量、时间步和模型族报告相对 L2、RMSE、守恒/残差误差。

## operation_limits
没有统一 test dataloader；不同模型族返回协议不同；HDF5 schema 不统一，不能跨文件硬编码。
