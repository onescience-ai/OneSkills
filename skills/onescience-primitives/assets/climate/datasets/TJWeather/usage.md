## access
平台挂载路径为 `/public/share/sugonhpcapp01/onestore/onedatasets/TJWeather`；在作业脚本中以只读数据根目录传入，避免复制大文件。

## data_schema
TJ1-GB 子目录保存实际数据；根目录未提供 README 或 metadata。

## task_usage
区域天气预报、变量下采样、气象时序建模。。输入输出：输入为历史区域网格变量；输出为未来气象变量。

## integration_paths
优先实现 dataset-specific datapipe，再通过模型 adapter 暴露统一 batch 字典；训练脚本只依赖 adapter 输出，不直接硬编码原始路径。

## preparation_requirements
需要定位 TJ1-GB 内部变量、时间轴、网格和归一化统计。

## consumption_interfaces
可接 xarray/h5py/zarr datapipe，具体由内部格式决定。

## evaluation_protocol
按 lead time、变量和区域报告 RMSE、MAE、ACC。

## resource_profile
共享存储读取为主；大文件建议使用 streaming、mmap、h5 chunk 或索引驱动采样。预处理统计量只从训练 split 计算，GPU/CPU/内存预算按单 batch 探测结果设置。

## operation_limits
根级元数据不足；使用前必须确认变量单位、网格和时间间隔。
