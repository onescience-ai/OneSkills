# 谱增强PINN高频多尺度PDE求解

## 适用范围

**触发条件**：
- PDE解包含高频振荡或多尺度结构，标准MLP-PINN因谱偏差无法捕获
- 需要维持因果一致性（时间推进中初始条件准确传递）
- 配点或网格覆盖宽频带物理量（如激波、界面、声波传播）

**适用场景**：
- 波方程在非均匀介质中的传播（地震波、声波、电磁波）
- 可压缩流体激波捕获（Ma > 1的超声速/高超声速流动）
- 非线性波动问题（Burgers方程、sine-Gordon方程）
- 多尺度湍流结构的时间演化

**不适用场景**：
- 纯椭圆型或抛物型方程（谱偏差问题不突出）
- 空间域极度复杂（需自定义非Fourier谱基）
- 刚性问题（Neural ODE积分可能不稳定）

## 输入

- 高频与多尺度PDE配点数据（空间坐标、时间、物理量）
- 数据契约：变量名、单位、坐标系定义
- 训练/验证/测试切分配置

## 输出

- 训练好的谱增强PINN模型（best_checkpoint.pt）
- 解场与残差场（solution_fields/、pde_residuals/）
- 评估报告（evaluation.json、applicability_report.md）
- 验收结论（PASS/REJECT/BLOCKED）

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：读取PDE配点数据，核验样本数、变量、单位、坐标系、网格拓扑、时间范围
- **参数**：DATASET_PATH、DATASET_NAME、DATA_CONTRACT
- **工具**：数据加载脚本、契约验证
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

### Step 2：预处理与数据切分
- **操作**：统一物理量表示，按几何/工况/时间构造无泄漏切分，归一化或无量纲化
- **参数**：SPLIT_CONFIG（train/val/test比例）、TARGET_FIELDS、NONDIMENSIONALIZE
- **工具**：数据切分脚本、归一化工具
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

### Step 3：模型配置与训练
- **操作**：配置Spectral PINN/SIREN模型，选择谱基类型与初始化策略，执行训练
- **参数**：MODEL_NAME（Spectral PINN/SIREN）、TRAIN_CONFIG（epochs、lr、batch_size）、INIT_CHECKPOINT
- **工具**：PyTorch、TorchDyn（Neural ODE）
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### Step 4：方程求解与物理残差恢复
- **操作**：加载最佳权重，在查询配点上恢复解场、导数、通量与方程残差
- **参数**：CHECKPOINT、DEVICE、BATCH_SIZE
- **工具**：自动微分、离散算子
- **质量门禁**：解场导数与残差均为有限值；边初值逐项满足门限；独立数值解或解析解可对照

### Step 5：任务验收与适用域判定
- **操作**：评估统计误差、物理约束、泛化能力、计算收益，判定PASS/REJECT/BLOCKED
- **参数**：METRICS（relative_L2、PDE_residual、boundary_error、conservation_error）、MAX_RELATIVE_L2、RUN_OOD_TEST
- **工具**：评估脚本、外推测试
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 谱基类型 | Fourier基（正弦/余弦） | [1] | 全局正交基，可解析表达微分算子 |
| 谱截断频率 | 201^d（d为空间维数） | [1] | 控制解的频率分辨率 |
| Neural ODE求解器 | 4阶Runge-Kutta | [1] | 时间积分精度与稳定性 |
| 初始化策略 | 线性化PDE + Fourier乘子 | [1] | 将NODE初始化为近似线性解 |
| 物理损失权重 | 动态自适应 | [3] | 积分控制器自适应调整physics weight |

### 校准数值（体系专属，以下数值来自特定体系，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 2D波方程相对L2误差 | 0.075（NeuSA）vs 0.115-1.072（baseline） | [1] | 非均匀介质波传播基准 |
| sine-Gordon相对L2误差 | 0.001（NeuSA）vs 0.020-0.681（baseline） | [1] | 非线性波动基准 |
| 2D Burgers相对L2误差 | 0.051（NeuSA）vs 0.073-1.053（baseline） | [1] | 激波捕获基准 |
| Mach数范围 | Ma=1至Ma=15 | [4] | 可压缩无粘流适用范围 |

## 边界与分流

- **空间域复杂**：Fourier基不适用时，需改用自定义谱基（如小波、切比雪夫多项式），或退回标准MLP-PINN
- **刚性问题**：Neural ODE积分不稳定时，可改用隐式求解器或降低谱截断频率
- **初始化无先验**：无法获得线性化近似时，退化为标准Fourier Feature PINN训练
- **高维问题**：维度诅咒导致谱基数量爆炸时，考虑降维或稀疏谱方法

## 质量检查

- 谱系数收敛性：相邻epoch谱系数变化率 < 阈值
- 物理残差：PDE残差逐点有限且满足门限
- 边界条件：Dirichlet/Neumann边界逐点满足
- 时间因果性：t=0处解精确匹配初始条件
- 外推能力：训练域外工况误差不急剧恶化

## 回退策略

- 谱增强PINN收敛失败 → 退回标准PINN + Fourier Feature层
- Neural ODE不稳定 → 改用MLP直接预测解场（非谱方法）
- 训练时间过长 → 降低谱截断频率或使用稀疏谱基

## 资源召回建议

- 当用户提及"谱偏差""高频PDE""多尺度PDE""spectral bias"时召回本卡
- 配套资源：cfd-spectral-pinn-multiscale-pde-workflow（工作流卡）、cfd-spectral-pinn-model-training（训练卡）
- 与 cfd-pinn-boundary-condition-enforcement、cfd-pinn-loss-weighting-strategies 互补

## 证据来源

[1] "Neuro-Spectral Architectures for Causal Physics-Informed Networks", Bizzi et al., NeurIPS 2025, DOI: 10.48550/arXiv.2509.04966
[2] "Simple initialization and parametrization of sinusoidal networks via their kernel bandwidth", Belbute-Peres & Kolter, arXiv 2022, DOI: 10.48550/arXiv.2211.14503
[3] "A Control Perspective on Training PINNs", Barreau & Shen, arXiv 2025, DOI: 10.48550/arXiv.2501.18582
[4] "Data-Free PINNs for Compressible Flows: Mitigating Spectral Bias and Gradient Pathologies via Mach-Guided Scaling and Hybrid Convolutions", Yano, arXiv 2026, DOI: 10.48550/arXiv.2603.01001
