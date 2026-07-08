# component_info
OneHead 位于 head 模块，是最终输出层或任务头的轻量统一入口。对于 CFD 最常见的是 UNetHead1D/2D/3D，用于把已恢复的特征场映射到目标物理量通道。

# purpose
- 做什么：将主干/decoder 输出投影为任务目标通道或目标属性。
- 解决问题：统一管理不同任务头的构造。
- 适用场景：U-Net 输出场投影、材料能量/力/磁矩预测、生物 MSA mask 预测。
- 不适用场景：恢复空间尺度、构建图拓扑或替代 decoder。

# input_schema
输入由 style 决定；UNetHead*d 通常接收 `(Batch, Channels, ...Spatial)` 特征图，材料 head 接收模型定义的结构表征。

# output_schema
UNetHead*d 通常保持空间维度并改变通道数；其它 head 返回任务特定标量、向量或 logits。

# parameters
- `style`：注册表名称，常见取值包括 `UNetHead2D`, `UNetHead3D`, `MaskedMSAHead`, `EnergyHead`。
- `**kwargs`：透传给目标 预测头 实现。
- 常见参数：`in_channels`、`out_channels`、卷积核、激活或任务头隐藏维度。
- CFD 中 `out_channels` 应等于目标物理变量通道数。

# key_dependencies
- _lazy.py
- unet_head.py
- maskedmsahead.py
- matris_head.py

# usage_and_risks
- head 不能修复 decoder 已经丢失的空间分辨率。
- `out_channels` 与 datapipe label 通道顺序必须一致。
- MaskedMSAHead 与 CFD 场预测语义不同，不应误用。
- style 未注册会实例化失败。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/head/onehead.py`
- `{onescience_path}/onescience/src/onescience/modules/head/unet_head.py`
