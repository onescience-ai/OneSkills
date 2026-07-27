## description
为 Lagrangian MGN Water TFRecord 选择粒子窗口、半径图和 rollout workflow。

## when_to_use
任务需要 DeepMind Water 粒子动力学、MeshGraphNet 或拉格朗日流体预测时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/Lagrangian_MGN`。输入为 `data/Water/metadata.json` 和 TFRecord split。

## outputs
输出为 split 配置、history、noise、DGLGraph schema、单步和 rollout 指标。

## procedure
1. 读取 metadata，确认 dim、dt、bounds、统计量。
2. 配置 train/valid/test TFRecord 和样本数量。
3. 设置 history、noise_std、node type 数。
4. 构建一个样本图，检查节点/边字段。
5. 训练单步预测。
6. 执行 rollout 并记录动态粒子误差。

## constraints
依赖 TensorFlow/DGL；半径图成本高；metadata 不完整时不能训练。

## next_phase_recommendation
先限制 num_sequences/num_steps 做小规模验证。

## fallback
若 TFRecord 依赖不可用，只能做元数据和文件完整性检查。
