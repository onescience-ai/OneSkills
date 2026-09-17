# 二维湍流LES数据驱动亚格子闭合工作流

## 适用范围
本卡片描述从DNS数据到可用CNN SGS模型的完整工作流，覆盖数据接入、预处理、模型训练、后验耦合与验证评估五个阶段。适用于需要为二维湍流大涡模拟构建数据驱动闭合模型的任务，可扩展至三维湍流闭合问题。

## 输入
- **高保真DNS数据**：包含速度场、涡度场等物理量的时间序列
- **滤波参数**：滤波核类型、截止波数等
- **模型架构**：CNN类型（如FCNN）、超参数配置
- **求解器接口**：用于后验耦合的LES求解器

## 输出
- **训练好的CNN SGS模型**：可嵌入求解器的神经网络权重
- **评估报告**：先验精度、后验稳定性、物理一致性
- **适用域结论**：模型在不同工况下的泛化边界

## 流程节点

### 阶段1：数据接入与核验（s01）
**操作**：读取DNS数据，核验文件可读性、样本数、变量定义、单位、坐标系、时间范围、缺失值及使用许可
**参数**：数据集路径、数据集名称、数据契约
**工具**：Python数据加载库（如NumPy、xarray）
**质量门禁**：数据文件可读且样本可追溯；输入/目标变量单位坐标定义完整；不存在训练/测试泄漏
**产出**：dataset_manifest.json、data_contract.json、data_audit.md

### 阶段2：预处理与数据切分（s02）
**操作**：统一物理量表示，按几何、工况或时间构造无泄漏切分
**参数**：切分配置（train/val/test比例）、目标变量、无量纲化开关
**工具**：数据预处理库
**质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
**产出**：train_manifest.json、validation_manifest.json、test_manifest.json、normalization.json

### 阶段3：模型配置与训练（s03）
**操作**：加载切分数据，配置CNN架构，训练模型并保存最佳权重
**参数**：模型名称（CNN SGS model）、训练配置（框架、 epochs、batch_size、learning_rate、seed、early_stopping_patience）、可选初始权重
**工具**：深度学习框架（如PyTorch）
**质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
**产出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

### 阶段4：闭合项预测与后验CFD耦合（s04）
**操作**：加载模型权重预测闭合项，先在独立快照上做先验评估，再嵌入求解器执行后验推进
**参数**：模型权重、计算设备、推理批大小
**工具**：LES求解器、推理引擎
**质量门禁**：闭合张量或通量满足约束；后验求解无非物理解和发散；均值剖面与能谱均经验证
**产出**：apriori_closure/、aposteriori_fields/、solver_stability.csv

### 阶段5：任务验收与适用域判定（s05）
**操作**：评估统计误差、关键物理约束、泛化能力和计算收益，输出PASS/REJECT/BLOCKED结论
**参数**：验收指标（closure_RMSE、mean_profile_error、spectrum_error、stability_horizon）、相对误差门限、是否外推测试
**工具**：统计分析库
**质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
**产出**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt

## 关键参数

### 通用判据
| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 数据切分 | 按轨迹/工况切分，避免泄漏 | [1] | 随机切分会导致时空相关性泄漏 |
| 训练集规模 | 需足够大以捕获backscatter特征 | [1] | 小样本导致后验不稳定 |
| 后验稳定性 | 时间推进无发散 | [1] | 关键成功判据 |
| 适用域 | 需测试不同Re、网格分辨率 | [1] | 不可仅凭平均误差宣称可用 |

### 校准数值（来自特定体系）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 2D衰减湍流Re范围 | Re=1000-16000 | [1] | 用于验证迁移学习能力 |
| 迁移学习数据需求 | 1%新流场数据 | [1] | 适用于Re变化不大的情况 |

## 边界与分流
- **数据不可读或缺失**：返回BLOCKED，列出缺项
- **训练集不足**：需扩充数据或引入物理约束
- **后验不稳定**：退化为混合模型或传统涡粘性模型
- **泛化能力不足**：使用迁移学习或多尺度模型

## 质量检查
- 每阶段均有明确的质量门禁
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 回退策略
- 后验不稳定：退化为传统模型
- 泛化不足：迁移学习
- 训练失败：调整超参数或更换架构

## 资源召回建议
- **场景启动**：当用户需要完整执行二维湍流LES数据驱动闭合工作流时召回
- **配套资源**：各阶段的详细task卡片（数据接入、CNN训练、后验耦合、验证评估）

## 证据来源
[1] Guan Y, Chattopadhyay A, Subel A, et al. Stable a posteriori LES of 2D turbulence using convolutional neural networks: Backscattering analysis and generalization to higher Re via transfer learning. Journal of Computational Physics, 2022.
[2] Maulik R, San O, Rasheed A, Vedula P. Sub-grid modelling for two-dimensional turbulence using neural networks. Journal of Fluid Mechanics, 2018.
