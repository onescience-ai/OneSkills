# 贝叶斯PINN概率反演

## 适用范围
面向含噪观测与PDE先验数据，采用贝叶斯物理信息神经网络（B-PINN）进行概率反演，适用于流体力学、热传导、反应扩散等PDE控制问题的参数估计与不确定性量化。该方法结合了物理约束与贝叶斯推断，能够量化由于数据噪声和模型参数不确定性导致的预测不确定性。适用于正向问题（给定参数求解场）和逆向问题（从数据中反演参数）。

## 输入
- **含噪观测数据**：包括解场 \(u\)、源项 \(f\)、边界条件 \(b\) 的散点观测，各变量可具有不同的噪声水平。
- **PDE先验**：描述物理系统的微分方程，如泊松方程、Navier-Stokes方程、反应扩散方程等。
- **边界条件**：Dirichlet、Neumann、Robin或Cauchy边界条件。
- **数据契约**：定义变量、单位、坐标系、网格拓扑、时间/工况范围。
- **模型配置**：神经网络架构（层数、节点数）、训练超参数（学习率、批量大小、迭代次数）、后验估计方法（HMC或VI）。

## 输出
- **解场预测**：\(u(x)\) 的后验均值与标准差。
- **参数反演**：未知PDE参数 \(\lambda\) 的后验分布。
- **不确定性量化**：预测的可信区间，反映数据噪声和模型不确定性。
- **物理一致性评估**：PDE残差、边界误差、守恒误差。
- **适用域报告**：模型在训练域内外的表现，明确适用边界。

## 流程节点
1. **数据接入与契约核验**：接入含噪观测与PDE先验数据，核验样本、变量、单位、网格坐标及许可。
2. **预处理与数据切分**：统一物理量与表示，按几何、工况或时间构造无泄漏切分。
3. **模型配置与训练**：使用贝叶斯PINN训练模型，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。
4. **方程求解与物理残差恢复**：在查询配点或网格上恢复解场、导数、边界值与方程残差。
5. **任务验收与适用域判定**：评估统计误差、关键物理约束、泛化能力和计算收益。

每步含：操作、参数、工具、质量门禁。

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 后验估计方法 | Hamiltonian Monte Carlo (HMC) | [1] | HMC比VI更准确，但计算成本更高 |
| 网络架构 | 2隐藏层，每层50节点 | [1] | 标准配置，可根据问题复杂度调整 |
| 先验分布 | 独立标准高斯分布 | [1] | 权重和偏差的先验 |
| 噪声模型 | 高斯噪声，标准差已知 | [1] | 各传感器噪声水平可不同 |
| 损失函数 | 数据损失 + 物理损失 | [2] | 加权组合，权重可学习 |
| 评估指标 | 相对L2误差、PDE残差、边界误差、守恒误差 | [3] | 多指标综合评估 |
| 不确定性量化 | 后验预测分布的均值和标准差 | [1] | 反映数据噪声和模型不确定性 |

## 边界与分流
- **HMC vs VI**：当计算资源充足且需要高精度不确定性时，优先选择HMC；当需要快速近似时，使用VI。
- **网络架构**：若PDE高度非线性，增加网络宽度或深度；若问题简单，可使用更小网络。
- **噪声处理**：若噪声水平未知，可将其作为超参数进行估计。
- **适用域外工况**：若测试域外工况，需进行CFD复核。

## 质量检查
- **训练验证损失均为有限值**：防止梯度爆炸或消失。
- **最佳权重可重新加载**：确保模型可复现。
- **配置环境随机种子可复现**：保证实验可重复。
- **解场导数与残差均为有限值**：确保物理合理性。
- **边初值逐项满足门限**：边界条件满足预设误差阈值。
- **统计与物理指标同时报告**：避免仅凭平均误差宣称工程可用。
- **最差样本可追溯**：便于分析模型弱点。
- **结论含适用域限制与复核建议**：明确模型适用范围。

## 回退策略
- **HMC失败**：尝试VI或降低网络复杂度。
- **过拟合**：增加正则化、减少网络容量或增加数据量。
- **欠拟合**：增加网络容量或调整损失函数权重。
- **物理约束违反**：增加物理损失权重或使用更强的PDE约束。

## 资源召回建议
- **召回时机**：当用户需要处理含噪PDE数据、进行参数反演或不确定性量化时。
- **配套资源**：
  - `cfd-pinn-training`：PINN训练通用流程。
  - `cfd-pde-solver`：PDE求解通用流程。
  - `cfd-uncertainty-quantification`：不确定性量化通用流程。

## 补充证据（开源文档/用户自有，可选）
无

## 证据来源
[1] Liu Yang, Xuhui Meng, George Em Karniadakis. B-PINNs: Bayesian physics-informed neural networks for forward and inverse PDE problems with noisy data. Journal of Computational Physics, 2020. DOI: 10.1016/j.jcp.2020.109913
[2] Kevin Linka, Amelie Schäfer, Xuhui Meng, Zongren Zou, George Em Karniadakis, Ellen Kuhl. Bayesian Physics Informed Neural Networks for real-world nonlinear dynamical systems. Computer Methods in Applied Mechanics and Engineering, 2022. DOI: 10.1016/j.cma.2022.115346
[3] Yibo Yang, Paris Perdikaris. Adversarial uncertainty quantification in physics-informed neural networks. Journal of Computational Physics, 2019. DOI: 10.1016/j.jcp.2019.05.027
[4] Mara Daniels, Liam Hodgkinson, Michael W. Mahoney. Uncertainty-Aware Diagnostics for Physics-Informed Machine Learning. arXiv:2510.26121, 2025.