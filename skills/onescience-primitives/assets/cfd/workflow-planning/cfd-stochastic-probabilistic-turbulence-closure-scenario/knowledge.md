# 随机微分与概率粗粒化湍流闭合 — 场景总览

## 适用范围

面向多尺度湍流系统，当粗尺度状态轨迹可用但细尺度闭合项缺失或不确定时，本场景描述一套完整的随机微分与概率粗粒化湍流闭合建模流程。适用于：LES/RANS 子网格尺度建模、多尺度流体动力学降阶、从观测数据学习随机闭合项、概率预测不确定性量化。不适用于：纯确定性闭合模型、无尺度分离的均匀湍流、单尺度DNS直接求解。

## 输入

- 多尺度湍流粗细状态轨迹数据集（DNS/LES/实验数据）
- 数据契约：变量定义、单位、网格坐标、时间/工况范围
- 可选：预训练权重、初始检查点

## 输出

- 可复现的闭合模型权重（best_checkpoint.pt）
- 先验/后验闭合项预测结果
- 物理一致性评估报告
- 适用域报告（含边界工况复核建议）
- 任务验收结果（PASS/REJECT/BLOCKED）

## 流程节点

```
数据接入与契约核验 (s01)
    ↓
预处理与数据切分 (s02)
    ↓
模型配置与训练 (s03)
    ↓
闭合项预测与后验CFD耦合 (s04)
    ↓
任务验收与适用域判定 (s05)
```

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | 场景需求书 | 深度学习框架 |
| epochs | 100 | 场景需求书 | 默认训练轮数 |
| batch_size | 8 | 场景需求书 | 默认批大小 |
| learning_rate | 0.001 | 场景需求书 | 默认学习率 |
| early_stopping_patience | 15 | 场景需求书 | 早停耐心值 |
| train/val/test比例 | 0.7/0.15/0.15 | 场景需求书 | 默认切分比例 |
| seed | 42 | 场景需求书 | 随机种子 |
| MAX_RELATIVE_L2 | 0.1 | 场景需求书 | 默认相对误差门限 |

## 边界与分流

- 数据文件不可读或样本不可追溯 → 返回 BLOCKED，列出缺项
- 训练验证损失出现非有限值 → 重新检查数据与模型配置
- 闭合张量/通量不满足约束 → 调整模型架构或训练策略
- 后验求解出现非物理发散 → 检查闭合项可实现性，必要时降级为先验评估
- 域外工况测试失败 → 明确标注适用域限制，建议CFD复核

## 质量检查

- 数据集：文件可读、样本可追溯、无训练测试泄漏
- 训练：损失均为有限值、最佳权重可重新加载、配置可复现
- 预测：闭合张量满足约束、后验求解稳定、均值剖面与能谱验证通过
- 验收：统计与物理指标同时报告、最差样本可追溯、结论含适用域限制

## 回退策略

- 训练失败 → 检查数据质量、调整超参数、尝试不同随机种子
- 后验耦合失败 → 降级为纯先验评估，仅报告闭合项预测误差
- 适用域外工况 → 标记为不适用，建议使用DNS或实验数据重新训练

## 资源召回建议

- 需要了解湍流闭合理论基础时召回本卡
- 需要了解Neural SDE或多尺度建模方法时召回方法卡
- 需要了解数据切分策略时召回预处理卡
- 需要了解验收标准时召回验收卡

## 证据来源

[1] Grigo, C., Koutsourelakis, P.-S. (2019). A physics-aware, probabilistic machine learning framework for coarse-graining high-dimensional systems in the Small Data regime. Journal of Computational Physics, 397, 108842. DOI: 10.1016/j.jcp.2019.05.053
[2] Ilersich, A.F., Nair, P.B. (2025). Learning Stochastic Multiscale Models. arXiv:2506.22655.
[3] Heyder, F., Schumacher, J. (2021). Echo State Network for two-dimensional turbulent moist Rayleigh-Bénard convection. Physical Review E, 103, 053107. DOI: 10.1103/PhysRevE.103.053107
[4] Charalampopoulos, A.-T.G., Sapsis, T.P. (2022). Machine-learning energy-preserving nonlocal closures for turbulent fluid flows and inertial tracers. Physical Review Fluids, 7, 024305. DOI: 10.1103/PhysRevFluids.7.024305
