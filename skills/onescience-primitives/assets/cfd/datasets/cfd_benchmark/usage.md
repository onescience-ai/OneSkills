## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/CFD_Benchmark`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/CFD_Benchmark`。按子集目录选择入口。

## data_schema
`airfoil/pipe` 使用 `Q/X/Y.npy`；`ns/darcy/plas` 使用 MAT；`diffusion_sorption` 使用 H5；`elasticity` 使用 mesh NumPy；`car` 包含预处理压缩包。

## task_usage
适用于 FNO、DeepONet、CNO、PINO、UNet 等神经算子 benchmark，以及 CFD/PDE 场预测和多分辨率泛化实验。

## integration_paths
NumPy 子集可直接 mmap；MAT/H5 需使用 scipy/h5py 或兼容 reader；不同子集应写独立 adapter，不要用统一硬编码通道解析。

## preparation_requirements
先选定子任务，再探测文件 shape、内部键、通道含义、坐标网格和时间维；记录 split、降采样、归一化统计。

## consumption_interfaces
规则网格模型通常消费 `(input, target, grid)`；时序任务还需 history/lead time；PINO 任务额外消费物理残差采样点。

## evaluation_protocol
报告相对 L2、RMSE、rollout error 和按变量通道的误差；跨子集不要只汇总一个平均值。

## operation_limits
格式和语义高度异构；MAT/H5 未探测键前不要生成训练脚本；压缩包需先确认是否解压和版本一致。
