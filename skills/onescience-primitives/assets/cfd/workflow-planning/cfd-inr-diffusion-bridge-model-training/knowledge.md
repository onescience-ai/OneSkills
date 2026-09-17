# 隐式神经表示与扩散桥模型训练

## 适用范围

**触发条件**：
- 已完成数据预处理与切分（Step 2），切分清单与归一化统计量已建立
- 需要训练隐式神经表示（INR）或扩散桥模型完成CFD流场补全
- 需要确保模型可复现、权重可重新加载

**适用场景**：
- 从坐标-物理量对学习连续场表示的INR训练
- 基于扩散过程的物理对齐场重构训练
- 物理增强的隐式表示训练（如PEINR）
- 超分辨率湍流场重建模型训练

**不适用场景**：
- 数据预处理未完成（需先执行预处理步骤）
- 仅需推理不需训练（跳至重构步骤）
- 模型架构未确定（需先完成模型选型）

## 输入

| 输入项 | 格式 | 必填 | 说明 |
|--------|------|------|------|
| {MODEL_NAME} | 字符串 | 是 | 模型实现或注册名 |
| {TRAIN_CONFIG} | JSON | 是 | 训练超参数与配置 |
| {INIT_CHECKPOINT} | 路径 | 否 | 可选预训练权重 |

## 输出

| 输出项 | 格式 | 说明 |
|--------|------|------|
| best_checkpoint.pt | PyTorch权重 | 通过训练门限的最佳权重 |
| train_config.json | JSON | 训练配置快照 |
| training_metrics.csv | CSV | 逐轮训练验证指标 |
| environment.txt | 文本 | 代码版本、依赖、随机种子 |

## 流程节点

### Step 3.1：环境与配置记录
- **操作**：记录代码版本、依赖包版本、随机种子、训练配置
- **参数**：{TRAIN_CONFIG}
- **质量门禁**：环境信息完整可追溯

### Step 3.2：模型初始化
- **操作**：按{MODEL_NAME}实例化模型，若提供{INIT_CHECKPOINT}则检查结构兼容性
- **参数**：{MODEL_NAME}, {INIT_CHECKPOINT}
- **质量门禁**：模型结构正确、预训练权重兼容

### Step 3.3：训练循环
- **操作**：加载s02切分数据与统计量，执行训练循环，记录逐轮指标
- **参数**：{TRAIN_CONFIG}中的epochs, batch_size, learning_rate, seed
- **质量门禁**：训练验证损失均为有限值

### Step 3.4：早停与最佳权重保存
- **操作**：监控验证集损失，早停触发时保存最佳权重
- **参数**：early_stopping_patience
- **质量门禁**：最佳权重可重新加载

### Step 3.5：训练记录生成
- **操作**：保存training_metrics.csv、train_config.json、environment.txt
- **参数**：训练日志
- **质量门禁**：记录完整、可复现

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认框架 | PyTorch | [场景需求书] | 可替换 |
| 默认训练轮数 | 100 epochs | [场景需求书] | 可按实际调整 |
| 默认批大小 | 8 | [场景需求书] | 可按显存调整 |
| 默认学习率 | 0.001 | [场景需求书] | 可按模型调整 |
| 默认随机种子 | 42 | [场景需求书] | 可复现性 |
| 默认早停耐心 | 15 epochs | [场景需求书] | 防止过拟合 |
| 模型类型 | INR + Diffusion Bridge | [场景需求书] | 双模型架构 |

## 边界与分流

- **训练发散**（损失NaN/Inf）：降低学习率 → 简化网络 → 检查数据 → 增加正则化
- **预训练权重不兼容**：结构不匹配时忽略预训练权重从头训练
- **过拟合**：验证损失上升 → 增加早停耐心 → 增加数据增强 → 简化模型
- **欠拟合**：验证损失不下降 → 增大模型容量 → 增加训练轮数
- **显存不足**：减小批大小或使用梯度累积

## 质量检查

- 训练损失曲线收敛
- 验证损失不低于训练损失过多（过拟合检测）
- 最佳权重文件可独立加载
- 随机种子一致时训练可复现
- 环境信息完整

## 回退策略

- 训练完全失败 → 检查数据质量、简化模型架构
- 部分收敛但质量不足 → 调整超参、增加物理约束
- 无法复现 → 检查随机种子设置、环境版本

## 资源召回建议

- 当CFD流场补全任务完成数据预处理后，需要训练模型时召回
- 前置步骤：cfd-cfd-data-preprocessing-splitting
- 后续步骤：cfd-sparse-field-reconstruction-inference

## 证据来源

[1] PEINR: A Physics-enhanced Implicit Neural Representation for High-Fidelity Flow Field Reconstruction, 2024
[2] Physics-aligned field reconstruction with diffusion bridge, 2024
[3] SCoReT: Super-Resolution Compression and Reconstruction of Turbulent Flows, arXiv:2607.03683, 2026
