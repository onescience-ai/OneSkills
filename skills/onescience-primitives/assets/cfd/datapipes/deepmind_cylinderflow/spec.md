# pipeline_responsibility

负责将 DeepMind CylinderFlow 轨迹 TFRecord 解析为 DGL 图样本，完成网格拓扑恢复、边特征生成、节点特征/目标构造、训练噪声注入、统计量保存和 GraphDataLoader 封装。

# pipeline_architecture

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

# data_loading

- 从 `source.data_dir/meta.json` 读取字段和序列元数据。
- 读取 `train.tfrecord`、`valid.tfrecord`、`test.tfrecord`。
- `mode="val"` 在内部映射到 `valid.tfrecord`。
- 从 `source.stats_dir` 读取或写入 `edge_stats.json` 和 `node_stats.json`。

# sampling_strategy

- 每个 split 配置轨迹数量和每条轨迹保留的时间步数。
- 一个 dataset item 对应某条轨迹的某个相邻时间步对。
- 索引规则为 `gidx = idx // (num_steps - 1)`，`tidx = idx % (num_steps - 1)`。
- train 按样本图打乱，val/test 通常不打乱。

# data_transform

- 将 cell 拓扑转为双向图边。
- 边特征由相对位移和距离范数组成，并按训练统计量标准化。
- 节点输入通常由二维速度和四维节点类型 one-hot 拼接。
- 目标为下一时刻速度差或状态项以及压力相关变量。
- 训练阶段按 `data.noise_std` 对部分节点速度加噪。
- 生成 rollout mask，区分可预测节点。

# input_schema

- `<data_dir>/meta.json`。
- `<data_dir>/train.tfrecord`、`valid.tfrecord`、`test.tfrecord`。
- 配置 `data.train_samples/train_steps/val_samples/val_steps/test_samples/test_steps/noise_std`。
- 配置 `source.stats_dir` 保存统计量。

# output_schema

- 训练阶段返回 `DGLGraph`。
- 验证/测试阶段返回 `(DGLGraph, cells, mask)`。
- `graph.ndata["x"]`: `[NumNodes, 6]`，通常为 `2` 维速度 + `4` 维节点类型 one-hot。
- `graph.ndata["y"]`: `[NumNodes, 3]`，通常为目标速度项和压力项。
- `graph.edata["x"]`: 边相对位移和距离特征。

# constraints

- 依赖 TFRecord 数据和 `meta.json` 字段约定。
- 依赖 TensorFlow 解析 TFRecord，依赖 DGL 承载图。
- 非训练 split 需要训练阶段生成或可读取的统计量。
- train 与 val/test 返回协议不同，训练脚本必须分别处理。
- 该原语不是通用 DGL 图模板，节点/目标维度与示例模型配置强绑定。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/cfd/deepmind_cylinderflow.py`
- `{onescience_path}/onescience/examples/cfd/Vortex_shedding_mgn/train.py`
- `{onescience_path}/onescience/examples/cfd/Vortex_shedding_mgn/conf/mgn_cylinderflow.yaml`
