# CFD数据无泄漏切分策略

## 适用范围
适用于具有几何标识或轨迹标识的CFD数据集，需要按组切分以避免数据泄漏的场景。对于无分组标识的简单数据集，可退化为随机切分。

## 输入
- 带有分组标识（geometry_id, trajectory_id）的CFD数据集
- 切分比例（默认0.7/0.15/0.15）
- 随机种子

## 输出
- 三份切分文件：train.csv, validation.csv, test.csv
- 三份manifest文件：train_manifest.json, validation_manifest.json, test_manifest.json
- 标准化参数文件：normalization.json

## 流程节点
1. **分组识别** → 确定分组键（geometry_id或trajectory_id）
2. **分组切分** → 使用GroupShuffleSplit按组切分
3. **验证集划分** → 从训练集中划分验证集（同样按组）
4. **标准化拟合** → 仅在训练集上拟合StandardScaler
5. **数据变换** → 应用标准化到所有切分
6. **Manifest生成** → 记录样本ID、分组键、统计量

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | 0.7/0.15/0.15 | 用户自有 | 训练/验证/测试 |
| 分组键 | geometry_id | 用户自有 | 几何标识符 |
| 随机种子 | 42 | 用户自有 | 可重现性 |
| 标准化方法 | StandardScaler | 用户自有 | 零均值单位方差 |
| 验证集比例 | 0.15 | 用户自有 | 从训练集中划分 |

## 边界与分流
- 若数据集无分组标识，可使用随机切分但需记录风险
- 若数据集时间序列特性，需使用时间序列切分（按时间戳）
- 若数据集类别不平衡，需使用分层切分（StratifiedGroupShuffleSplit）

## 质量检查
- 验证各切分集的geometry_id是否无交集
- 检查normalization.json中的统计量与训练集实际统计量一致
- 验证三份manifest文件包含所有样本ID

## 回退策略
- 若分组切分导致某些组样本过少，可合并小样本组
- 若验证集不足，可使用K折交叉验证作为替代

## 资源召回建议
- 当任务涉及CFD数据预处理时召回本卡片
- 配套资源：cfd-drivaernet-dataset-access、general-standard-scaler-parameter-serialization

## 证据来源
[U1] 归因报告 CFD_S032 report.json 中的优化计划描述（用户自有, 未经公开源验证）
[U2] sklearn文档中的GroupShuffleSplit说明（权威文档, 交叉验证）