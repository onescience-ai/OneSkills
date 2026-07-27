## access
数据获取路径优先使用 `${ONESCIENCE_DATASETS_DIR}/Lagrangian_MGN`；若运行环境未设置 `ONESCIENCE_DATASETS_DIR`，则回退到默认挂载路径 `/public/share/sugonhpcapp01/onestore/onedatasets/Lagrangian_MGN`。入口为 `data/Water`。

## data_schema
`metadata.json` 给出 bounds、dt、维度、connectivity radius 和速度/加速度统计；TFRecord 给出粒子类型和位置序列。

## task_usage
适用于 MeshGraphNet、粒子动力学、拉格朗日流体预测、随机游走噪声训练和长 rollout。

## integration_paths
使用 `cfd/datapipes/deepmind_lagrangian`；配置 history 步数、noise_std、num_node_types、split、num_sequences 和 num_steps。

## preparation_requirements
确认 TensorFlow/DGL 可用；检查 metadata 完整；限制序列数和步数做 smoke test；确认动态粒子 mask。

## consumption_interfaces
返回 DGLGraph，节点含当前位置、历史速度、边界距离、类型 one-hot，边含相对位移/距离，目标含下一状态。

## evaluation_protocol
报告单步位置/速度/加速度误差和多步 rollout 误差；动态粒子和运动学粒子分开统计。

## operation_limits
半径图构建成本高；split 必须使用官方 TFRecord；metadata 统计不可与其它粒子数据混用。
