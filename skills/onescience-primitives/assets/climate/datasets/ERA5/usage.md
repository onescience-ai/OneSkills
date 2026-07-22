## access
ERA5 的逻辑存储路径为 `$ONESCIENCE_DATASETS_DIR/ERA5`；当前平台挂载路径可映射为 `/public/share/sugonhpcapp01/onestore/onedatasets/ERA5`。在作业脚本中应以只读数据根目录传入，避免复制大文件。

## data_schema
读取变量时必须先从 `fields.attrs["variables"]` 中查找变量名对应的通道索引，再从 `fields[:, index, :, :]` 或 `fields[t, index, :, :]` 提取数据；不要硬编码通道顺序。

典型读取方式如下：

```python
import h5py

with h5py.File("data/1979.h5", "r") as f:
    fields = f["fields"]
    variables = [
        v.decode() if isinstance(v, bytes) else str(v)
        for v in fields.attrs["variables"]
    ]
    idx = variables.index("2m_temperature")
    first_time_step = fields[0, idx, :, :]
```

静态场与主数据共享相同的空间网格，可作为额外输入特征拼接或并行编码。

## task_usage
适用于全球天气预报、时序外推、再分析下采样和气象基础模型训练。输入通常为历史多变量网格和静态场，输出通常为未来一个或多个 lead time 的多变量网格。

## integration_paths
优先实现 dataset-specific datapipe，再通过模型 adapter 暴露统一 batch 字典；训练脚本只依赖 adapter 输出，不直接硬编码原始路径。建议在 datapipe 层同时处理时间窗口采样、变量选通、静态场拼接和统计量归一化。

## preparation_requirements
需要使用 `h5py` 或兼容接口按时间步、变量维做切片读取，避免一次性加载完整 `fields`。训练前应明确：
- 变量到通道索引的映射来自 `fields.attrs["variables"]`
- 时间索引以 6 小时递增
- 静态场空间维度需与 `721 x 1440` 主网格对齐
- 归一化应优先使用年度 HDF5 文件内部的 `global_means` 和 `global_stds`

## consumption_interfaces
可通过 `h5py` / `xarray` datapipe 接入 FourCastNet、GraphCast 类模型或时空 Transformer，也可封装为统一 batch 字典供其他全球网格预报模型消费。

## evaluation_protocol
按 lead time 报告 RMSE、ACC、变量分层误差和区域加权指标。若任务包含多变量或多压力层，评测时应至少区分变量类型、压力层和预测步长。

## resource_profile
共享存储读取为主；年度文件体量大，建议使用按时间步和变量切片的 streaming、索引驱动采样或基于 chunk 的读取策略。GPU/CPU/内存预算应先通过单 batch 探测确定，再放大到正式训练配置。

## operation_limits
- 时间划分必须保持因果，不能随机打散训练/验证/测试样本。
- 当前外部 `stats/global_*.npy` 文件维度可能仍为 `[1, 99, 1, 1]`，对应旧版 99 通道；对 243 通道数据做标准化时，应优先使用年度 HDF5 文件内部统计量，或确认外部统计文件已重生成为 243 通道版本。
- 不同版本的统计目录和统计口径不要混用。
- 当前版本闰年仍按 365 天、1460 个时间步处理，构造时间轴时需要显式遵循这一约定。
- 不建议一次性加载完整年度 `fields` 到内存。