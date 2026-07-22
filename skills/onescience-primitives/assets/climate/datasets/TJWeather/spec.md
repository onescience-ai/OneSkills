## content_principle
区域气象数据按时间和变量组织为模型输入输出，用于区域预报或下游气象任务。

## data_schema
TJ1-GB 子目录保存实际数据；根目录未提供 README 或 metadata。

## storage_format
具体格式需进入 TJ1-GB 或配套 dataloader 确认。

## scale_spec
平台根目录未提供样本数、变量数或大小统计。

## coverage_spec
TJWeather 指定区域和变量范围，需根据 TJ1-GB 内部元数据确认。

## label_spec
未来气象变量或观测值作为监督标签。

## split_strategy
无根级 split；推荐按时间连续划分。
