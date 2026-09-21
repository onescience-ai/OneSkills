# 无铅杂化钙钛矿稳定性验证数据

## 适用范围
适用于无铅杂化钙钛矿材料稳定性预测任务的验证阶段，需要独立实验或高保真计算数据进行验证的场景。

## 输入
- 验证数据来源：实验文献、DFT计算结果
- 验证标准：误差容忍度、验证指标
- 验证方法：对比分析、统计检验

## 输出
- 验证结果：PASS/PARTIAL/REJECT
- 误差分析：预测值与实验值对比
- 验证报告：来源可追溯性、数据质量

## 流程节点
1. 选择验证数据源 → 2. 获取独立数据 → 3. 对比分析 → 4. 误差计算 → 5. 验证结论

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 误差容忍度 | MAE < 0.1 eV | [1] | 形成能预测误差容忍度 |
| 验证指标 | R² > 0.8 | [1] | 模型解释方差比例 |
| 数据来源 | 实验文献 | [1] | 独立实验数据 |
| 数据来源 | DFT计算 | [2] | 高保真计算数据 |
| 验证集大小 | ≥5个候选 | [1] | 最小验证集规模 |

## 边界与分流
- 如果实验数据不可用，使用高保真DFT计算数据
- 如果DFT数据不可用，使用其他机器学习模型预测作为参考
- 如果验证数据不足，记录验证局限性

## 质量检查
- 验证数据来源的可追溯性
- 检查验证数据的独立性（非训练数据）
- 确认验证标准的合理性

## 回退策略
- 如果主要验证数据源不可用，尝试替代数据源
- 如果验证数据质量不足，降低验证标准并说明
- 如果验证失败，分析原因并改进建模方法

## 资源召回建议
- 当任务需要验证模型预测结果时召回本卡片
- 当任务涉及材料筛选的可靠性评估时召回本卡片
- 配套工具：pymatgen、ASE、DFT计算工具

## 证据来源
[1] Machine learning stability and band gap of lead-free halide double perovskite materials for perovskite solar cells, Zongmei Guo, Bin Lin, Solar Energy, 2021, DOI: 10.1016/j.solener.2021.09.030
[2] Efficiency and Stability Analysis of 2D/3D Perovskite Solar Cells Using Machine Learning, Beyza Yılmaz, Çağla Odabaşı, Ramazan Yıldırım, Energy Technology, 2022, DOI: 10.1002/ente.202100948