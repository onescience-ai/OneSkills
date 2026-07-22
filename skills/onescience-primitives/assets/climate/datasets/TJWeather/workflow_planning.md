## description
为 TJWeather 选择数据接入、预处理、训练/评测路线的规划知识。

## when_to_use
当任务属于 weather 领域，且目标与以下用途匹配时使用：区域天气预报、变量下采样、气象时序建模。

## inputs
数据根目录：/public/share/sugonhpcapp01/onestore/onedatasets/TJWeather。任务输入规范：输入为历史区域网格变量。

## outputs
输出结构应与任务定义一致：输出为未来气象变量。。同时产出 split、统计量和 datapipe 配置。

## procedure
1. 校验目录权限和文件完整性。
2. 按 spec.md 确认 schema、格式、规模和覆盖范围。
3. 按 usage.md 选择任务、split、预处理和消费接口。
4. 生成 datapipe/adapter 配置并做单 batch shape 检查。
5. 运行小样本训练或推理 smoke test。
6. 固化 benchmark 评测协议和资源预算。

## constraints
必须保留原始数据版本和划分语义；根级元数据不足；使用前必须确认变量单位、网格和时间间隔。

## next_phase_recommendation
若 schema 和 split 已确认，进入 datapipe adapter 实现；若标签或变量名不明确，先做样本级探测和字段字典补全。

## fallback
若文件权限、格式解析或依赖失败，先记录失败路径和错误信息，降级为只读索引模式；无法获得标签时仅支持无监督预训练、推理或数据探测任务。
