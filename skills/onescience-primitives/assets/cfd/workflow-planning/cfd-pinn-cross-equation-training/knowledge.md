# 跨方程PINN训练

## 适用范围

面向PDE方程族，使用Meta-PINN、PINN agent或PINN Transformer在多个物理方程上训练统一模型。适用于需要在一个模型框架内同时处理多种PDE类型（如Navier-Stokes、Burgers、扩散、波动方程等）的场景。

**触发条件**：完成数据接入与预处理后，进入模型训练阶段。

## 输入

| 输入类型 | 变量 | 必填 | 说明 |
|---------|------|------|------|
| 模型名称 | `{MODEL_NAME}` | 是 | Meta-PINN/PINN agent/PINN Transformer |
| 训练配置 | `{TRAIN_CONFIG}` | 是 | 超参数和随机种子 |
| 训练集 | s02产物 | 是 | train_manifest.json |
| 验证集 | s02产物 | 是 | validation_manifest.json |
| 归一化参数 | s02产物 | 是 | normalization.json |
| 初始权重 | `{INIT_CHECKPOINT}` | 否 | 可选预训练权重 |

## 输出

| 输出产物 | 格式 | 说明 |
|---------|------|------|
| best_checkpoint.pt | PyTorch | 最佳模型权重 |
| train_config.json | JSON | 训练配置快照 |
| training_metrics.csv | CSV | 逐轮训练验证指标 |
| environment.txt | TXT | 代码版本、依赖、随机种子 |

## 流程节点

### 1. 训练配置解析

**操作**：
- 读取{TRAIN_CONFIG}，提取超参数
- 验证配置完整性（框架、轮数、批大小、学习率、种子、早停）
- 生成配置快照

**参数**：
- 框架：PyTorch（默认）
- 轮数：100（默认）
- 批大小：8（默认）
- 学习率：0.001（默认）
- 随机种子：42（默认）
- 早停耐心：15 epochs（默认）

**质量门禁**：配置完整，参数合理

---

### 2. 数据加载与预处理

**操作**：
- 加载s02切分的训练集和验证集
- 应用normalization.json中的归一化参数
- 构建数据加载器（DataLoader）

**参数**：
- 批大小：{TRAIN_CONFIG}.batch_size
- 打乱：仅训练集打乱
- 多进程加载：根据CPU核心数

**质量门禁**：数据加载无错误，归一化正确应用

---

### 3. 模型初始化

**操作**：
- 根据{MODEL_NAME}实例化模型
- 若提供{INIT_CHECKPOINT}，检查结构兼容性并加载
- 初始化优化器（Adam/AdamW等）

**模型类型**：
- **Meta-PINN**：元学习框架，学习跨方程的通用表示
- **PINN agent**：基于LLM的自动化PDE代理生成
- **PINN Transformer**：Transformer架构的PINN

**质量门禁**：模型初始化成功，参数可训练

---

### 4. 训练循环

**操作**：
- 逐epoch执行前向传播、损失计算、反向传播
- 计算PDE残差损失、边界损失、数据拟合损失
- 记录训练和验证指标
- 应用早停策略

**损失函数**：
- L_total = λ_PDE * L_PDE + λ_BC * L_BC + λ_data * L_data
- 权重λ可配置或自适应调整

**指标**：
- 训练损失、验证损失
- 相对L2误差
- PDE残差范数

**质量门禁**：损失为有限值，指标可追溯

---

### 5. 最佳权重保存

**操作**：
- 监控验证集指标
- 保存最佳权重（基于验证损失或指定指标）
- 保存训练配置和指标历史

**保存格式**：
- best_checkpoint.pt：PyTorch state_dict
- train_config.json：配置快照
- training_metrics.csv：逐轮指标

**质量门禁**：最佳权重可重新加载

---

### 6. 环境记录

**操作**：
- 记录代码版本（git commit）
- 记录依赖版本（requirements.txt或conda环境）
- 记录随机种子
- 记录硬件信息（GPU型号、显存）

**输出**：environment.txt

**质量门禁**：环境信息完整，可复现

## 关键参数

### 通用判据（方法层）

| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 配置完整性 | 框架/轮数/批大小/学习率/种子/早停均存在 | [场景需求书s03] | 训练前提 |
| 损失有限性 | 训练验证损失均为有限值 | [场景需求书s03] | 发散即终止 |
| 权重可加载 | checkpoint可重新加载 | [场景需求书s03] | 模型持久化 |
| 环境可复现 | 随机种子固定，依赖明确 | [场景需求书s03] | 复现性 |
| 初始权重兼容 | 若提供checkpoint，结构兼容 | [场景需求书s03] | 迁移学习 |

### 校准数值（PDEBench/PINNacle体系）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认框架 | PyTorch | [场景需求书s03] | 实现依赖 |
| 默认轮数 | 100 epochs | [场景需求书s03] | 可根据收敛调整 |
| 默认批大小 | 8 | [场景需求书s03] | 按显存调整 |
| 默认学习率 | 0.001 | [场景需求书s03] | 基准超参 |
| 默认随机种子 | 42 | [场景需求书s03] | 可复现性 |
| 默认早停耐心 | 15 epochs | [场景需求书s03] | 验证集不改善终止 |

## 边界与分流

| 前提条件 | 不成立时转向 |
|---------|-------------|
| 数据加载成功 | 检查数据格式、路径、归一化参数 |
| 模型初始化成功 | 检查模型定义、参数维度、设备 |
| 训练损失收敛 | 调整学习率、损失权重、网络结构 |
| 最佳权重可保存 | 检查磁盘空间、文件权限 |

## 质量检查

**检查清单**：
1. 配置完整性：所有必填超参数存在
2. 数据加载：训练集/验证集加载成功
3. 模型初始化：参数可训练，无错误
4. 训练循环：损失为有限值，指标可追溯
5. 最佳权重：可重新加载
6. 环境记录：版本、依赖、种子完整

## 回退策略

1. **训练发散**：降低学习率（0.0001）、增加早停耐心（30）、调整损失权重
2. **过拟合**：增加数据增强、正则化（L2、Dropout）、减少网络容量
3. **欠拟合**：增加网络宽度/深度、增加训练轮数、调整损失权重
4. **显存不足**：减小批大小、使用梯度累积、混合精度训练

## 资源召回建议

- 当需要训练跨方程PINN模型时召回本卡片
- 配套资源：Meta-PINN/PINN agent/PINN Transformer实现
- 关联卡片：cfd-pinn-benchmark-data-access（数据接入）、cfd-pinn-physics-residual-recovery（残差恢复）

## 证据来源

[1] PINNsAgent: Automated PDE Surrogation with Large Language Models, 2024
[2] DATS: Difficulty-Aware Task Sampler for Meta-Learning Physics-Informed Neural Networks, 2024
[3] Hypernetwork-based Meta-Learning for Low-Rank Physics-Informed Neural Networks, 2024
