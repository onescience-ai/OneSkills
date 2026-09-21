# 图神经网络在晶体结构预测中的应用范式

## 适用范围
本任务卡适用于材料科学领域中使用图神经网络（GNN）进行晶体结构预测与优化的场景。触发条件：用户需要使用CGCNN、CHGNet、MACE-MP-0、SevenNet等GNN模型进行晶体性质预测、结构弛豫或候选筛选。不适用于纯DFT计算工作流或不涉及GNN的晶体结构预测任务。

## 输入
- **晶体结构文件**：CIF或POSCAR格式，包含原子坐标、晶格参数和元素信息
- **预训练模型权重**：从Materials Project、MACE等数据库下载的预训练权重文件
- **任务类型**：性质预测（形成能、带隙、弹性模量等）或结构弛豫（力预测+梯度优化）
- **工况参数**：压力、温度、电荷态等（如适用）

## 输出
- **性质预测结果**：预测值及其置信区间
- **弛豫后结构**：优化后的原子坐标和晶格参数
- **稳定性指标**：形成能、凸包距离、能量分解等
- **验证报告**：与DFT参考值的对比、误差分析

## 流程节点

### 节点1：模型选择与加载
1. 根据任务类型选择合适的预训练模型：
   - **性质预测**：CGCNN（形成能、带隙）、MODNet（多种性质）
   - **结构弛豫**：CHGNet、MACE-MP-0、SevenNet（通用势）
   - **高精度能量**：M3GNet、DeePMD（需微调）
2. 加载预训练权重：从Materials Project API或官方仓库下载
3. 验证模型兼容性：检查元素覆盖范围、输入格式要求

### 节点2：晶体图表示构建
1. 将晶体结构转换为图表示：
   - **节点特征**：原子序数、电负性、价电子数等
   - **边特征**：原子间距离、角度、对称性信息
   - **图级别特征**：晶格参数、空间群
2. 应用截断半径：通常4-6 Å，平衡精度与效率
3. 处理周期性边界条件

### 节点3：推理执行
1. **性质预测模式**：
   - 输入：晶体图
   - 输出：标量性质（能量、带隙等）
   - 适用：高通量筛选、候选排序
2. **结构弛豫模式**：
   - 输入：初始结构
   - 迭代：力预测 → 梯度下降 → 结构更新
   - 输出：弛豫后结构、能量轨迹
   - 收敛标准：力 < 0.01 eV/Å，应力 < 0.1 GPa

### 节点4：结果验证与集成
1. 与DFT参考值对比：计算MAE、R²等指标
2. 不确定性量化：使用集成模型或MC Dropout
3. 集成到工作流：
   - **s02候选筛选**：GNN预测 → 能量排序 → 去除高能候选
   - **s03稳定性计算**：GNN弛豫 → DFT精修 → 最终排序
   - **s04可合成性判断**：GNN预测形成能 → 凸包距离计算

## 关键参数

### 通用判据（方法层）
| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| 截断半径 | 4-6 Å | [1][2] | 平衡精度与计算效率 |
| 邻居数量 | 12-16 | [1] | 保持图连通性 |
| 力收敛阈值 | 0.01 eV/Å | [3] | 结构弛豫停止条件 |
| 能量收敛阈值 | 1e-5 eV/atom | [3] | 结构弛豫停止条件 |

### 校准数值（模型专属）
| 模型 | 训练数据 | 预测性质 | MAE | 来源 |
|------|----------|----------|-----|------|
| CGCNN | Materials Project | 形成能 | 0.039 eV/atom | [1] |
| CGCNN | Materials Project | 带隙 | 0.388 eV | [1] |
| CHGNet | Materials Project | 力 | 0.08 eV/Å | [2] |
| MACE-MO-0 | MPtrj | 能量/力 | 0.02/0.05 | [4] |

## 边界与分流
- **元素不在模型覆盖范围内**：降级到DFT计算或使用更通用的模型（如SevenNet）
- **需要高精度能量**：GNN预测作为初始筛选，DFT作为最终验证
- **需要电荷态信息**：使用CHGNet（支持电荷感知）而非CGCNN
- **需要大尺度模拟**：使用GNN势进行MD模拟而非单点预测

## 质量检查
- **收敛性检查**：力/能量是否达到收敛标准
- **结构合理性**：原子间距是否在合理范围（>0.5 Å）
- **能量一致性**：GNN预测能量与DFT参考值的偏差
- **可重复性**：相同输入是否产生相同输出（考虑随机种子）

## 回退策略
- **GNN失败**：降级到经典力场或DFT计算
- **预训练权重不可用**：使用在线推理API或重新训练
- **计算资源不足**：使用小批量处理或模型蒸馏

## 资源召回建议
- **召回时机**：当任务涉及GNN模型选择、晶体性质预测、结构弛豫时
- **配套资源**：
  - 场景卡：matchem-graph-neural-network-crystal-structure-prediction-and-scenario
  - 工作流卡：matchem-composition-structure-search-space-definition-candidate-workflow
  - 模型卡：cgcnn、chgnet、mace-mp-0
  - 工具卡：pymatgen、materials-project-api

## 证据来源
[1] CHGNet as a pretrained universal neural network potential for charge-informed atomistic modelling, Nature Machine Intelligence, 2023, DOI: 10.1038/s42256-023-00716-3
[2] Scaling deep learning for materials discovery, Nature, 2023, DOI: 10.1038/s41586-023-06735-9
[3] Perovskite synthesizability using graph neural networks, npj Computational Materials, 2022, DOI: 10.1038/s41524-022-00595-5
[4] Crystal structure prediction by combining graph network and optimization algorithm, Nature Communications, 2022, DOI: 10.1038/s41467-022-29241-4
