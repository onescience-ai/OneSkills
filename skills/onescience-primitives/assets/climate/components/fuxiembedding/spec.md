# component_info
将多时间步二维气象场组成的三维时空块切分为三维 patch，并投影到统一的 embedding 特征空间。

这是 Fuxi 输入编码阶段的 patch embedding 组件。

补充说明：

- 该组件处理的是三维时空块 `(TimeSteps, Height, Width)`
- 输出是三维 patch 特征图，不是展平 token 序列
- 当前实现不做自动 padding

该组件的核心实现包括 `FuxiEmbedding`，定位为嵌入层，由上层 OneScience 模型或流水线通过 Python API 调用。

# purpose
把原始数值特征、patch 或图节点/边特征投影到统一隐空间，适用于主干网络进入前的特征标准化表达。

# input_schema
- 2D 输入：`not_applicable`
- 3D 输入：`(Batch, in_chans, TimeSteps, Height, Width)`

内部统一做法：

- 使用 `Conv3d` 完成 patch 切分和线性投影
- 可选 `norm_layer` 作用在展平后的 patch token 上
- 最终再恢复回三维 patch 特征图

# output_schema
- 2D 输出：`not_applicable`
- 3D 输出：`(Batch, embed_dim, OutTimeSteps, OutHeight, OutWidth)`

其中：

- `OutTimeSteps = TimeSteps // PatchTimeSteps`
- `OutHeight = Height // PatchHeight`
- `OutWidth = Width // PatchWidth`

# parameters
- `img_size`
  - 输入空间尺寸 `(TimeSteps, Height, Width)`
- `patch_size`
  - patch 切分尺寸 `(PatchTimeSteps, PatchHeight, PatchWidth)`
- `in_chans`
  - 输入变量通道数
- `embed_dim`
  - 输出特征维度
- `norm_layer`
  - 可选归一化层

# key_dependencies
- `embedding` 模块族内的相邻组件

# usage_and_risks
- 该组件不支持二维输入
- 当前实现不做自动 padding，不能整除的尾部区域不会进入输出特征图
- Fuxi 当前调用层通常要求 `OutTimeSteps = 1`

# code_references
- `{onescience_path}/onescience/src/onescience/modules/embedding/fuxiembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/oneembedding.py`
- `{onescience_path}/onescience/src/onescience/models/fuxi/fuxi.py`
