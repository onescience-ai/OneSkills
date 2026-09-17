# 时间并行与多时间尺度神经PDE推进

## 适用范围
本卡片适用于长时间多尺度PDE（偏微分方程）轨迹预测场景，核心目标是利用神经网络方法实现时间并行与多时间尺度的PDE推进。典型应用包括：长时间流体动力学模拟、多尺度物理过程建模、需要加速时间推进的科学计算任务。本场景不适用于：瞬态单时间尺度问题、纯数据驱动无物理约束的预测任务、以及无法定义PDE残差的纯统计建模问题。

## 输入
- **PDE轨迹数据集**：包含长时间序列的流场或其他物理场数据，需支持多时间尺度特征
- **数据契约**：定义输入变量、目标变量、单位、网格坐标系
- **训练配置**：包括框架、超参数、随机种子等
- **可选预训练权重**：用于迁移学习或微调场景

## 输出
- **可复现模型**：训练完成的Parareal neural solver或Temporal neural operator
- **任务结果**：测试集上的预测结果、推理耗时
- **物理一致性评估**：守恒残差、边界误差等物理约束验证
- **适用域报告**：明确模型的泛化边界和域外工况复核建议

## 流程节点
1. **数据接入与契约核验** → 检查数据文件可读性、样本数、变量单位、坐标系、缺失值等，生成数据清单和机器可读契约
2. **预处理与数据切分** → 统一物理量表示，按几何、工况或时间构造无泄漏切分，保存统计量与可逆变换
3. **模型配置与训练** → 使用Parareal neural solver或Temporal neural operator进行训练，记录训练指标和最佳权重
4. **批量推理与物理恢复** → 在独立测试集上推理，恢复原始单位、网格和物理派生量
5. **任务验收与适用域判定** → 评估统计误差、物理约束、泛化能力和计算收益，给出PASS/REJECT/BLOCKED结论

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型类型 | Parareal neural solver, Temporal neural operator | 场景需求书 | 两种可选的神经PDE求解器 |
| 默认训练框架 | PyTorch | 场景需求书 | 标准深度学习框架 |
| 默认epoch数 | 100 | 场景需求书 | 训练迭代次数 |
| 默认batch_size | 8 | 场景需求书 | 批处理大小 |
| 默认学习率 | 0.001 | 场景需求书 | 优化器学习率 |
| 默认early_stopping_patience | 15 | 场景需求书 | 早停耐心值 |
| 默认随机种子 | 42 | 场景需求书 | 可复现性保证 |
| 相对误差门限 | 0.1 (10%) | 场景需求书 | 测试集PASS/REJECT阈值 |

## 边界与分流
- **数据缺失**：缺少必填输入时返回BLOCKED并列出缺项，不得编造数据
- **训练失败**：训练验证损失出现非有限值时，需检查数据和超参数配置
- **域外工况**：超出适用域的工况需经CFD复核，不得仅凭平均误差宣称工程可用
- **物理约束违反**：守恒残差或边界误差超限时，需分析模型在物理一致性方面的缺陷

## 质量检查
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现
- 预测无NaN或Inf且形状单位正确
- 每个测试样本有唯一结果
- 推理未使用测试目标校正
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 回退策略
- 数据质量问题：返回BLOCKED状态，等待用户提供符合契约的数据
- 训练收敛失败：调整超参数或检查数据分布
- 推理异常：检查模型权重加载和数据预处理流程
- 适用域判定不确定：默认PASS但附加更严格的复核要求

## 资源召回建议
- 需要Parareal neural solver实现细节时，可召回相关论文证据
- 需要Temporal neural operator具体架构时，可参考Temporal Stencil Modeling相关文献
- 需要物理一致性评估方法时，可参考守恒残差和边界误差计算规范
- 域外工况复核时，建议召回CFD标准验证流程卡片

## 证据来源
[1] A Neural PDE Solver with Temporal Stencil Modeling
[2] Advection Augmented Convolutional Neural Networks
[3] Continuous Temporal Domain Generalization
[4] RandNet-Parareal: a time-parallel PDE solver using Random Neural Networks
[5] TENG: Time-Evolving Natural Gradient for Solving PDEs With Deep Neural Nets Toward Machine Precision
[6] PARCv2: Physics-aware Recurrent Convolutional Neural Networks for Spatiotemporal Dynamics Modeling
[7] Anamnesic Neural Differential Equations with Orthogonal Polynomial Projections
[8] CARE: Modeling Interacting Dynamics Under Temporal Environmental Variation
[9] Neural-Fly enables rapid learning for agile flight in strong winds
