# Datapipe: DeepmindCylinderflowDatapipe

## 基本信息

- Datapipe 名称：`DeepmindCylinderflowDatapipe`
- 数据类型：`cfd`
- 主要任务：`mesh-graph cylinder-flow next-step prediction`
- 数据组织方式：`split_tfrecord_trajectories_with_meta_json`

## pipeline_responsibility

负责将 DeepMind CylinderFlow 轨迹 TFRecord 解析为 DGL 图样本，完成网格拓扑恢复、边特征生成、节点特征/目标构造、训练噪声注入、统计量保存和 GraphDataLoader 封装。

## 管道架构

```text
数据目录
  meta.json
    -> field_names / features / trajectory metadata
  train.tfrecord
  valid.tfrecord
  test.tfrecord

TFRecord 解析
  trajectory
    -> cells
    -> mesh_pos
    -> node_type
    -> velocity / pressure

时间展开
  idx -> trajectory_id + time_id
  t 时刻特征
    -> ndata["x"]: velocity_t + node_type_onehot
  t+1 目标
    -> ndata["y"]: velocity/pressure target
  cells -> DGL edges -> edata["x"]

输出
  train: graph
  val/test: (graph, cells, mask)
```

## 数据加载

- 从 `source.data_dir/meta.json` 读取字段和序列元数据。
- 读取 `train.tfrecord`、`valid.tfrecord`、`test.tfrecord`。
- `mode="val"` 在内部映射到 `valid.tfrecord`。
- 从 `source.stats_dir` 读取或写入 `edge_stats.json` 和 `node_stats.json`。

## 采样策略

- 每个 split 配置轨迹数量和每条轨迹保留的时间步数。
- 一个 dataset item 对应某条轨迹的某个相邻时间步对。
- 索引规则为 `gidx = idx // (num_steps - 1)`，`tidx = idx % (num_steps - 1)`。
- train 按样本图打乱，val/test 通常不打乱。

## 数据转换

- 将 cell 拓扑转为双向图边。
- 边特征由相对位移和距离范数组成，并按训练统计量标准化。
- 节点输入通常由二维速度和四维节点类型 one-hot 拼接。
- 目标为下一时刻速度差或状态项以及压力相关变量。
- 训练阶段按 `data.noise_std` 对部分节点速度加噪。
- 生成 rollout mask，区分可预测节点。

## 输入规格

- `<data_dir>/meta.json`。
- `<data_dir>/train.tfrecord`、`valid.tfrecord`、`test.tfrecord`。
- 配置 `data.train_samples/train_steps/val_samples/val_steps/test_samples/test_steps/noise_std`。
- 配置 `source.stats_dir` 保存统计量。

## 输出规格

- 训练阶段返回 `DGLGraph`。
- 验证/测试阶段返回 `(DGLGraph, cells, mask)`。
- `graph.ndata["x"]`: `[NumNodes, 6]`，通常为 `2` 维速度 + `4` 维节点类型 one-hot。
- `graph.ndata["y"]`: `[NumNodes, 3]`，通常为目标速度项和压力项。
- `graph.edata["x"]`: 边相对位移和距离特征。

## 约束条件

- 依赖 TFRecord 数据和 `meta.json` 字段约定。
- 依赖 TensorFlow 解析 TFRecord，依赖 DGL 承载图。
- 非训练 split 需要训练阶段生成或可读取的统计量。
- train 与 val/test 返回协议不同，训练脚本必须分别处理。
- 该原语不是通用 DGL 图模板，节点/目标维度与示例模型配置强绑定。

## 启动方式

Python API 启动示例：

```python
from omegaconf import OmegaConf
from onescience.datapipes.cfd import DeepMind_CylinderFlowDatapipe

cfg = OmegaConf.load("conf/mgn_cylinderflow.yaml")
datapipe = DeepMind_CylinderFlowDatapipe(cfg.datapipe, distributed=False)
train_loader, train_sampler = datapipe.train_dataloader()
val_loader, val_sampler = datapipe.val_dataloader()
test_loader = datapipe.test_dataloader()
```

