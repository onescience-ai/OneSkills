# component_info
将二维或三维原始气象场切分为非重叠 patch，并投影到统一的 embedding 特征空间。

这是 Pangu 系列输入编码阶段的统一 patch embedding 组件。

该组件的核心实现包括 `PanguEmbedding`，定位为嵌入层，由上层 OneScience 模型或流水线通过 Python API 调用。

补充说明：

- 本知识默认描述的是 canonical Pangu / unified 3D trunk 场景中的 embedding 语义。
- 它可以作为 Pangu family-level 背景知识使用，但不能自动代表所有 lite / hybrid / 2D trunk 变体的 embedding 实现。

# purpose
把原始数值特征、patch 或图节点/边特征投影到统一隐空间，适用于主干网络进入前的特征标准化表达。

# input_schema
- 2D 输入：`(Batch, Variables, Height, Width)`
- 3D 输入：`(Batch, Variables, PressureLevels, Height, Width)`

内部统一做法：

- 在 canonical Pangu 中，对 2D 输入先补一个长度为 1 的伪 `PressureLevels`
- 再映射到统一的 Pangu embedding 语义空间
- patch 不整除时可按实现策略补齐或拒绝
- 若目标变体要求 surface 走 2D embedding、upper-air 走 3D embedding、再汇入共享 2D trunk，则必须由对应变体卡或组件卡明确后续 rank 变换，不能只依赖本卡推断

# output_schema
- 2D 输入在 canonical Pangu 中常作为进入统一 3D trunk 前的过渡表示。
- 3D 输出：`(Batch, embed_dim, OutPressureLevels, OutHeight, OutWidth)`
- 2D 分支若用于 canonical 流程，通常还需要补出压力层语义后再与 upper-air 合并。
 
其中：

- `OutPressureLevels = ceil(PressureLevels / PatchPressureLevels)` 或由具体实现约束
- `OutHeight = ceil(Height / PatchHeight)`
- `OutWidth = ceil(Width / PatchWidth)`
- 若输出将接入 2D-lite trunk，上层必须再次确认输出最终是 4D 网格、5D 体特征，还是已展平 token 序列

# parameters
- `img_size`
  - 2D: `(Height, Width)`
  - 3D: `(PressureLevels, Height, Width)`
- `patch_size`
  - 2D: `(PatchHeight, PatchWidth)`
  - 3D: `(PatchPressureLevels, PatchHeight, PatchWidth)`
- `Variables`
  - 输入变量数
- `embed_dim`
  - 输出特征维度
- `norm_layer`
  - 可选归一化层

# key_dependencies
- `embedding` 模块族内的相邻组件

# usage_and_risks
- 若目标是 canonical Pangu，可优先参考本卡。
- 若任务保留 Pangu 外部 I/O、但内部 trunk 已切换为 2D/shared-lite 结构，本卡只能提供 family-level 输入语义，不能单独决定中间 rank 走向。
- 不应把本卡理解成“Pangu 家族所有 embedding 都必须统一走 Conv3d”。
- 在 2D-lite 任务中，若忽略 branch-specific embedding 契约，容易把 upper-air 5D 特征直接传给只接受 4D 的 2D trunk。
- `patch_size` 变化会直接改变输出 token / feature grid 尺寸。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/embedding/panguembedding.py`
- `{onescience_path}/onescience/src/onescience/modules/embedding/oneembedding.py`
