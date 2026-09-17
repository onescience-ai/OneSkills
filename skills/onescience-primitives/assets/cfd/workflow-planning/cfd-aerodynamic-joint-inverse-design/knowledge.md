# 生成模型气动外形与流场联合逆向设计

## 适用范围

**触发条件**：
- 需要从目标气动性能指标出发，同时生成满足性能要求的几何外形与对应流场分布
- 已有翼型或飞行器几何-流场-性能联合数据集，需要训练生成式逆向设计模型
- 需要在潜空间中探索多样化气动设计方案并评估物理一致性

**适用场景**：
- 翼型气动外形与流场联合逆向设计
- 飞行器气动布局的生成式探索
- 基于潜空间扩散模型的流场条件生成
- 多样化气动候选设计的批量生成与物理筛选

**不适用场景**：
- 仅优化几何外形而无需同时生成流场的场景（使用传统优化方法更合适）
- 无几何-流场联合数据的纯理论分析
- 需要实时在线推理的嵌入式部署场景（生成模型推理成本较高）
- 域外工况未经CFD复核直接工程应用

## 输入

- 翼型或飞行器几何-流场-性能联合数据集（含网格坐标、物理场变量、性能指标）
- 数据契约定义：输入字段、目标字段、单位、坐标系
- 切分配置：按几何对象或工况轨迹切分，防止训练-测试泄漏
- 训练配置：框架、超参数、随机种子、早停策略

## 输出

- 训练好的生成模型权重（best_checkpoint.pt）
- 多样化流场生成样本集（含采样轨迹、条件、随机种子）
- 物理一致性筛选结果（physics_filter.json）
- 分布覆盖评估（distribution_metrics.json）
- 任务验收报告（evaluation.json、applicability_report.md）
- 适用域判定（PASS/REJECT/BLOCKED）

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：接入翼型几何流场性能联合数据，核验样本、变量、单位、网格坐标及许可
- **参数**：DATASET_PATH（数据集路径）、DATASET_NAME（数据集名称）、DATA_CONTRACT（数据契约定义）
- **工具**：Python 数据读取库
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏

### Step 2：预处理与数据切分
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分
- **参数**：SPLIT_CONFIG（切分比例，默认70/15/15）、TARGET_FIELDS（目标变量）、NONDIMENSIONALIZE（是否无量纲化）
- **工具**：Python 数据处理库
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏

### Step 3：模型配置与训练
- **操作**：训练Latent diffusion model、Generative design model完成指定输入到目标物理量的映射
- **参数**：MODEL_NAME（模型名称）、TRAIN_CONFIG（超参数：epochs=100, batch_size=8, lr=0.001, seed=42, early_stopping_patience=15）、INIT_CHECKPOINT（可选预训练权重）
- **工具**：PyTorch 框架
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现

### Step 4：条件采样与物理一致性筛选
- **操作**：按工况生成多样流场样本并依据物理残差筛选
- **参数**：CHECKPOINT（模型权重）、DEVICE（计算设备）、BATCH_SIZE（推理批大小）
- **工具**：PyTorch 推理
- **质量门禁**：样本条件与随机种子可追溯；多样性和真实性同时评价；物理筛选前后统计均报告

### Step 5：任务验收与适用域判定
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益
- **参数**：METRICS（验收指标：distribution_distance, diversity, physics_residual, coverage）、MAX_RELATIVE_L2（相对误差门限，默认0.1）、RUN_OOD_TEST（是否外推测试）
- **工具**：评估脚本
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | train:0.7 / val:0.15 / test:0.15 | [1] | 防止数据泄漏的基本比例 |
| 切分单位 | 按几何对象或完整轨迹 | [1] | 不得把同一轨迹的帧随机打散 |
| 无量纲化 | 默认开启 | [1] | 统一跨工况量纲 |
| 早停耐心 | 15 epochs | [1] | 防止过拟合的默认值 |
| 物理筛选 | 边界、守恒与方程残差 | [1] | 多维度物理一致性检查 |
| 验收指标 | distribution_distance + diversity + physics_residual + coverage | [1] | 统计与物理指标同时评价 |
| 误差门限 | MAX_RELATIVE_L2 ≤ 0.1 | [1] | 测试集放行阈值 |
| OOD测试 | 默认开启 | [1] | 必须测试域外工况并明确适用域 |

