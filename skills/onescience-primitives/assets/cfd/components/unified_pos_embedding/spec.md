# component_info
unified_pos_embedding 位于 embedding 模块，是无状态函数原语，面向规则 1D/2D/3D 网格生成到参考网格的距离型位置编码。

# purpose
- 做什么：生成输入网格点到参考网格点的距离矩阵。
- 解决问题：将不同分辨率网格映射到固定参考锚点距离空间。
- 适用场景：PDE/CFD 网格相对位置特征、注意力 bias、跨分辨率条件编码。
- 不适用场景：非结构点云、经纬球面距离、可学习绝对位置表。

# input_schema
- `shapelist`: 长度为 1、2 或 3 的整数列表，如 `[L]`、`[H, W]`、`[D, H, W]`。
- `ref`: 每个维度参考网格分辨率。
- `batchsize=1`: 输出 batch 数。
- `device='cuda'`: 目标设备；传 `None` 时按 CUDA 可用性选择。

# output_schema
`pos`: `(Batch, N_input, N_ref)`，其中 `N_input=prod(shapelist)`，`N_ref=ref ** len(shapelist)`；元素是归一化坐标空间中的欧氏距离。

# parameters
- `shapelist`：输入规则网格尺寸。
- `ref`：参考锚点分辨率。
- `batchsize`：复制到 batch 维。
- `device`：输出设备。

# key_dependencies
- torch
- numpy

# usage_and_risks
- 输出矩阵规模为 `batchsize * prod(shapelist) * ref^dim`，高分辨率 3D 会快速占用大量显存。
- 只支持规则网格，不支持任意坐标输入。
- 默认 device 为 `cuda`，无 GPU 环境需显式传 `device='cpu'` 或 `None`。
- 源码对非法 shapelist 长度没有显式报错，可能返回未定义变量。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/embedding/unified_pos_embedding.py`
