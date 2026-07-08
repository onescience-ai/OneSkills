# component_info
在二维 patch 网格 `(Height, Width)` 上完成 FourCastNet 主干特征融合。

补充说明：

- 该组件处理的是二维 patch 网格特征，不是原始图像
- 内部先做 AFNO 频域混合，再做逐位置 MLP 通道混合
- 它是 FourCastNet 主模型中重复堆叠的核心 trunk block

该组件的核心实现包括 `FourCastNetFuser`，定位为融合模块，由上层 OneScience 模型或流水线通过 Python API 调用。

# purpose
融合来自不同变量、尺度、时间步或分支的特征，适用于多源气象场建模。

# input_schema
- 2D 输入：`(Batch, Height, Width, dim)`
- 3D 输入：`not_applicable`

内部统一做法：

- 先做 `LayerNorm`
- 再调用 `OneAFNO(style="FourCastNetAFNO2D")`
- 再调用 `OneFC(style="FourCastNetFC")`
- 通过残差连接与 `DropPath` 完成 block 输出

# output_schema
- 2D 输出：`(Batch, Height, Width, dim)`
- 3D 输出：`not_applicable`

明确约束：

- 输出 shape 与输入 shape 保持一致
- `dim` 必须与上下游 embedding / head 的特征维度对齐

# parameters
- `dim`
  - 输入与输出特征维度
- `mlp_ratio`
  - MLP 隐层放大倍数
- `drop`
  - MLP dropout 比例
- `drop_path`
  - Stochastic Depth 比例
- `double_skip`
  - 是否启用中间残差连接
- `num_blocks`
  - AFNO 的通道分块数
- `sparsity_threshold`
  - AFNO soft shrink 阈值
- `hard_thresholding_fraction`
  - AFNO 保留的频率模式比例
- `act_layer`, `norm_layer`
  - 激活函数与归一化层类型

# key_dependencies
- `onefuser`
- `oneafno`
- `fourcastnetafno`
- `onefc`
- `fourcastnetfc`
- `layers`

# usage_and_risks
- 该组件输入是二维 patch 网格，不是展平 token 序列
- 若调用层忘记把 token 序列恢复成 `(Height, Width)` 网格，shape 会不匹配
- `num_blocks` 必须能与内部 AFNO 的 `dim` 配合整除

# code_references
- `{onescience_path}/onescience/src/onescience/modules/fuser/fourcastnetfuser.py`
- `{onescience_path}/onescience/src/onescience/modules/fuser/onefuser.py`
- `{onescience_path}/onescience/src/onescience/models/fourcastnet/fourcastnet.py`
