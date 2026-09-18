# PDE算子学习无泄漏数据切分策略

## 适用范围

适用于PDE算子学习任务中训练/验证/测试集的无泄漏切分。提供Darcy流（静态问题）和Navier-Stokes（时序问题）两种场景的切分策略模板。确保不同集合的输入参数空间无重叠，防止数据泄漏导致的性能高估。

## 输入

- **原始数据集**：已完成数据接入与契约核验的HDF5数据
- **切分配置**：训练/验证/测试集比例（默认0.7/0.15/0.15）
- **切分维度**：按样本ID（静态）或按时间轨迹（时序）

## 输出

- **切分清单**：train_manifest.json、validation_manifest.json、test_manifest.json
- **统计信息**：各集合样本数、参数范围、切分依据
- **无量纲化统计量**：仅从训练集计算的均值和标准差（normalization.json）

## 流程节点

### 1. 切分策略选择

**Darcy流（静态问题）**：
- 切分维度：按样本ID（geometry_id）
- 原则：不同几何域的样本不跨集
- 实现：每个样本对应一个独立的渗透率场-压力场对

**Navier-Stokes（时序问题）**：
- 切分维度：按时间轨迹（trajectory_id）
- 原则：同一模拟的不同时间步不跨集
- 实现：每个轨迹包含完整的初始条件→时间演化序列

### 2. 切分执行

**Darcy流切分模板**：
```python
# 按样本ID切分
sample_ids = list(range(n_samples))
random.shuffle(sample_ids)
n_train = int(0.7 * n_samples)
n_val = int(0.15 * n_samples)
train_ids = sample_ids[:n_train]
val_ids = sample_ids[n_train:n_train+n_val]
test_ids = sample_ids[n_train+n_val:]
# 验证：各集合ID无交集
assert len(set(train_ids) & set(val_ids)) == 0
assert len(set(train_ids) & set(test_ids)) == 0
assert len(set(val_ids) & set(test_ids)) == 0
```

**Navier-Stokes切分模板**：
```python
# 按时间轨迹切分
trajectories = group_by_trajectory(data)  # 按模拟实例分组
traj_ids = list(trajectories.keys())
random.shuffle(traj_ids)
n_train = int(0.7 * len(traj_ids))
n_val = int(0.15 * len(traj_ids))
train_trajs = traj_ids[:n_train]
val_trajs = traj_ids[n_train:n_train+n_val]
test_trajs = traj_ids[n_train+n_val:]
# 验证：各集合轨迹无交集
assert len(set(train_trajs) & set(val_trajs)) == 0
assert len(set(train_trajs) & set(test_trajs)) == 0
assert len(set(val_trajs) & set(test_trajs)) == 0
```

### 3. 无量纲化统计量计算

- **操作**：仅从训练集计算均值和标准差
- **公式**：$\mu = \frac{1}{N_{train}} \sum_{i=1}^{N_{train}} x_i$，$\sigma = \sqrt{\frac{1}{N_{train}} \sum_{i=1}^{N_{train}} (x_i - \mu)^2}$
- **应用**：对训练集、验证集、测试集统一使用训练集统计量进行归一化
- **质量门禁**：验证集和测试集的归一化必须使用训练集统计量，不得重新计算

### 4. 切分验证

- **操作**：检查各集合样本ID/轨迹ID无交集
- **参数**：切分后的manifest文件
- **质量门禁**：三份切分的对象互斥；仅用训练集计算变换统计量

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认切分比例 | 0.7/0.15/0.15 | [1][2] | 训练/验证/测试集比例 |
| 切分随机种子 | 固定值 | [1] | 确保可复现性 |
| 统计量计算范围 | 仅训练集 | [1] | 防止信息泄漏 |
| 切分验证 | 强制执行 | [1] | 确保无泄漏 |

### 校准数值（体系专属）

| 参数 | Darcy流 | Navier-Stokes | 来源 | 说明 |
|------|---------|---------------|------|------|
| 切分维度 | 按样本ID | 按轨迹ID | [1][2] | 静态vs时序 |
| 标准训练样本 | 1000 | 1000 | [1] | Li et al. 2020配置 |
| 标准验证样本 | 200 | 200 | [1] | 按比例推算 |
| 标准测试样本 | 200 | 200 | [1] | 按比例推算 |

## 边界与分流

**关键前提不成立时的改道方案**：
1. **样本数过少**：使用k-fold交叉验证替代固定切分
2. **数据高度相关**：按工况参数分层切分（stratified split）
3. **多分辨率数据**：按分辨率分组切分，确保各集合包含所有分辨率
4. **迁移学习场景**：源域和目标域数据需分开管理

## 质量检查

- 各集合样本ID/轨迹ID互斥（无交集）
- 无量纲化统计量仅从训练集计算
- 各集合的参数范围分布合理
- 切分比例与配置一致

## 回退策略

- 切分比例不合理：根据数据量调整比例
- 样本分布不均：使用分层切分（stratified split）
- 切分不可复现：固定随机种子并记录

## 资源召回建议

- 本卡片适用于PDE算子学习任务的预处理与数据切分步骤
- 配套卡片：`cfd-fno-darcy-ns-data-contract`（数据契约）
- 配套卡片：`cfd-fno-regular-grid-pde-operator-learning-workflow`（完整工作流）

## 证据来源

[1] Duruisseaux, V., Kossaifi, J., & Anandkumar, A. (2025). Fourier Neural Operators Explained: A Practical Perspective. arXiv:2512.01421.

[2] Li, Z., Kovachki, N., Azizzadenesheli, K., Liu, B., Bhattacharya, K., Stuart, A., & Anandkumar, A. (2020). Fourier Neural Operator for Parametric Partial Differential Equations. arXiv:2010.08895.
