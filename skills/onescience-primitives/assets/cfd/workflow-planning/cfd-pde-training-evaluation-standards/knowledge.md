# PDE条件生成模型训练超参数标准与评估产物规范

## 适用范围

面向PDE条件生成模型（CVAE、扩散模型、Neural SDE等）的训练配置与评估产物生成。适用于多物理PDE场量预测任务中的模型训练超参数标准化管理、收敛性保障、评估指标计算和worst case追溯。不适用于非PDE任务或纯数据驱动模型。

## 输入

- 训练数据集（已切分的train/val/test集）
- 标准训练配置（epochs、early_stopping_patience、learning_rate等）
- 验收指标定义（distribution_distance、diversity、physics_residual、coverage）

## 输出

- 训练好的模型checkpoint（best_checkpoint.pt）
- 训练配置文件（train_config.json，含deviated_from_standard字段）
- 训练指标文件（training_metrics.json）
- 评估结果文件（evaluation.json）
- 最差样本文件（worst_cases.csv）
- 适用性报告（applicability_report.md）
- 结论文件（PASS_REJECT_BLOCKED.txt）

## 流程节点

### 1. 训练配置标准化
- **操作**：按标准配置设定训练超参数，偏离时记录原因
- **参数**：standard_epochs=100, standard_patience=15, standard_lr=1e-3
- **工具**：JSON配置文件
- **质量门禁**：train_config.json包含所有标准参数和deviated_from_standard字段

### 2. 训练执行与监控
- **操作**：执行训练并监控验证损失，使用early stopping
- **参数**：monitor=val_loss, mode=min, restore_best_weights=True
- **工具**：PyTorch training loop
- **质量门禁**：训练loss和验证loss均收敛（不再显著下降）

### 3. CPU环境训练规模估算
- **操作**：根据单epoch时间估算合理训练规模
- **参数**：max_total_time=24h, single_epoch_time=测量值
- **工具**：时间估算公式：max_epochs = max_total_time / single_epoch_time × 0.8
- **质量门禁**：总训练时间在预算范围内

### 4. worst_cases.csv 生成
- **操作**：从生成样本中按验收指标提取表现最差的样本
- **参数**：top_n=10, sort_by=physics_residual（降序）
- **工具**：NumPy argsort + pandas to_csv
- **质量门禁**：worst_cases.csv至少包含1条记录；字段完整

### 5. 评估产物完整性检查
- **操作**：检查所有必需评估产物是否存在且非空
- **参数**：required_files=[evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt]
- **工具**：文件存在性检查 + JSON解析
- **质量门禁**：所有文件存在、JSON可解析、worst_cases非空数组

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 标准epochs | 100 | 标准规范 | 最大训练轮次，确保模型充分收敛 |
| 标准early_stopping_patience | 15 | 标准规范 | 验证损失不改善的容忍轮次 |
| CPU环境训练规模缩减 | 可适当缩减但需记录 | [论文1] | 单epoch时间较长时可减少epochs，必须记录偏离原因 |
| Adam最优迭代次数 | 20,000次 | [论文1] | PINN类模型的经验值 |
| L-BFGS最优迭代次数 | 3,000次 | [论文1] | 二阶优化器的精调迭代 |
| 网络深度 | 6层 | [论文1] | PINN类模型的经验最优深度 |
| 网络宽度 | 50神经元/层 | [论文1] | 平衡容量与计算效率 |
| 激活函数 | Tanh | [论文1] | 在PINN中优于Sigmoid |

### 校准数值（worst_cases.csv规范）

| 字段 | 类型 | 说明 |
|------|------|------|
| sample_idx | int | 样本在测试集中的索引 |
| condition | str/array | 条件信息（初始条件/边界条件标识） |
| distribution_distance | float | 生成分布与真实分布的距离（KL散度/Wasserstein距离） |
| diversity | float | 生成样本的多样性指标 |
| physics_residual | float | 物理约束残差（PDE方程不满足程度） |
| coverage | float | 覆盖率（生成样本覆盖目标分布的程度） |

### worst_cases排序规则

- 主排序：physics_residual 降序（物理一致性最差的排在前面）
- 次排序：distribution_distance 降序（分布匹配最差的排在前面）
- 输出：top-N（默认N=10）最差样本

## 边界与分流

- **训练轮次不足**（实际epochs << 标准epochs）：检查是否因early stopping触发或环境限制导致提前终止，在train_config.json中记录实际轮次和原因
- **CPU环境单epoch时间过长**（>1小时）：适当缩减epochs至50-80，但必须在deviated_from_standard字段中说明
- **worst_cases.csv为空**：检查evaluation.json中是否有有效的样本级指标；若指标未按样本计算，需先执行样本级评估
- **评估产物不完整**：逐项检查缺失文件，优先生成worst_cases.csv（影响可追溯性）

## 质量检查

- [ ] train_config.json中epochs和patience参数与标准一致或有偏离说明
- [ ] training_metrics.json记录了完整的训练曲线（每epoch的loss值）
- [ ] evaluation.json中worst_cases非空数组（至少1条记录）
- [ ] worst_cases.csv文件存在且包含至少1行数据
- [ ] worst_cases.csv字段完整（sample_idx, condition, metrics...）
- [ ] PASS_REJECT_BLOCKED.txt与evaluation.json结论一致

## 回退策略

- 若CPU环境训练时间严重不足，可使用预训练权重进行fine-tuning而非从头训练
- 若worst_cases.csv生成失败，可从evaluation.json的worst_cases数组手动提取
- 若评估产物生成流程中断，可从最后完成的步骤恢复

## 资源召回建议

- 本卡片适用于PDE条件生成模型的训练和评估阶段
- 配套资源：cfd-conditional-generative-pde-data-pipeline（数据准备流程）
- 配套资源：cfd-physics-constraint-threshold-calibration（物理约束阈值校准）

## 证据来源

[1] Ahmad A, et al. "WHC-PINN: Physics-Informed Neural Network with weighted loss and hard constraint for compressible flow", Scientific Reports, 2026, DOI: 10.1038/s41598-025-34263-1

[2] Glyn-Davies A, et al. "A primer on variational inference for physics-informed deep generative models", Phil. Trans. R. Soc. A, 2025, DOI: 10.1098/rsta.2024.0324
