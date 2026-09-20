# 二维湍流LES亚格子闭合数据质量与评估

## 适用范围
面向湍流大涡模拟（LES）数据生成任务，评估DNS模拟参数对亚格子闭合数据质量的影响。适用于卷积神经网络（CNN）等数据驱动模型训练数据生成场景，不适用于高雷诺数工业级湍流直接模拟。

## 输入
- DNS模拟参数：网格分辨率N、雷诺数Re、时间步长dt、总模拟时间T_total
- 滤波参数：滤波核类型（box/Gaussian）、滤波尺寸Δ
- 误差评估指标选择：relative L2、RMSE、MAE、相关系数

## 输出
- 满足充分发展湍流统计特性的DNS数据集
- 适用的误差评估指标及阈值
- 参数选择决策依据

## 流程节点
1. 参数选择 → 2. 数据生成 → 3. 质量验证 → 4. 误差评估

### 步骤1：DNS参数选择
- 操作：根据目标雷诺数选择网格分辨率
- 参数：N≥256，Re≥10000（充分发展2D湍流基本要求）
- 工具：CFL稳定性条件、Kolmogorov尺度估算
- 质量门禁：dx/η<2（η为Kolmogorov尺度）

### 步骤2：数据生成
- 操作：运行DNS模拟生成速度场快照
- 参数：save_interval=0.01，T_total=5.0
- 工具：伪谱法求解器
- 质量门禁：能谱符合-5/3幂律

### 步骤3：质量验证
- 操作：检查能谱、统计特性
- 参数：惯性子区能谱范围
- 工具：功率谱密度分析
- 质量门禁：惯性子区能谱截断频率符合预期

### 步骤4：误差评估
- 操作：选择适用评估指标
- 参数：目标值量级判断
- 工具：多指标交叉验证
- 质量门禁：当目标值L2范数<1e-4时，标注relative L2为不可靠

## 关键参数
### 通用判据
| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 网格分辨率N | ≥256（2D湍流） | [1][2] | 低于此值无法解析充分发展湍流的最小涡结构 |
| 雷诺数Re | ≥10000（2D湍流） | [1][2] | 低于此值惯性子区能谱截断导致SGS应力统计特性失真 |
| dx/η比值 | <2 | [3] | 确保Kolmogorov尺度解析 |
| 滤波尺寸Δ/η | 保守恒定 | [3] | 保持Δ/η比值恒定有助于泛化性 |

### 校准数值
以下数值来自2D湍流DNS研究，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| N=128, Re=5000 | 数据保真度不足 | [1] | 实际执行导致relative L2误差71326.40 |
| N=256, Re=10000 | 场景标准配置 | [1] | 充分发展2D湍流基本要求 |
| relative L2阈值 | 0.3 | [1] | 当目标值量级为1e-7时可能失真 |

## 边界与分流
- **前提1：N≥256且Re≥10000** → 不成立时：报告BLOCKED，说明所需HPC资源，不得自主降低参数
- **前提2：目标值L2范数>1e-4** → 不成立时：切换到RMSE/MAE/相关系数作为主评估指标
- **前提3：滤波尺寸Δ/η保守恒定** → 不成立时：训练数据需覆盖多尺度滤波

## 质量检查
- 检查dataset_manifest.json中N_dns和Re值与场景记录一致
- 验证能谱符合-5/3幂律
- 确认误差评估包含多指标及可靠性标注

## 回退策略
- 若本地算力不支持标准参数，报告BLOCKED并说明所需HPC资源
- 若relative L2失真，切换到绝对误差指标

## 资源召回建议
- 执行DNS数据生成前召回本卡片
- 选择误差评估指标时召回本卡片
- 训练数据质量验证时召回本卡片

## 证据来源
[1] Guan et al., "Stable a posteriori LES of 2D turbulence using convolutional neural networks", Journal of Computational Physics, 2022, DOI: 10.1016/j.jcp.2022.111090
[2] Pawar et al., "A priori analysis on deep learning of subgrid-scale parameterizations for Kraichnan turbulence", Theoretical and Computational Fluid Dynamics, 2020, DOI: 10.1007/s00162-019-00512-z
[3] Arumapperuma et al., "Extrapolation Performance of CNN-Based Combustion Models for LES", Flow Turbulence and Combustion, 2025, DOI: 10.1007/s10494-025-00643-w
[4] Guan et al., "Learning physics-constrained subgrid-scale closures in the small-data regime", Physica D Nonlinear Phenomena, 2022, DOI: 10.1016/j.physd.2022.133568