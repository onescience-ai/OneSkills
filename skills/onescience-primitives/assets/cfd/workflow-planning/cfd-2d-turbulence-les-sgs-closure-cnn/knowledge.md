# 卷积网络二维湍流LES亚格子闭合工作流规划

## 适用范围
本卡片服务的工作流面向二维湍流大涡模拟（LES）中的亚格子闭合问题，使用卷积神经网络（CNN）从高保真DNS数据学习亚格子应力、通量或源项映射。适用于Kraichnan湍流、衰减湍流等二维湍流体系，可扩展至三维湍流闭合问题。核心目标是构建数据驱动的SGS模型，替代或增强传统涡粘性模型，同时保持数值稳定性和物理一致性。

## 输入
- **高保真数据源**：二维湍流DNS时间序列，包含速度场、涡度场等物理量
- **滤波操作**：对DNS数据施加空间滤波，生成粗网格场与亚格子应力/通量标签
- **模型选择**：全卷积神经网络（FCNN）或其他CNN变体，用于学习滤波后局部信息到亚格子闭合项的映射
- **数据契约**：定义输入/输出变量、单位、网格坐标及许可约束

## 输出
- **训练好的CNN SGS模型**：可嵌入LES求解器的神经网络权重
- **先验评估结果**：闭合项预测精度、物理约束满足度
- **后验评估结果**：嵌入求解器后的稳定性、能谱、统计剖面
- **适用域报告**：模型在不同Re、网格分辨率下的泛化能力边界

## 流程节点

### 数据接入与预处理
1. **数据读取与核验**：加载DNS数据，检查文件可读性、样本数、变量定义、坐标系、时间范围、缺失值
2. **滤波与标签生成**：对DNS数据施加空间滤波，计算亚格子应力/通量作为训练标签
3. **数据切分**：按几何、工况或时间构造无泄漏切分（train/validation/test），确保同一轨迹帧不跨集
4. **归一化/无量纲化**：统一跨工况量纲，保存统计量与可逆变换

### CNN模型训练
5. **模型配置**：选择CNN架构（如FCNN），配置超参数（学习率、批大小、早停策略等）
6. **训练执行**：加载切分数据训练模型，记录逐轮训练验证指标
7. **最佳权重保存**：保存验证损失最低的模型权重，确保可重新加载

### 先验与后验评估
8. **先验评估**：在独立DNS快照上评估闭合项预测精度，检查物理约束（如能量守恒）
9. **后验耦合**：将训练好的CNN嵌入LES求解器，执行时间推进模拟
10. **稳定性监控**：监控求解器发散、非物理解、能谱畸变等问题

### 适用域判定
11. **统计误差分析**：计算逐变量误差、边界误差、守恒残差
12. **最差样本追溯**：识别预测最差的样本，分析失败原因
13. **泛化能力测试**：测试不同Re、网格分辨率下的模型表现
14. **适用域报告**：输出PASS/REJECT/BLOCKED结论及复核建议

## 关键参数

### 通用判据
| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 训练集规模 | 需覆盖足够多的流动状态以捕获backscatter | [1] | 训练样本不足会导致backscatter预测不准，引发后验不稳定 |
| 滤波核类型 | 高斯滤波、盒式滤波等 | [2] | 滤波核选择影响亚格子应力的物理含义 |
| CNN感受野 | 应覆盖局部涡结构特征尺度 | [1] | 感受野太小无法捕获非局部相互作用 |
| 后验稳定性 | 时间推进无发散，能谱无畸变 | [1] | 关键质量门禁 |

### 校准数值（来自特定体系）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 2D衰减湍流Re范围 | Re=1000-16000 | [1] | 用于验证迁移学习能力 |
| 训练集大小影响 | 小样本导致backscatter精度下降 | [1] | 建议训练集足够大以保证后验稳定 |
| 迁移学习数据需求 | 1%新流场数据即可泛化 | [1] | 适用于Re变化不大的情况 |

## 边界与分流
- **训练集不足**：若训练样本过少，backscatter预测不准，后验易不稳定 → 需扩充训练集或引入物理约束
- **网格分辨率变化**：若目标流场网格分辨率与训练集差异大 → 需重新训练或使用迁移学习
- **Re跨度过大**：若目标Re远超训练范围（如>16倍） → 需迁移学习或使用多尺度模型
- **物理约束违反**：若闭合项违反能量守恒、正定性等 → 需引入惩罚项或调整损失函数

## 质量检查
- **数据完整性**：文件可读、样本可追溯、变量单位坐标定义完整
- **训练收敛**：训练验证损失均为有限值，无过拟合/欠拟合
- **权重可复现**：最佳权重可重新加载，随机种子可复现
- **物理一致性**：闭合张量/通量满足约束，后验求解无非物理解和发散
- **统计精度**：均值剖面与能谱经验证，误差在可接受范围内
- **适用域明确**：结论含适用域限制与复核建议，不凭平均误差宣称工程可用

## 回退策略
- **后验不稳定**：退化为传统涡粘性模型（如Smagorinsky）或混合CNN与物理模型
- **泛化能力不足**：使用迁移学习，仅用少量新流场数据微调
- **训练失败**：检查数据质量、调整超参数、更换网络架构
- **物理约束违反**：在损失函数中添加物理约束惩罚项

## 资源召回建议
- **场景启动**：当用户需要为二维湍流LES构建数据驱动闭合模型时召回本卡片
- **配套资源**：
  - `cfd-2d-turbulence-data-ingestion`：数据接入与预处理的详细步骤
  - `cfd-2d-turbulence-cnn-sgs-training`：CNN模型训练的具体配置与执行
  - `cfd-2d-turbulence-coupled-cfd-simulation`：后验CFD耦合的实现细节
  - `cfd-2d-turbulence-les-validation`：验证与适用域判定的方法

## 证据来源
[1] Guan Y, Chattopadhyay A, Subel A, et al. Stable a posteriori LES of 2D turbulence using convolutional neural networks: Backscattering analysis and generalization to higher Re via transfer learning. Journal of Computational Physics, 2022.
[2] Maulik R, San O, Rasheed A, Vedula P. Sub-grid modelling for two-dimensional turbulence using neural networks. Journal of Fluid Mechanics, 2018.
[3] Subel A, Chattopadhyay A, Guan Y, Hassanzadeh P. Data-driven subgrid-scale modeling of forced Burgers turbulence using deep learning with generalization to higher Reynolds numbers via transfer learning. Physics of Fluids, 2021.
[4] Maulik R, San O, Jacob JD, Crick C. Sub-grid scale model classification and blending through deep learning. Journal of Fluid Mechanics, 2019.
