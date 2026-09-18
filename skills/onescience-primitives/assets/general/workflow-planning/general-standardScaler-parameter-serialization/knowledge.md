# 机器学习预处理参数序列化标准方法

## 适用范围
适用于所有基于sklearn预处理的机器学习管道，需要保存和加载预处理器参数以确保训练和推理的一致性。不适用于非sklearn预处理器。

## 输入
- 训练数据集（用于拟合scaler）
- 预处理后的数据集
- 序列化格式（JSON、YAML、joblib）

## 输出
- normalization.json（包含mean和scale参数）
- 加载后的scaler对象
- 标准化和逆标准化函数

## 流程节点
1. **scaler拟合** → 在训练集上拟合预处理器（如StandardScaler）
2. **参数提取** → 提取预处理器参数（如mean和scale）
3. **参数序列化** → 将numpy数组转换为JSON/YAML格式
4. **参数保存** → 保存到normalization.json
5. **参数加载** → 从文件加载参数
6. **scaler恢复** → 恢复scaler对象用于新数据标准化

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 预处理器参数（如mean） | numpy数组 | [D1] | 各特征的均值 |
| 预处理器参数（如scale） | numpy数组 | [D1] | 各特征的标准差 |
| 序列化格式 | JSON | 用户自有 | 通用格式 |
| 数据类型 | float64 | [D1] | numpy默认精度 |

## 边界与分流
- 若需要完整scaler对象，可使用joblib.dump/load
- 若数据量极大，可考虑增量标准化（partial_fit）
- 若特征选择变化，需重新拟合scaler

## 质量检查
- 验证normalization.json中的均值和标准差与训练集实际统计量一致
- 检查加载后的scaler能否正确标准化新数据
- 验证逆标准化后的数据与原始数据误差<1e-10

## 回退策略
- 若JSON序列化失败，可使用pickle或joblib
- 若参数丢失，可重新从训练数据计算

## 资源召回建议
- 当任务涉及机器学习预处理参数持久化时召回本卡片
- 配套资源：cfd-leakage-free-split-strategy、cfd-drivaernet-dataset-access

## 证据来源
[D1] scikit-learn官方文档, Preprocessing data, https://scikit-learn.org/stable/modules/preprocessing.html（权威文档, 交叉验证）
[U1] 归因报告 CFD_S032 report.json 中的优化计划描述（用户自有, 经权威文档佐证）