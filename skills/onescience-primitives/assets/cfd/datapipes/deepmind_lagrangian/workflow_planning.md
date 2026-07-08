# description

该原语用于拉格朗日粒子仿真任务编排，将粒子历史窗口转换为可 rollout 的动态图样本。

# when_to_use

- 数据是粒子轨迹而不是固定网格场。
- 模型需要预测下一步位置、速度或加速度。
- 任务要求动态重建邻接关系。
- 训练中需要噪声增强提高 rollout 稳定性。

# inputs

- `metadata.json` 与 split TFRecord。
- 历史步数、连接半径、粒子类型数量。
- split 名称、序列数和时间步数。
- 噪声标准差和 dataloader 参数。

# outputs

- train/valid/test GraphDataLoader。
- 每个样本的 DGLGraph。
- 反归一化、输入/目标解包和时间积分辅助接口。

# procedure

1. 校验 metadata 统计量、边界和半径配置。
2. 确认 TFRecord 的 split 名称与配置一致。
3. 设置 `num_history` 以匹配模型输入维度。
4. 根据粒子数评估半径图构建成本。
5. 构造 datapipe 并在 rollout 阶段使用 `graph_update`。

# constraints

- 粒子类型编码数量必须覆盖数据中全部类型。
- 动态粒子 mask 决定哪些节点参与训练目标。
- 半径过大将显著增加边数，半径过小可能断开物理邻域。

# next_phase_recommendation

若数据是网格圆柱流 TFRecord，优先 DeepMind CylinderFlow；若需要规则网格 operator learning，优先 PDENNEval；若要处理 VTK 几何外流场，使用 AirfRANS 或 ShapeNetCar。

# fallback

- 粒子数太大时减小半径、下采样粒子或预计算邻接。
- TFRecord 解析失败时先转换为中间 npy/h5 格式验证字段。
- rollout 发散时降低噪声或检查统计量与时间步长。
