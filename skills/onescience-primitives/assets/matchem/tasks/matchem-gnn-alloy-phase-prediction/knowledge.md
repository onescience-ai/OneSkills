# 图神经网络预测合金相稳定性与形成能

## 适用范围
当需要对合金体系（特别是金属间化合物）进行相稳定性预测或形成能回归时，使用图神经网络（GNN）方法替代传统随机森林等浅层模型。适用于多主元合金高通量筛选、B2相形成能力评估等任务。不适用于数据量极少（<100条）的场景——此时浅层模型可能更稳健。

## 输入
- 合金晶体结构数据（CIF/POSCAR格式或pymatgen Structure对象）
- 训练标签：formation_energy_per_atom、energy_above_hull、space_group等
- 可选物理约束：电中性、原子尺寸匹配规则等

## 输出
- 训练好的GNN模型（可保存为checkpoint）
- 预测结果：formation_energy、phase_stability分类
- 模型性能指标：MAE、R²、分类准确率

## 流程节点

### 1. 晶体图构建
- **节点表示**：每个原子为一个节点，特征包括元素种类（one-hot或嵌入向量）、原子半径、电负性、价电子数等 [1]
- **边表示**：原子间距离小于截断半径（通常5-6 Å）的原子对形成边，边特征包括距离、角度 [1]
- **图构建工具**：pymatgen的`CrystalGraph`或torch_geometric的`CrystalData`

### 2. GNN架构选择
| 架构 | 特点 | 适用场景 | 参考 |
|------|------|----------|------|
| CGCNN | 晶体图卷积，直接处理周期性结构 | 形成能回归、带隙预测 | [1][2] |
| MEGNet | 图注意力+全局状态信息 | 多属性联合预测 | [1] |
| ALIGNN | 线图表示键角信息 | 需要角度信息的性质 | [1] |
| SchNet | 连续滤波卷积，处理3D坐标 | 分子动力学性质 | [1] |

### 3. 训练流程
```python
# 以CGCNN为例（使用matgl框架）
from matgl.apps import FormEnergyPred
model = FormEnergyPred(preset="M3GNet-MP-2024")
# 或从头训练
from matgl.gl import M3GNet
model = M3GNet(is_intensive=False)
# 训练参数
train_args = {
    "learning_rate": 1e-3,
    "batch_size": 128,
    "epochs": 200,
    "patience": 20,  # early stopping
    "loss": "mse",  # 或自定义物理约束损失
}
```

### 4. 物理约束损失函数（可选）
- 形成能约束：对已知稳定相施加额外损失项
- 相稳定性约束：B2相对应特定空间群，可作分类辅助任务
- 实现方式：在MSE损失基础上加权物理正则项

### 5. 模型评估
- 回归指标：MAE < 0.05 eV/atom（形成能）、R² > 0.9
- 分类指标：相稳定性分类准确率 > 85%
- 泛化验证：留出体系交叉验证（leave-one-system-out）

## 关键参数

| 参数 | 推荐值 | 来源 | 说明 |
|------|--------|------|------|
| 截断半径 | 5.0 Å | [1] | 构建晶体图的原子对距离阈值 |
| 节点特征维度 | 92（元素one-hot）或64（嵌入） | [1] | 取决于表示方法 |
| 学习率 | 1e-3 | [2] | Adam优化器初始学习率 |
| 批量大小 | 128 | [2] | 受GPU显存限制 |
| 训练轮数 | 200（early stopping） | [2] | patience=20防止过拟合 |
| MAE目标 | < 0.05 eV/atom | [1] | 形成能预测精度基准 |

## 边界与分流
- 数据量 < 100 → 考虑使用迁移学习（预训练模型微调）或浅层模型
- 无GPU资源 → 使用CGCPU或降级为随机森林（但需标注模型选择偏离）
- PyTorch Geometric未安装 → 使用matgl（内置M3GNet/MEGNet）或DGL
- 需要可解释性 → 使用CGCNN + 注意力可视化，或降级为特征重要性分析

## 质量检查
- 训练集/验证集/测试集划分应按体系分组（避免同体系数据泄露）
- 检查预测值分布是否与训练集一致（域外检测）
- MAE应在测试集上稳定（多次随机种子运行方差 < 10%）

## 回退策略
- GNN训练失败 → 使用随机森林 + 手工特征（需在报告中明确标注模型偏离及影响）
- 数据不足 → 使用迁移学习：在大规模数据集（如Materials Project全量）上预训练，再在目标体系微调

## 资源召回建议
- 当任务涉及合金相预测、形成能回归、需要图结构表示时召回本卡
- 配套资源：matgl（M3GNet预训练模型）、pymatgen（结构处理）、torch_geometric（图操作）

## 证据来源
[1] Shi X. et al., "A review on the applications of graph neural networks in materials science at the atomic scale", Materials Genome Engineering Advances, 2024, DOI: 10.1002/mgea.50
[2] Liu J. et al., "Comparation of Graph Neural Networks and Traditional Machine Learning for Property Prediction in All-Inorganic Perovskite Materials", Inorganics, 2026, DOI: 10.3390/inorganics14020058
[3] Du Z. et al., "CTGNN: Crystal Transformer Graph Neural Network for Crystal Material Property Prediction", 2024
[4] Bhattacharjee S., "SR-CGCNN: Shared Recurrent Convolution in Crystal Graph Neural Networks for Materials Property Prediction", 2026
