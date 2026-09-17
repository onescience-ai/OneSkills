# CFD Foundation Model Multiphysics Operator Transfer Scenario

## 适用范围

面向将预训练科学基础模型（PDE foundation model、Pretrained neural operator）迁移到目标多物理场预测任务的场景，涉及多物理多分辨率大规模预训练数据、算子学习、物理一致性评估与适用域判定。适用于需要利用预训练知识加速新物理场模型训练、降低数据需求的CFD应用，不适用于单一物理场且无需迁移学习的传统CFD模拟。

## 输入

- **预训练模型权重**：已训练完成的 PDE foundation model 或 Pretrained neural operator checkpoint
- **目标任务数据**：目标物理场的训练数据（含输入变量、目标变量、网格坐标、边界条件）
- **数据契约**：变量定义、单位、坐标系、网格拓扑、工况范围
- **训练配置**：超参数、随机种子、计算设备
- **验收指标**：统计误差门限、物理约束阈值、外推测试开关

## 输出

- **迁移后模型权重**：fine-tuned 或 adapted 的目标域 checkpoint
- **任务结果**：预测场、逐变量误差、边界误差、守恒残差
- **适用域报告**：外推测试结论、域外工况复核建议
- **可复现制品**：训练日志、环境配置、随机种子记录

## 流程节点

1. **数据接入与契约核验** → 检查多物理多分辨率数据完整性，建立数据契约
2. **预处理与数据切分** → 无量纲化、归一化、按几何/轨迹/工况无泄漏切分
3. **模型配置与训练** → 加载预训练权重，fine-tune 或 transfer 到目标任务
4. **批量推理与物理恢复** → 独立测试集推理，恢复原始单位与网格
5. **任务验收与适用域判定** → 统计误差+物理约束+泛化能力联合评估

## 关键参数

### 通用判据（方法层）
| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 数据切分 | 按几何/轨迹/工况互斥 | 场景需求书 | 避免训练测试泄漏 |
| 预训练权重检查 | 结构兼容性验证 | 场景需求书 | 防止架构不匹配 |
| 误差门限 | relative_L2 ≤ 0.1 | 场景需求书 | 任务级放行阈值 |
| 物理约束 | conservation_residual + boundary_error | 场景需求书 | 守恒与边界条件验证 |
| 外推测试 | OOD 几何或工况测试 | 场景需求书 | 适用域判定 |

### 校准数值
> 以下数值来自场景需求书，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认 batch_size | 8 | 场景需求书 | 显存相关 |
| 默认 learning_rate | 0.001 | 场景需求书 | 微调学习率 |
| early_stopping_patience | 15 | 场景需求书 | 训练终止条件 |

## 边界与分流

- **预训练权重不可用**：转向从头训练（需更多数据与计算资源）
- **目标域与源域物理差异过大**：转向 domain adaptation 或 multi-task pretraining 策略
- **域外工况命中**：必须经 CFD 复核，不得仅凭平均误差宣称工程可用
- **物理约束违反严重**：reject 模型，需调整 loss 权重或引入 hard constraint

## 质量检查

- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现
- 预测无 NaN 或 Inf 且形状单位正确
- 统计与物理指标同时报告
- 最差样本可追溯

## 回退策略

- 模型收敛失败 → 降低学习率、增加预热轮次、检查数据质量
- 物理约束违反 → 增加 PDE 残差 loss 权重、引入 boundary penalty
- 外推性能不足 → 扩充 OOD 训练数据、使用 domain randomization

## 资源召回建议

当用户涉及以下关键词时召回本卡片：
- "科学基础模型"、"PDE foundation model"、"pretrained neural operator"
- "多物理算子迁移"、"算子学习迁移"
- "physics-informed transfer"、"operator transfer learning"

配套资源：
- cfd-pde-foundation-model-zero-shot-forecasting-workflow（零样本预测工作流）
- cfd-transformer-pde-operator-pretrain-finetune（Transformer PDE 算子预训练微调）

## 证据来源

[1] Poseidon: Efficient Foundation Models for PDEs, 2025
[2] Towards a Physics Foundation Model, 2025
[3] Pretraining Codomain Attention Neural Operators for Solving Multiphysics PDEs, 2025
[4] Data-Efficient Operator Learning via Unsupervised Pretraining and In-Context Learning, 2025