### 校准数值（以下数值来自翼型几何流场联合数据集，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练轮数 | 100 epochs | [1] | 场景需求书默认值 |
| 批大小 | 8 | [1] | 按显存调整 |
| 学习率 | 0.001 | [1] | PyTorch 默认量级 |
| 随机种子 | 42 | [1] | 可复现性 |

## 边界与分流

- **几何数据不完整**（缺少网格坐标或拓扑信息）：转向降维参数化表征（如CST、PARSEC），或使用点云/隐式表征替代结构化网格
- **流场数据维度不匹配**（几何分辨率与场分辨率不一致）：先做空间插值或使用多分辨率编码，确保几何-流场配对关系正确
- **数据量不足以训练扩散模型**：改用条件GAN或VAE等轻量生成模型，或引入迁移学习/数据增强策略
- **物理残差筛选通过率过低**（<50%）：降低物理约束强度或使用软约束加权，同时排查数据质量问题
- **域外工况泛化失败**：明确标记适用域边界，域外工况必须经CFD复核后方可使用
- **训练不收敛**：检查学习率、批大小、数据预处理质量；必要时引入课程学习或渐进式训练策略

## 质量检查

- 数据文件可读且样本可追溯（s01门禁）
- 三份切分对象轨迹互斥，仅用训练集计算统计量（s02门禁）
- 训练验证损失均为有限值，最佳权重可重新加载（s03门禁）
- 生成样本条件与随机种子可追溯，多样性与真实性同时评价（s04门禁）
- 统计与物理指标同时报告，最差样本可追溯，结论含适用域限制（s05门禁）
- 禁止用单个漂亮样本代表整体性能（s04原则）
- 不得仅凭平均误差宣称工程可用（s05原则）

## 回退策略

- 模型训练失败：回退到传统优化方法（如遗传算法+CFD评估）进行气动外形设计
- 物理一致性筛选全部不通过：使用简化物理模型（如势流理论）做初筛，再用完整CFD复核
- 适用域判定为BLOCKED：停止自动设计流程，转为人工CFD复核模式
- 数据质量不足：退回数据采集阶段，补充高保真CFD模拟数据

## 资源召回建议

- 当需要从目标性能逆向生成气动外形与流场时召回本卡片
- 配套资源：cfd-aerodynamic-inverse-design-workflow（工作流级）、cfd-latent-diffusion-aerodynamic-training（训练方法）
- 若已有翼型跨工况场预测需求，可关联 cfd-airfoil-cross-condition-field-prediction-scenario
- 若涉及多保真数据融合，可关联 cfd-multifidelity-airfoil-optimization-workflow

## 证据来源

[1] 场景需求书 CFD_S094：生成模型气动外形与流场联合逆向设计，scenario_catalogs/fluid/CFD_S094_生成模型气动外形与流场联合逆向设计.json
[2] "Aerodynamic Shape Design Space Exploration with Deep Latent Diffusion Model", arXiv:2609.00812
[3] "Diffusion Model Driven Airfoil Design_ From Geometry Encoding to Practical Applications", arXiv:2601.16228
[4] "From Zero to Turbulence_ Generative Modeling for 3D Flow Simulation", Journal of Fluid Mechanics, DOI: 10.1017/jfm.2019.923
[5] "Text2PDE_ Latent Diffusion Models for Accessible Physics Simulation"
[6] "Multi-fidelity reduced-order surrogate modeling", arXiv:2309.00325