CLI 示例：

```sh
python train.py --config-name mgn_cylinderflow datapipe.source.data_dir=/data/cylinder_flow datapipe.source.stats_dir=/data/cylinder_flow/stats datapipe.data.train_samples=1000 datapipe.data.train_steps=600 datapipe.data.val_samples=100 datapipe.data.val_steps=600 datapipe.dataloader.batch_size=2
```

## 输入规格

- 数据目录必须包含 `meta.json` 和三个 split 的 TFRecord。
- `stats_dir` 应可写；训练阶段会生成统计量。
- 配置每个 split 的样本数和时间步数，避免超过 TFRecord 实际长度。

## 运行接口

- `DeepMind_CylinderFlowDataset(config, mode)`: 解析指定 split 为图样本。
- `DeepMind_CylinderFlowDatapipe(params, distributed)`: 构造三个 split 的 GraphDataLoader。
- `train_dataloader()`: 返回训练 GraphDataLoader 和 sampler。
- `val_dataloader()`: 返回验证 GraphDataLoader 和 sampler。
- `test_dataloader()`: 返回测试 GraphDataLoader。

## 主要函数

- `__getitem__`
- `train_dataloader`
- `val_dataloader`
- `test_dataloader`

## 执行资源

- 需要 TensorFlow TFRecord 读取环境。
- 需要 DGL 图运行环境。
- 图 batch 内存与节点数、边数和轨迹展开长度相关。
- 训练噪声和统计量计算主要消耗 CPU/GPU 张量计算资源。

## 操作限制

- 不支持普通 npy、h5、VTK 输入。
- val/test batch 不是单纯 graph，调用侧需要解包 `cells` 和 `mask`。
- 统计量缺失会影响非训练 split 初始化。
- 节点类型、速度和压力字段变化时需要同步改模型配置。

## 规划决策

### 描述

该原语用于选择 DeepMind MeshGraphNet 风格圆柱流 rollout 数据流，把 TFRecord 轨迹拆成逐时间步图样本。

### 使用时机

- 数据是 DeepMind 风格 `meta.json + split.tfrecord`。
- 任务是瞬态圆柱绕流或相似网格时序预测。
- 模型需要 DGL 图、边特征、节点类型 one-hot 和 rollout mask。
- 训练流程来自 Vortex_shedding_mgn 或兼容 MeshGraphNet。

### 输入

- TFRecord 数据根目录。
- 每个 split 的轨迹数量和时间步数。
- 训练噪声标准差。
- 统计量输出目录和 batch 参数。

### 输出

- train/val/test GraphDataLoader。
- 训练图样本和验证/测试 rollout 解包样本。
- 节点/边归一化统计量。

### 执行步骤

1. 校验 `meta.json` 与 TFRecord 文件存在。
2. 先运行训练 split 生成统计量。
3. 确认节点输入和目标维度与模型配置一致。
4. 设置每条轨迹展开时间步，控制总样本量。
5. 在训练脚本中区分 train 与 val/test 返回协议。

### 约束

- 依赖 TensorFlow 和 DGL。
- 图拓扑来自 cells，缺失 cells 无法构造边。
- 该协议以 rollout 为中心，不适合静态单步几何回归。

### 下一阶段建议

若新数据仍是 TFRecord 轨迹但字段稍有不同，优先写解析适配；若是粒子拉格朗日数据，使用 DeepMindLagrangian；若是规则网格，改用 CFDBench 或 PDENNEval。

### 回退策略

- 统计量缺失时先单独初始化训练集。
- 环境缺 TensorFlow/DGL 时先转换为 h5/npy，再选择其它 datapipe。
- batch 内存不足时降低 batch size 或减少 `num_steps`。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/deepmind_cylinderflow.py`
- `{onescience_path}/onescience/examples/cfd/Vortex_shedding_mgn/train.py`
- `{onescience_path}/onescience/examples/cfd/Vortex_shedding_mgn/conf/mgn_cylinderflow.yaml`
