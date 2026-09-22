# 多孔材料验证方法

## 适用范围
本卡片服务于多孔材料模型预测结果的独立验证任务，涵盖实验吸附测试、高保真计算（如GCMC模拟）等验证手段，用于评估模型预测的准确性并与实验或高保真计算结果进行对比。

## 输入
- 模型预测结果：吸附等温线、选择性系数、扩散系数等
- 验证数据来源：实验数据或高保真计算数据
- 验证指标定义：MAE、RMSE、R²、相对误差等

## 输出
- 验证报告：模型预测与验证数据的对比结果
- 误差分析：预测误差的分布和来源分析
- 改进建议：基于验证结果的模型优化方向

## 流程节点

### 1. 验证数据获取
- **操作**：从公开数据库或文献中获取实验或高保真计算数据
- **参数**：数据类型（吸附等温线、选择性等）、材料类型、条件范围
- **工具**：数据库API、文献数据提取工具
- **质量门禁**：验证数据的可靠性和可追溯性

### 2. 验证指标计算
- **操作**：计算模型预测与验证数据之间的误差指标
- **参数**：MAE、RMSE、R²、相对误差、平均绝对百分比误差
- **工具**：scikit-learn、numpy
- **质量门禁**：指标计算正确性

### 3. 误差分析
- **操作**：分析预测误差的分布和来源
- **参数**：误差分布统计、异常值检测、条件依赖性分析
- **工具**：pandas、matplotlib
- **质量门禁**：误差来源识别

### 4. 报告生成
- **操作**：生成验证报告和改进建议
- **参数**：报告模板、可视化图表
- **工具**：Jupyter Notebook、LaTeX
- **质量门禁**：报告完整性和可读性

## 关键参数

### 通用判据（方法层）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| GCMC模拟温度 | 298-350 K | [1] | 常见吸附测试温度 |
| GCMC模拟压力 | 0-100 bar | [1] | 覆盖低压到高压范围 |
| 力场选择 | UFF/DREIDING | [1] | 常用分子力场 |
| 周期性边界条件 | 三维周期性 | [1] | 模拟无限周期体系 |
| 平衡步数 | 10,000-50,000 | [1] | 确保体系达到平衡 |
| 采样步数 | 50,000-200,000 | [1] | 确保统计精度 |

### 校准数值（多孔材料体系）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| MOF-5 CO2吸附 | 2.5-3.5 mmol/g (298K, 1bar) | [2] | 标准验证数据 |
| ZIF-8 CO2吸附 | 0.8-1.2 mmol/g (298K, 1bar) | [2] | 标准验证数据 |
| UiO-66 CO2吸附 | 1.5-2.0 mmol/g (298K, 1bar) | [2] | 标准验证数据 |
| 预测误差阈值 | MAE < 0.5 mmol/g | [1] | 模型可接受精度 |

## 边界与分流
- **缺少实验数据**：使用高保真计算（如DFT+GCMC）作为替代验证
- **模型预测偏差大**：检查训练数据质量、模型架构、力场选择
- **验证数据不可靠**：寻找多个独立数据源交叉验证

## 质量检查
- **数据可追溯性**：验证数据来源必须可追溯
- **误差合理性**：误差在领域可接受范围内
- **可重复性**：验证过程可重复执行

## 回退策略
- 若验证数据不可获取，可尝试：(1) 使用高保真计算生成验证数据；(2) 降低验证标准；(3) 报告验证局限性

## 资源召回建议
- 当任务涉及多孔材料模型验证时召回本卡片
- 配套资源：matchem-porous-materials-databases（验证数据获取）、matchem-porous-materials-foundation-model（待验证模型）

## 证据来源
[1] Grand canonical Monte Carlo (GCMC) study on adsorption performance of metal organic frameworks (MOFs) for carbon capture, Sustainable Materials and Technologies, 2022, DOI: 10.1016/j.susmat.2021.e00383
[2] High-efficiency prediction of water adsorption performance of porous adsorbents by lattice grand canonical Monte Carlo molecular simulation, RSC Applied Interfaces, 2025, DOI: 10.1039/d4lf00354c
[3] Microscopic adsorption of CO2 in metal organic frameworks (MOF-5, ZIF-8 and UiO-66) by grand canonical Monte Carlo simulation, Adsorption, 2025, DOI: 10.1007/s10450-025-00664-x