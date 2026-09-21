# 基因组功能预测AUPRC评估

## 适用范围

**触发条件**：
- 需要评估DNA语言模型在基因组功能预测任务上的性能
- 需要区分AUPRC（PR曲线下面积）与多指标简单平均的本质区别
- 需要导出区间/碱基/变异层评估结果

**适用场景**：
- DNA序列变异效应预测（如SNP致病性分类）
- 基因组调控元件识别（如增强子活性预测）
- 3D基因组接触图预测
- 不平衡分类任务的性能评估

**不适用场景**：
- 回归任务（如连续值预测）
- 多分类任务（需使用宏/微平均AUPRC）
- 无需区分参考/替代等位基因的任务

## 输入

**输入要求**：
- 模型预测分数：每个样本/区间/变异的预测概率
- 真实标签：二值标签（0/1）
- 评估粒度：样本层/区间层/碱基层/变异层

**预处理要求**：
- 预测分数需为概率形式（0-1之间）
- 标签需为二值（0=负类，1=正类）
- 如需区分等位基因，需提供参考/替代等位基因标记

## 输出

**输出产物**：
- AUPRC分数：PR曲线下面积（0-1之间）
- 置置区间：AUPRC的95%置信区间
- 结果文件：区间级/变异级详细结果表

**验证标准**：
- AUPRC值应≥0.5（优于随机基线）
- 与论文报告的基线性能可比（如Caduceus AUPRC≥0.6）
- 结果文件格式符合VCF/BED/tabular规范

## 流程节点

### Step 1：预测分数收集
- **操作**：从模型获取每个样本的预测概率
- **参数**：输出层使用sigmoid激活
- **工具**：model.forward() + torch.sigmoid()
- **质量门禁**：预测分数在[0,1]范围内

### Step 2：真实标签准备
- **操作**：加载真实标签并与预测分数对齐
- **参数**：标签编码为0/1
- **工具**：pandas/numpy
- **质量门禁**：标签与预测一一对应

### Step 3：AUPRC计算
- **操作**：计算PR曲线下面积
- **参数**：使用sklearn.metrics.average_precision_score
- **工具**：scikit-learn
- **质量门禁**：AUPRC值在[0,1]范围内

### Step 4：置信区间估计
- **操作**：通过bootstrap估计AUPRC的置信区间
- **参数**：bootstrap次数≥1000
- **工具**：numpy/scipy
- **质量门禁**：置信区间宽度合理

### Step 5：结果导出
- **操作**：导出区间/变异级详细结果
- **参数**：格式=VCF/BED/tabular
- **工具**：pandas
- **质量门禁**：导出文件可解析

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 评估指标 | AUPRC (Average Precision) | [1] | PR曲线下面积 |
| 计算方法 | sklearn.metrics.average_precision_score | [2] | 标准实现 |
| 与随机基线比较 | AUPRC≥0.5为优于随机 | [1] | 基线参考 |
| 置信区间 | 95% CI, bootstrap≥1000 | [1] | 统计显著性 |
| 结果格式 | VCF/BED/tabular | [1] | 标准输出格式 |
| 等位基因区分 | 参考/替代等位基因分别评估 | [1] | 变异效应预测 |

## 边界与分流

**异常处理**：
- 预测分数超出[0,1]范围→使用sigmoid归一化
- 正负样本极度不平衡→使用分层抽样
- 计算失败→检查标签格式和预测形状

**降级策略**：
- AUPRC计算库不可用→手动实现PR曲线积分
- bootstrap计算慢→减少bootstrap次数或使用近似方法
- 结果文件格式不支持→使用通用tabular格式

**分支条件**：
- 任务为变异效应预测→区分参考/替代等位基因
- 任务为区间预测→使用BED格式导出
- 任务为变异预测→使用VCF格式导出

## 质量检查

**验证点**：
1. AUPRC值合理：0≤AUPRC≤1
2. 与基线可比：AUPRC≥0.5（优于随机）
3. 结果文件完整：包含所有样本/区间/变异
4. 格式合规：VCF/BED/tabular可解析

**阈值**：
- AUPRC值范围：[0, 1]
- 优于随机基线：AUPRC≥0.5
- 与论文基线可比：AUPRC≥0.6（Caduceus基准）

## 回退策略

**失败替代方案**：
- AUPRC计算完全不可用→使用ROC-AUC作为替代指标
- 结果导出失败→保存预测分数到CSV供后续处理
- 置信区间估计不可用→仅报告点估计值

## 资源召回建议

**何时召回**：
- 任务需要评估基因组功能预测性能
- 需要区分AUPRC与多指标平均的差异
- 需要导出标准格式的评估结果

**配套资源**：
- DNALONGBENCH：标准评估基准
- Caduceus模型：需要性能评估
- BEND：DNA语言模型基准评测

## 证据来源

[1] "BEND: Benchmarking DNA Language Models on biologically meaningful tasks", Marin et al., ICLR 2024, DOI: 10.48550/arXiv.2311.12570

[2] "Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling", Schiff et al., ICML 2024, DOI: 10.48550/arXiv.2403.03234

## 补充证据

[D1] "scikit-learn average_precision_score Documentation", scikit-learn, version 1.9.1, URL: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html（accessed 2026-09-21，标准计算方法参考）