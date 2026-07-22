## description
为 ERA5 选择数据接入、预处理、训练/评测路线的规划知识。

## when_to_use
当任务属于 weather 领域，且目标与以下用途匹配时使用：全球天气预报、时序外推、再分析下采样、气象基础模型训练。

## inputs
数据根目录：/public/share/sugonhpcapp01/onestore/onedatasets/ERA5。任务输入规范：输入为历史多变量网格和静态场。

## outputs
输出结构应与任务定义一致：输出为未来 lead time 的多变量网格。同时产出 split、统计量和 datapipe 配置。

## procedure
1. 校验目录权限、年度文件完整性和静态场/统计量文件是否齐全。
2. 按 spec.md 确认 schema、变量顺序、格式、规模和覆盖范围。
3. 按 usage.md 选择任务类型、年份划分、时间窗口、变量子集和消费接口。
4. 先做样本级读取探测，确认 `fields.attrs["variables"]`、单样本 shape、时间索引规则和统计量口径。
5. 生成 datapipe/adapter 配置并做单 batch shape 检查。
6. 运行小样本训练或推理 smoke test。
7. 固化 benchmark 评测协议、资源预算和归一化方案。

## constraints
必须保留原始数据版本和按年份的因果划分语义；变量通道顺序必须以 `fields.attrs["variables"]` 为准；不同 stats 目录版本和不同通道数口径不能混用；当前版本闰年仍按 365 天、1460 个时间步处理。

## next_phase_recommendation
若 schema、变量映射和 split 已确认，进入 datapipe adapter 实现；若变量名、统计量口径或标签定义不明确，先做样本级探测和字段字典补全，再决定训练或评测路线。

## fallback
若文件权限、格式解析或依赖失败，先记录失败路径和错误信息，降级为只读索引模式；若外部 stats 与 243 通道数据不一致，则回退为优先使用年度 HDF5 文件内部统计量；若无法确认 lead time 标签构造规则，则仅支持数据探测、无监督预训练或推理任务。