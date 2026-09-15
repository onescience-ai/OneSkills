# 骨架任务：模型与检查点兼容性验证

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 加载模型代码、配置和检查点，核验版本、哈希、输入输出通道并执行单步干运行。

## 执行 prompt（跨场景聚合去重）
- 加载{MODEL_CONFIG}和{MODEL_CHECKPOINT}，核对{CHECKPOINT_SHA256}，在{RUNTIME_DEVICE}上执行一个原生时间步的干运行。报告代码、依赖、配置和权重版本；存在通道错配、缺失权重或未登记转换时停止。

## 输入槽（var/hint/default）
- {MODEL_CHECKPOINT} | required=True | type=str | var_name=模型权重路径 | hint=输入模型权重文件路径。 | default=None
- {MODEL_CONFIG} | required=True | type=str | var_name=模型配置路径 | hint=输入模型配置文件路径。 | default=None
- {CHECKPOINT_SHA256} | required=False | type=str | var_name=权重SHA-256 | hint=输入权重SHA-256。 | default=None
- {RUNTIME_DEVICE} | required=True | type=str | var_name=推理设备 | hint=输入运行设备，如GPU。 | default=None

## 产出
- 单步干运行日志
- 模型与检查点身份报告
- 输入输出兼容性矩阵

## 质量门禁 quality_gate
- 不存在缺失或意外的权重、变量和通道
- 代码、配置、标准化参数和检查点属于兼容版本
- 单步干运行正常退出且输出形状和值域可检查
- 检查点SHA-256与登记值一致

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-1b0d5205

## 复用场景
- E1
