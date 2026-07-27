## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/vortex_shedding_mgn`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/vortex_shedding_mgn`。入口为 `cylinder_flow`。

## data_schema
`meta.json` 描述字段和轨迹元数据；`train/valid/test.tfrecord` 存储 cells、mesh_pos、node_type、velocity、pressure；`stats` 存储节点/边归一化统计。

## task_usage
适用于 MeshGraphNet 圆柱绕流、涡街单步预测、多步 rollout 和非结构网格图建模。

## integration_paths
使用 `cfd/datapipes/deepmind_cylinderflow`；配置 train/val/test 样本数和步数、noise_std、stats_dir。

## preparation_requirements
确认 TensorFlow/DGL 可用；检查统计文件与 TFRecord 同版本；小规模读取单个图确认节点/边维度。

## consumption_interfaces
训练返回 DGLGraph；验证/测试返回 `(graph,cells,mask)`，节点含速度和类型，边含相对位移和距离。

## evaluation_protocol
报告单步速度/压力误差、多步 rollout 误差和 mask 内误差；固定 valid/test split。

## operation_limits
train 与 val/test batch 协议不同；非训练 split 需要训练统计量；TFRecord 解析依赖不可缺。
