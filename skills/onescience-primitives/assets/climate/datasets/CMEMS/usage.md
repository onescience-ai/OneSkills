## access
平台挂载路径为 `/public/share/sugonhpcapp01/onestore/onedatasets/CMEMS`；在作业脚本中以只读数据根目录传入，避免复制大文件。

## data_schema
metadata.json 给出 years=[2010,2011,2012]、variables 列表和 total_files=365；data/h5/newdata 存放年度 h5；stats/stats-new 存放统计量。

## task_usage
海洋状态预测、海温/海流预报、海洋基础模型训练、海气耦合建模。。输入输出：输入为历史多变量海洋网格；输出为未来 SST/SSH/流速/盐度/位温。

## integration_paths
优先实现 dataset-specific datapipe，再通过模型 adapter 暴露统一 batch 字典；训练脚本只依赖 adapter 输出，不直接硬编码原始路径。

## preparation_requirements
需要用 metadata 选择变量，读取 h5，按深度层展开通道并应用 stats。

## consumption_interfaces
h5py/xarray datapipe，接时空 CNN、Transformer、Neural Operator。

## evaluation_protocol
按 lead time 和变量报告 RMSE、ACC、区域加权误差。

## resource_profile
共享存储读取为主；大文件建议使用 streaming、mmap、h5 chunk 或索引驱动采样。预处理统计量只从训练 split 计算，GPU/CPU/内存预算按单 batch 探测结果设置。

## operation_limits
metadata years 与目录中年度文件可能不完全一致；训练前需明确实际使用年份。
