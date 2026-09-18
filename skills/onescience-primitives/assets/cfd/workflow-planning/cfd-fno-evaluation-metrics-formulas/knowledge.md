# PDE算子学习模型多维度评估指标

## 适用范围

适用于PDE算子学习模型（如FNO）的多维度评估，提供统计误差、物理约束、泛化能力和计算收益的计算公式、验收门限标准、worst_cases可追溯实现方法和适用域报告的标准格式。

## 输入

- **预测场**：模型推理输出的物理场 $u_{pred} \in \mathbb{R}^{H \times W}$
- **真实场**：参考解或高保真模拟结果 $u_{true} \in \mathbb{R}^{H \times W}$
- **PDE残差**：预测场满足控制方程的程度
- **网格信息**：网格分辨率、物理域范围
- **边界条件**：边界区域的预测值与真实值

## 输出

- **评估结果**：evaluation.json（包含所有评估指标）
- **最差样本**：worst_cases.csv（记录最差样本ID和指标）
- **适用域报告**：applicability_report.md（说明模型在训练分布内/外的表现）
- **验收结论**：PASS_REJECT_BLOCKED.txt

## 流程节点

### 1. 统计误差评估

**相对L2误差**（主要指标）：
$$\text{Relative L2} = \frac{\|u_{pred} - u_{true}\|_2}{\|u_{true}\|_2} = \frac{\sqrt{\sum_{i,j} (u_{pred,i,j} - u_{true,i,j})^2}}{\sqrt{\sum_{i,j} u_{true,i,j}^2}}$$

**均方根误差（RMSE）**：
$$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i,j} (u_{pred,i,j} - u_{true,i,j})^2}$$

**最大绝对误差**：
$$\text{Max Error} = \max_{i,j} |u_{pred,i,j} - u_{true,i,j}|$$

**L1误差**：
$$\text{L1 Error} = \frac{1}{N} \sum_{i,j} |u_{pred,i,j} - u_{true,i,j}|$$

### 2. 物理约束评估

**守恒残差**（适用于守恒律PDE）：
- 连续性方程残差：$\text{Res}_{mass} = \|\nabla \cdot u_{pred}\|_2$
- 动量方程残差：$\text{Res}_{momentum} = \|u_t + (u \cdot \nabla)u + \nabla p - \nu \nabla^2 u\|_2$

**边界误差**：
$$\text{Boundary Error} = \frac{1}{N_{boundary}} \sum_{(i,j) \in \partial \Omega} |u_{pred,i,j} - u_{true,i,j}|$$

**PDE残差可视化**：
- 计算预测场在每个网格点满足控制方程的残差
- 绘制残差空间分布图
- 识别残差较大的区域

### 3. 泛化能力评估

**几何外推测试**：
- 在训练分布外的几何域上测试
- 记录不同几何参数下的误差变化

**工况外推测试**：
- 在训练分布外的工况参数上测试
- 记录不同工况参数下的误差变化

**分辨率泛化测试**：
- 在不同分辨率的网格上测试
- 验证分辨率不变性

### 4. 计算收益评估

**推理时间**：
- 记录单样本推理时间
- 记录批量推理的吞吐量

**内存占用**：
- 记录峰值GPU内存
- 记录模型参数量

**与数值求解器对比**：
- 计算加速比
- 记录精度-速度权衡

### 5. worst_cases可追溯

**实现方法**：
```python
# 计算每个样本的相对L2误差
errors = []
for i in range(n_test_samples):
    rel_l2 = np.linalg.norm(pred[i] - true[i]) / np.linalg.norm(true[i])
    errors.append({'sample_id': i, 'rel_l2': rel_l2})

# 按误差排序，取最差样本
worst_cases = sorted(errors, key=lambda x: x['rel_l2'], reverse=True)[:n_worst]
```

**输出格式**：
```csv
sample_id,rel_l2,rmse,max_error,pde_residual
0,0.085,0.012,0.045,0.003
1,0.072,0.010,0.038,0.002
...
```

### 6. 适用域报告

**报告结构**：
```markdown
# 适用域报告

## 训练分布内表现
- 测试集相对L2误差：mean=0.05, std=0.02
- 最差样本相对L2误差：0.12
- 物理约束满足度：守恒残差<0.01

## 训练分布外表现
- 几何外推：相对L2误差增加至0.15
- 工况外推：相对L2误差增加至0.20
- 分辨率泛化：256×256训练→128×128测试，误差稳定

## 适用域限制
- 几何范围：训练域[0,1]²内有效
- 工况范围：参数空间[0.1,10]内有效
- 分辨率范围：64×64至256×256

## 复核建议
- 工程应用前需在目标工况上验证
- 关键区域需CFD复核
```

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 主要评估指标 | 相对L2误差 | [1][2] | 标准评估指标 |
| 默认验收门限 | 相对L2 < 0.1 | [1][2] | 默认放行阈值 |
| worst_cases数量 | Top 5-10% | [1] | 可追溯最差样本 |
| 评估维度 | 统计+物理+泛化 | [1] | 多维度评估 |

### 校准数值（体系专属）

| 参数 | 默认值 | 来源 | 说明 |
|------|--------|------|------|
| 相对L2门限 | 0.1 | [1][2] | 默认阈值，其他体系需重新锚定 |
| 守恒残差门限 | 任务相关 | [1] | 需根据具体PDE设定 |
| 边界误差门限 | 任务相关 | [1] | 需根据边界条件精度要求设定 |
| 最差样本比例 | 5% | [1] | 用于worst_cases分析 |

## 边界与分流

**关键前提不成立时的改道方案**：
1. **相对L2超标**：返回REJECT，建议调整模型超参数或增加训练数据
2. **物理约束不满足**：返回REJECT，建议使用物理信息神经网络（PINO）
3. **泛化能力差**：返回REJECT，建议增加训练数据多样性
4. **计算成本过高**：返回REJECT，建议使用模型压缩（如TFNO）

## 质量检查

- 所有评估指标计算正确
- worst_cases可追溯最差样本ID
- 适用域报告包含训练内外表现对比
- 验收结论明确（PASS/REJECT/BLOCKED）

## 回退策略

- 评估指标计算错误：检查反归一化流程
- worst_cases分析不足：增加评估维度和样本数
- 适用域报告不完整：补充分布外测试

## 资源召回建议

- 本卡片适用于FNO算子学习任务的验收与适用域判定步骤
- 配套卡片：`cfd-fno-inference-denormalization`（推理后处理）
- 配套卡片：`cfd-fno-acceptance-applicability`（验收流程）

## 证据来源

[1] Duruisseaux, V., Kossaifi, J., & Anandkumar, A. (2025). Fourier Neural Operators Explained: A Practical Perspective. arXiv:2512.01421.

[2] Li, Z., Kovachki, N., Azizzadenesheli, K., Liu, B., Bhattacharya, K., Stuart, A., & Anandkumar, A. (2020). Fourier Neural Operator for Parametric Partial Differential Equations. arXiv:2010.08895.
