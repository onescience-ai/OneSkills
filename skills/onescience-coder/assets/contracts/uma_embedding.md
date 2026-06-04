# Contract: uma_embedding.py

## 基本信息

- 组件名：`UMA Embedding Family`
- 所属模块族：`materials / uma / embedding`
- 统一入口：`direct_import`
- 注册名：`not_applicable`
- 主源码：`./onescience/src/onescience/modules/embedding/uma_embedding.py`

## 组件职责

提供 UMA 主干初始化所需的条件与结构嵌入，将原子图中的边度、charge、spin、dataset 条件编码成 eSCNMD backbone 可消费的特征。

覆盖组件：

- `EdgeDegreeEmbedding`
- `ChgSpinEmbedding`
- `DatasetEmbedding`

## 输入契约

- `atomic_numbers`: `(NumAtoms,)`
- `edge_index`: `(2, NumEdges)`
- `edge_distance`: `(NumEdges,)`
- `edge_distance_vec`: `(NumEdges, 3)`
- `batch`: `(NumAtoms,)`
- `charge`: `(NumGraphs,)` 或 batch 字段
- `spin`: `(NumGraphs,)` 或 batch 字段
- `dataset`: dataset name / id
- Wigner / SO3 mapping 相关对象

## 输出契约

- 边度嵌入：与节点球谐特征同形态或可加到节点特征的张量
- charge/spin 嵌入：系统级条件向量，可广播到节点或图级特征
- dataset 嵌入：数据集条件向量，用于多数据集 head 或 MoE 路由

## 关键参数

- `sphere_channels`
- `lmax`
- `mmax`
- `edge_channels_list`
- `cutoff`
- `rescale_factor`
- `embedding_type`
- `embedding_target`
- `dataset_list`
- `embedding_size`

## 典型调用位置

- `eSCNMDBackbone`
- `eSCNMDMoeBackbone`
- UMA Hydra checkpoint 初始化
- UMA fine-tuning 与 inference forward

## 常见修改点

- 新增 dataset：同步扩展 `dataset_list`、dataset embedding、head wrapper 和 task 配置。
- 启用 charge/spin：确认 batch 字段存在，且训练和推理的取值语义一致。
- 改 edge embedding 通道：同步检查 `uma_radial.md`、`uma_escn_md_block.md` 和 checkpoint。

## 风险点

- `dataset_list` 漏项会导致 batch 内 dataset key 无法映射。
- charge/spin 缺失时不能默认填无意义值；要确认预训练模型是否依赖该条件。
- edge 通道不匹配会在径向 MLP 或 block 线性层出现 shape mismatch。
- 多数据集任务中 dataset embedding、head wrapper、normalizer 必须同源。

## 源码锚点

- `./onescience/src/onescience/modules/embedding/uma_embedding.py`
- `./onescience/src/onescience/models/UMA/uma_escn_md.py`
- `./onescience/src/onescience/models/UMA/uma_escn_moe.py`

## 下钻关系

- 径向边特征：`./uma_radial.md`
- 主干 block：`./uma_escn_md_block.md`
- MoE 路由：`./uma_moe.md`
- 数据字段：`../datapipes/materials_uma.md`
