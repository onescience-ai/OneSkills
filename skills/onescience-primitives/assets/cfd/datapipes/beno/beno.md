# Datapipe: BenoDatapipe

## 基本信息

- Datapipe 名称：`BenoDatapipe`
- 数据类型：`cfd`
- 主要任务：`elliptic PDE heterogeneous-graph surrogate learning`
- 数据组织方式：`fixed_prefix_npy_arrays_with_preprocessed_pt_cache`

## pipeline_responsibility

负责把 `RHS/SOL/BC` 三组数组转换为 BENO 模型可消费的异构图样本，包含原始数组读取、边界归一化、输入场平滑、梯度构造、节点采样、图连接、边特征生成和预处理缓存。

## 管道架构

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

## 数据加载

- 从 `source.data_dir` 读取 `RHS_<file_prefix>_all.npy`、`SOL_<file_prefix>_all.npy`、`BC_<file_prefix>_all.npy`。
- 若 `source.cache_dir` 下存在当前 mode 与样本数对应的 `.pt` 缓存，优先直接加载。
- 否则执行完整预处理，并将 `data_list` 写入缓存。

## 采样策略

- train 使用前 `data.ntrain` 个样本。
- test 使用测试数量 `data.ntest` 对应的样本段。
- 节点采样与邻接构建由 `resolution` 和 `ns` 控制，底网格按 `resolution x resolution` 解释。
- 当前没有独立验证 split。

## 数据转换

- `BC` 被 reshape 为固定边界点数并做归一化。
- `RHS` 中坐标、输入场和 `cell_state` 被拆分。
- 对输入场做平滑并计算两个方向梯度。
- 计算节点到边界的距离特征。
- 构造 `G1.x` 和 `G2.x`，其中 `G2` 将中间场特征置零以突出边界条件分支。
- 训练目标通过归一化器编码，测试目标保持原尺度。

## 输入规格

- `source.data_dir`: 包含三组 npy 文件。
- `source.file_prefix`: 文件名前缀。
- `source.cache_dir`: 可写缓存目录。
- `RHS`: 默认列含义为 `[x, y, f, cell_state, ...]`。
- `SOL`: 默认第 0 列为标量监督目标。
- `BC`: 默认可 reshape 为 `[-1, 128, 1]`。

## 输出规格

- 返回 `HeteroData`。
- `data["G1"].x`: `[NumNodes, 10]`。
- `data["G2"].x`: `[NumNodes, 10]`。
- `data["G1+2"].y`: 采样节点上的标量目标。
- 附加字段包括 `boundary`、`edge_index`、`edge_features`、`sample_idx`、`cell_state`。

## 约束条件

- 边界点数 128 是当前实现的硬编码假设。
- 底网格需适配方形 `resolution x resolution`。
- 只有 train/test 两个 dataloader。
- train/test 目标尺度处理不同，训练脚本需要显式处理解码和评估尺度。
- 首次预处理耗时较高，缓存目录应可写且容量足够。

## 启动方式

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd import BENODatapipe

cfg = OmegaConf.load("conf/beno.yaml")
datapipe = BENODatapipe(cfg.datapipe, distributed=False)
train_loader, train_sampler = datapipe.train_dataloader()
test_loader, test_sampler = datapipe.test_dataloader()
```

CLI 示例：

```sh
python train.py --config-name beno datapipe.source.data_dir=/data/BENO datapipe.source.file_prefix=example datapipe.source.cache_dir=/data/BENO/cache datapipe.data.ntrain=1000 datapipe.data.ntest=200 datapipe.dataloader.batch_size=8
```

## 输入规格

- 数据目录需包含 `RHS_<prefix>_all.npy`、`SOL_<prefix>_all.npy`、`BC_<prefix>_all.npy`。
- `cache_dir` 建议独立于原始数据目录，便于清理和复用。
- 配置 `resolution`、`ns` 与原始数组空间分辨率保持一致。

## 运行接口

- `BENODataset(config, mode="train"|"test")`: 读取或生成异构图样本。
- `BENODatapipe(config, distributed=False)`: 同时构造训练和测试数据集。
- `train_dataloader()`: 返回训练 `GeoDataLoader` 和 sampler。
- `test_dataloader()`: 返回测试 `GeoDataLoader` 和 sampler。

## 主要函数

- `__getitem__`
- `train_dataloader`
- `test_dataloader`

## 执行资源

- 首次运行需要较多 CPU 时间完成平滑、梯度、距离和图边构造。
- 缓存写入需要本地磁盘空间。
- batch 后是图结构数据，节点数和边数会影响内存占用。

## 操作限制

- 没有 `val_dataloader`。
- 不适合边界点数不是 128 且未修改源码的数据。
- 不适合目标列不是 `SOL[..., 0]` 的多变量监督任务。
- 缓存与 `file_prefix/mode/count` 绑定，配置变化后需确认缓存是否过期。

## 规划决策

### 描述

该原语用于选择 BENO 异构图数据协议，将规则底网格椭圆 PDE 数据变成场分支和边界分支共同驱动的图样本。

### 使用时机

- 数据由 RHS、解场和边界条件三类数组组成。
- 模型需要 BENO 风格 `G1/G2/G1+2` 异构图。
- 任务强调边界条件和内部场共同决定标量解。
- 希望预处理后缓存，减少重复构图成本。

### 输入

- 三组 npy 文件和文件前缀。
- 训练/测试样本数。
- 网格分辨率、邻域采样参数和缓存目录。
- 目标是否需要保持 BENO 默认归一化协议。

### 输出

- train/test 图 dataloader。
- 缓存的 `.pt` 异构图样本列表。
- 每个样本的节点特征、边特征、边界信息和监督目标。

### 执行步骤

1. 校验三个 npy 文件是否存在且样本数一致。
2. 校验 `BC` 是否能 reshape 到固定边界点协议。
3. 设置 `cache_dir`，避免重复预处理。
4. 初始化训练集并生成缓存。
5. 初始化测试集，确认目标尺度与评估逻辑匹配。
6. 将 dataloader 接入 BENO 或兼容模型。

### 约束

- 当前实现强依赖固定列布局和边界点数。
- 训练和测试目标尺度不同。
- 图构建参数与底网格分辨率不匹配会导致样本语义错误。

### 下一阶段建议

若新数据仍是椭圆 PDE 但边界点数不同，先修改预处理 reshape 与边界特征逻辑；若数据是时序 CFD 或规则网格基准，优先考虑 CFDBench、PDEBench 或 DeepCFD。

### 回退策略

- 缓存损坏时删除对应 `cached_<prefix>_<mode>_<count>.pt` 后重建。
- 边界点数不匹配时先离线重采样边界到 128 点。
- 预处理过慢时先用小 `ntrain/ntest` 验证协议，再放大数据规模。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/beno.py`
- `{onescience_path}/onescience/src/onescience/utils/beno/utilities.py`
- `{onescience_path}/onescience/src/onescience/datapipes/core/base_dataset.py`
