# pipeline_responsibility

负责把 `RHS/SOL/BC` 三组数组转换为 BENO 模型可消费的异构图样本，包含原始数组读取、边界归一化、输入场平滑、梯度构造、节点采样、图连接、边特征生成和预处理缓存。

# pipeline_architecture

```text
原始数组
  RHS_<prefix>_all.npy
    -> 坐标 / 输入场 / cell_state
  SOL_<prefix>_all.npy
    -> 监督目标
  BC_<prefix>_all.npy
    -> 边界值

预处理
  边界值归一化
  输入场平滑 + 梯度
  规则底网格采样
  MeshGenerator.ball_connectivity
  MeshGenerator.attributes

异构图输出
  G1: 场分支
  G2: 边界分支
  G1+2: 监督目标
  -> cached_<prefix>_<mode>_<count>.pt
```

# data_loading

- 从 `source.data_dir` 读取 `RHS_<file_prefix>_all.npy`、`SOL_<file_prefix>_all.npy`、`BC_<file_prefix>_all.npy`。
- 若 `source.cache_dir` 下存在当前 mode 与样本数对应的 `.pt` 缓存，优先直接加载。
- 否则执行完整预处理，并将 `data_list` 写入缓存。

# sampling_strategy

- train 使用前 `data.ntrain` 个样本。
- test 使用测试数量 `data.ntest` 对应的样本段。
- 节点采样与邻接构建由 `resolution` 和 `ns` 控制，底网格按 `resolution x resolution` 解释。
- 当前没有独立验证 split。

# data_transform

- `BC` 被 reshape 为固定边界点数并做归一化。
- `RHS` 中坐标、输入场和 `cell_state` 被拆分。
- 对输入场做平滑并计算两个方向梯度。
- 计算节点到边界的距离特征。
- 构造 `G1.x` 和 `G2.x`，其中 `G2` 将中间场特征置零以突出边界条件分支。
- 训练目标通过归一化器编码，测试目标保持原尺度。

# input_schema

- `source.data_dir`: 包含三组 npy 文件。
- `source.file_prefix`: 文件名前缀。
- `source.cache_dir`: 可写缓存目录。
- `RHS`: 默认列含义为 `[x, y, f, cell_state, ...]`。
- `SOL`: 默认第 0 列为标量监督目标。
- `BC`: 默认可 reshape 为 `[-1, 128, 1]`。

# output_schema

- 返回 `HeteroData`。
- `data["G1"].x`: `[NumNodes, 10]`。
- `data["G2"].x`: `[NumNodes, 10]`。
- `data["G1+2"].y`: 采样节点上的标量目标。
- 附加字段包括 `boundary`、`edge_index`、`edge_features`、`sample_idx`、`cell_state`。

# constraints

- 边界点数 128 是当前实现的硬编码假设。
- 底网格需适配方形 `resolution x resolution`。
- 只有 train/test 两个 dataloader。
- train/test 目标尺度处理不同，训练脚本需要显式处理解码和评估尺度。
- 首次预处理耗时较高，缓存目录应可写且容量足够。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/beno.py`
- `{onescience_path}/onescience/src/onescience/utils/beno/utilities.py`
- `{onescience_path}/onescience/src/onescience/datapipes/core/base_dataset.py`
