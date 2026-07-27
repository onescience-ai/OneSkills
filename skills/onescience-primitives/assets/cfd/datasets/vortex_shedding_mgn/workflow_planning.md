## description
为 Vortex Shedding MGN CylinderFlow TFRecord 选择图解析、统计量和 rollout workflow。

## when_to_use
任务需要 DeepMind CylinderFlow、MeshGraphNet 或圆柱绕流涡街预测时使用。

## inputs
数据获取路径：`/public/share/sugonhpcapp01/onestore/onedatasets/vortex_shedding_mgn`。输入为 `cylinder_flow` 下 meta、TFRecord 和 stats。

## outputs
输出为 train/valid/test dataloader、DGLGraph schema、单步 loss 和 rollout 指标。

## procedure
1. 读取 meta，确认字段和 trajectory_length。
2. 配置 split 样本数、步数和 noise_std。
3. 检查 stats 是否可读。
4. 构造一个训练图和一个验证样本。
5. 训练单步模型。
6. 用 valid/test rollout 评测。

## constraints
TensorFlow/DGL 是硬依赖；train 与 val/test 返回协议不同；统计量要与 TFRecord 版本一致。

## next_phase_recommendation
先限制 train_samples/train_steps 做 smoke test，再扩大 rollout。

## fallback
若统计文件缺失，先用训练 split 重新生成；若 TFRecord 解析失败，记录环境依赖问题。
