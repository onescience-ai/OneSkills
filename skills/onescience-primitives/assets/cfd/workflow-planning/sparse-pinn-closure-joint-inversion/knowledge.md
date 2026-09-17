# 稀疏观测PINN均值流与闭合联合反演

## 适用范围

面向稀疏实验观测与RANS方程数据，利用Physics-Informed Neural Networks (PINN)联合反演均值流场与湍流闭合项。适用于以下场景：实验数据点稀疏（无法完整覆盖流场空间）、传统RANS闭合模型精度不足、需要从有限测量中推断完整流场信息。不适用于：数据密集且均匀分布的传统CFD验证场景、完全无物理约束的纯数据驱动替代模型、以及需要直接求解N-S方程而非RANS近似的高保真需求。

## 输入

- **稀疏实验观测数据**：空间分布不均匀的流场测量点（如压力、速度、雷诺应力等），可能来自PIV、LDV、热膜等实验手段
- **RANS方程数据**：控制方程离散形式，包括动量方程、连续性方程及相关源项
- **几何信息**：计算域几何描述与网格拓扑
- **工况参数**：来流速度、湍流强度、雷诺数等运行工况

## 输出

- **均值流场预测**：完整的RANS均值速度场、压力场
- **湍流闭合项**：Reynolds应力张量或等效涡粘性系数分布
- **物理一致性评估**：守恒残差、能谱验证、边界误差报告
- **适用域报告**：明确模型有效工况范围与域外工况复核建议

## 流程节点

数据接入与契约核验 → 预处理与数据切分 → 模型配置与训练 → 闭合项预测与后验CFD耦合 → 任务验收与适用域判定

每步含：操作、参数、工具、质量门禁（详见 workflow 级卡片 cfd-pinn-turbulence-closure-workflow）

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型类型 | Turbulence PINN | [场景需求书] | Physics-Informed Neural Network用于湍流闭合建模 |
| 框架 | PyTorch | [场景需求书] | 默认训练框架 |
| 默认训练轮数 | 100 | [场景需求书] | 可根据收敛情况调整 |
| 默认批大小 | 8 | [场景需求书] | 按显存调整 |
| 默认学习率 | 0.001 | [场景需求书] | 基线超参数 |
| 早停耐心 | 15 | [场景需求书] | 防止过拟合 |
| 数据切分比例 | train:0.7 / val:0.15 / test:0.15 | [场景需求书] | 按几何或轨迹分组切分 |
| 相对误差门限 | 0.1 | [场景需求书] | 测试集放行阈值 |
| 外推测试 | true | [场景需求书] | 需执行几何或工况外推测试 |

## 边界与分流

- **数据不足或缺失关键变量**：返回BLOCKED，列出缺项，不得编造数据
- **训练发散或损失非有限值**：检查学习率、网络架构、物理约束权重；必要时降低学习率或增加正则化
- **后验CFD求解非物理发散**：检查闭合项可实现性（如正定性、量纲一致性），必要时对闭合项施加物理约束裁剪
- **域外工况测试失败**：明确标注适用域边界，建议CFD复核，不得仅凭平均误差宣称工程可用

## 质量检查

- 统计误差（RMSE、L2范数）与物理约束（守恒残差、能谱斜率）必须同时报告
- 最差样本必须可追溯至具体工况与位置
- 结论必须包含适用域限制与复核建议
- 域外测试通过`PASS_REJECT_BLOCKED.txt`明确判定

## 回退策略

- 训练失败：检查数据质量与物理约束定义，尝试简化网络或调整超参数
- 后验耦合失败：降级为纯先验评估，仅报告闭合项预测精度
- 适用域不明：扩大外推测试范围，或标记为需进一步验证

## 资源召回建议

当用户需求涉及以下关键词时召回本卡片：PINN、turbulence closure、RANS、sparse observation、joint inversion、flow inference、physics-informed、稀疏观测、湍流闭合、联合反演、均值流。配套资源：cfd-pinn-turbulence-closure-workflow（工作流详细步骤）、cfd-turbulence-pinn-model-training（训练方法卡）。

## 证据来源

[1] Turbulence Closure in RANS and Flow Inference around a Cylinder using PINNs and Sparse Experimental Data, arXiv:2510.06049, 2025
[2] Turbulence closure in Reynolds-averaged Navier–Stokes and flow inference around a cylinder using physics-informed neural networks, J. Fluid Mech., 2026, DOI: 10.1017/jfm.2026.11471
