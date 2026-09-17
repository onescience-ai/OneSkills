# 气动弹性与非定常载荷降阶响应预测工作流

## 适用范围
本工作流面向非定常气动力与耦合响应时序，完成气动弹性与非定常载荷降阶响应预测。适用于需要快速预测非定常气动载荷的气动弹性分析场景，包括但不限于：翼型/机翼的颤振分析、阵风响应、机动载荷预测等。当需要从高保真CFD数据中学习低阶动力学模型以加速气动弹性仿真时，可采用本工作流。

不适用场景：稳态气动载荷预测（无需时序建模）、完全线性系统（可使用解析方法）、极高马赫数/高温气体效应（需特殊物理模型）。

## 输入
**必需输入**：
- 非定常气动力与耦合响应时序数据（{DATASET_PATH}）
- 数据集名称与来源描述（{DATASET_NAME}）
- 目标变量列表（{TARGET_FIELDS}）

**可选输入**：
- 数据契约定义（{DATA_CONTRACT}）
- 切分配置（{SPLIT_CONFIG}）
- 初始权重检查点（{INIT_CHECKPOINT}）

**输入数据格式**：
- 时间序列数据：包含时间步、工况参数（马赫数、攻角等）、气动力系数、结构响应等
- 网格数据：CFD网格坐标、拓扑信息（如适用）
- 单位：物理量单位需明确标注，建议使用国际单位制

## 输出
**必需输出**：
- 训练好的降阶模型检查点（best_checkpoint.pt）
- 评估报告（evaluation.json, applicability_report.md）
- 通过/拒绝判定（PASS_REJECT_BLOCKED.txt）

**可选输出**：
- 预测结果（predictions/）
- 训练过程指标（training_metrics.csv）
- 最差案例分析（worst_cases.csv）

**验证标准**：
- 统计误差：相对L2误差 ≤ 0.1（默认门限）
- 物理约束：守恒残差、边界误差在可接受范围内
- 泛化能力：外推测试通过

## 流程节点
1. **数据接入与契约核验** → 2. **预处理与数据切分** → 3. **模型配置与训练** → 4. **批量推理与物理恢复** → 5. **任务验收与适用域判定**

每步含：操作、参数、工具、质量门禁

## 关键参数
**通用判据**（方法层，同类体系可参考）：
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 相对L2误差门限 | 0.1 | 场景需求书 | 测试集放行阈值 |
| 训练验证比例 | 7:1.5:1.5 | 场景需求书 | 训练:验证:测试 |
| 早停耐心 | 15轮 | 场景需求书 | 防止过拟合 |
| 无量纲化 | 是 | 场景需求书 | 统一跨工况量纲 |

**校准数值**（体系专属值，以下数值来自相关研究，供量级校准；其他体系需以自身证据重新锚定）：
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| CNN-AE潜在空间维度 | 低维 | [2] | 用于湍流通道流降阶 |
| LSTM预测时间步 | 可调 | [2] | 影响长期预测稳定性 |
| 物理约束类型 | 不可压缩、能量守恒 | [4] | 用于湍流流体动力学 |
| Taylor展开阶数 | 二阶 | [7] | 足以描述三次结构非线性 |

## 边界与分流
- **数据质量不足**：若数据存在大量缺失值或噪声，需先进行数据清洗或降噪处理
- **模型不收敛**：检查学习率、批量大小，尝试不同的优化器或学习率调度策略
- **外推性能差**：若超出训练数据范围，需进行CFD复核或扩展训练数据
- **物理约束违反**：若预测违反守恒律或边界条件，需引入物理约束项或调整模型架构
- **计算资源不足**：对于大规模问题，可考虑使用更简单的模型或数据降维

## 质量检查
**验证点**：
1. 数据完整性：文件可读、样本可追溯、变量单位明确
2. 切分有效性：训练/验证/测试集互斥，无数据泄漏
3. 训练收敛性：损失函数收敛，最佳权重可重新加载
4. 推理正确性：预测无NaN/Inf，形状单位正确
5. 物理一致性：守恒残差、边界误差在可接受范围内
6. 泛化能力：外推测试通过，适用域明确

**阈值**：
- 相对L2误差 ≤ 0.1
- 守恒残差 ≤ 0.01（或根据具体问题调整）
- 边界误差 ≤ 0.05

**失败处理**：
- 数据问题：返回BLOCKED，列出缺项
- 训练失败：检查超参数，尝试不同配置
- 评估不通过：进行误差分析，确定是否需重新训练或调整模型

## 回退策略
- **数据不足**：使用数据增强技术或迁移学习
- **模型过于复杂**：简化模型架构，减少参数量
- **计算成本过高**：使用更高效的训练策略或近似方法
- **物理约束难以满足**：采用混合方法（数据驱动+物理模型）

## 资源召回建议
当遇到以下情况时召回本卡片：
- 需要建立非定常气动载荷的降阶模型
- 进行气动弹性分析需要快速载荷预测
- 从CFD数据中学习低阶动力学
- 需要评估降阶模型的适用域

配套资源：
- onescience-primitives中的CFD数据处理组件
- 神经网络训练框架（PyTorch等）
- 气动弹性分析工具

## 证据来源
[1] Stable Port-Hamiltonian Neural Networks, Roth et al., arXiv:2502.02480, 2025
[2] Convolutional neural network and long short-term memory based reduced order surrogate for minimal turbulent channel flow, Nakamura et al., Phys. Fluids 33, 025116, 2021
[3] A deep learning enabler for non-intrusive reduced order modeling of fluid flows, Pawar et al., arXiv:1907.04945, 2019
[4] Validation and parameterization of a novel physics-constrained neural dynamics model applied to turbulent fluid flow, Shankar et al., arXiv:2110.11528, 2021
[5] A Residual Learning Approach for Unsteady Aerodynamic Load Prediction, Sanghi & Cesnik, arXiv:2608.17894, 2026
[6] Neural-Network and Reduced-order Modeling Workflows for AI-Driven CFD, Eduku et al., arXiv:2608.26064, 2026
[7] Nonlinear Model Order Reduction for Coupled Aeroelastic-Flight Dynamic Systems, Tantaroudas & Karachalios, arXiv:2603.15296, 2026