# 数据驱动RANS雷诺应力与涡黏闭合

## 适用范围

本卡适用于利用高保真DNS数据训练机器学习模型，为RANS湍流闭合模型提供数据驱动的雷诺应力张量或涡黏系数预测能力。典型应用场景包括：翼型/机翼绕流、管道/槽道湍流、分离流、剪切流等经典CFD验证案例。当可用数据为DNS与RANS配对训练集（即同一几何/工况下同时有DNS高保真解和RANS低阶解），且目标是提升RANS闭合精度或量化模型形式不确定性时，可启用本场景工作流。

## 核心问题

RANS方法依赖湍流闭合模型（涡黏模型或雷诺应力模型）来封闭Navier-Stokes方程。传统经验模型在复杂流动（强分离、曲率效应、可压缩性等）中精度有限。数据驱动方法利用DNS作为"真相"，通过机器学习建立从局部流动特征到闭合项的映射，有望突破传统模型的物理假设限制。

## 工作流概览

```
数据接入与契约核验 → 预处理与数据切分 → 模型配置与训练 → 闭合项预测与后验CFD耦合 → 任务验收与适用域判定
```

### 关键阶段说明

**阶段1：数据接入与契约核验**
- 输入：DNS与RANS配对湍流闭合数据集
- 输出：data_contract.json（变量、单位、坐标系定义）
- 质量门禁：数据文件可读、变量定义完整、无训练测试泄漏

**阶段2：预处理与数据切分**
- 按几何、工况或轨迹无泄漏切分
- 统一物理量表示，执行无量纲化或归一化
- 保存统计量与可逆变换参数

**阶段3：模型配置与训练**
- 支持模型：Tensor-basis neural network、Symbolic closure model
- 默认框架：PyTorch
- 质量门禁：训练验证损失有限、权重可加载、环境可复现

**阶段4：闭合项预测与后验CFD耦合**
- 先验评估：独立快照上的闭合项预测误差与可实现性
- 后验推进：嵌入RANS或LES求解器执行完整CFD计算
- 输出：残差、能谱、统计剖面、稳定性记录

**阶段5：任务验收与适用域判定**
- 验收指标：closure_RMSE、mean_profile_error、spectrum_error、stability_horizon
- 默认相对误差门限：0.1（10%）
- 必须执行几何或工况外推测试以明确适用域边界

## 关键约束

1. **物理可实现性**：预测的雷诺应力张量必须满足可实现性约束（正定性、迹约束等）
2. **守恒性**：闭合项嵌入求解器后必须保持流动守恒特性
3. **稳定性**：后验推进必须在合理时间范围内保持数值稳定
4. **适用域明确**：禁止仅凭平均误差宣称工程可用，必须提供域外测试结果与复核建议

## 资源召回建议

当以下条件满足时召回本卡：
- 拥有DNS与RANS配对训练数据
- 目标是训练数据驱动湍流闭合模型
- 需要完整的从数据到CFD验证的端到端工作流规划
- 需要量化模型形式不确定性或适用域边界

配套资源：
- cfd-data-driven-rans-closure-workflow（工作流级）
- cfd-data-ingestion-contract-validation（数据接入步骤）
- cfd-preprocessing-data-splitting（预处理步骤）
- cfd-model-config-training（模型训练步骤）
- cfd-closure-prediction-coupling（后验耦合步骤）
- cfd-acceptance-applicability（验收判定步骤）

## 证据来源

[1] Quantifying model form uncertainty in Reynolds-averaged turbulence models with Bayesian deep neural networks, arXiv:1807.02901, 2018
[2] Machine learning for RANS turbulence modeling of variable property flows, arXiv:2210.15384, 2022
[3] Deep Learning Methods for Reynolds-Averaged Navier–Stokes Simulations of Airfoil Flows, arXiv:1810.08217, 2018
[4] Perspectives on machine learning-augmented Reynolds-averaged and large eddy simulation models of turbulence, Phys. Rev. Fluids 6, 050504, 2022
[5] Physics-informed machine learning approach for augmenting turbulence models: A comprehensive framework, arXiv:1701.07102, 2017