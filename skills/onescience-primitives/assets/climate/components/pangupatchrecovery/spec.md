# component_info
将 patch 级别特征图恢复为原始气象场分辨率，把高维特征映射回最终的二维或三维变量场。

这是 Pangu 系列输出解码阶段的统一 patch recovery 组件。

该组件的核心实现包括 `PanguPatchRecovery`，定位为重建模块，由上层 OneScience 模型或流水线通过 Python API 调用。

补充说明：

- 本知识默认描述的是 canonical Pangu / unified 3D trunk 场景中的恢复语义。
- 它可以提供 Pangu family-level 的输出语义参考，但不能自动代表所有 lite / hybrid 变体的内部恢复实现。

# purpose
把 token、patch 或中间特征恢复为目标物理场，适用于预测结果输出前的空间重建。

# input_schema
- 2D 输入：`(Batch, in_chans, Height, Width)`
- 3D 输入：`(Batch, in_chans, PressureLevels, Height, Width)`

内部统一做法：

- 在 canonical Pangu 中，对 2D 输入补一个长度为 1 的伪 `PressureLevels`
- 以统一 3D 恢复语义处理 canonical Pangu 主干输出
- 恢复后按 `img_size` 做裁剪或对齐
- 若原始输入为 2D，最后再去掉伪三维层
- 若目标变体已经把中间表示压成 2D 网格并计划先做 2D recovery，再 reshape 回 upper-air 结构，则必须由对应变体卡或组件卡明确该恢复路径

# output_schema
- 2D 输出：`(Batch, out_chans, OutHeight, OutWidth)`
- 3D 输出：`(Batch, out_chans, OutPressureLevels, OutHeight, OutWidth)`
- 若输出面向 lite 变体，上层应进一步确认是直接得到 2D 场，还是先得到 `(Batch, Variables * Levels, Height, Width)` 后再 reshape 为高空五维结构

# parameters
- `img_size`
  - 2D: `(Height, Width)`
  - 3D: `(PressureLevels, Height, Width)`
- `patch_size`
  - 2D: `(PatchHeight, PatchWidth)`
  - 3D: `(PatchPressureLevels, PatchHeight, PatchWidth)`
- `in_chans`
  - 输入特征通道数
- `out_chans`
  - 输出变量通道数

# key_dependencies
- `recovery` 模块族内的相邻组件

# usage_and_risks
- 这是特征图级组件，不接收 token 序列。
- 输入通道数必须与 `in_chans` 一致。
- 若目标变体的中间表示已经是 2D 网格，本卡只能作为输出语义参考，不能自动证明其内部恢复实现必须仍是 3D。
- 不应把本卡理解成“Pangu 家族 recovery 都必须是统一 3D recovery”。
- 在 2D-lite 任务中，应显式检查：恢复前特征 rank、恢复后对齐策略，以及 upper-air reshape 的位置。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/recovery/pangupatchrecovery.py`
- `{onescience_path}/onescience/src/onescience/modules/recovery/onerecovery.py`
