# Caduceus RC等变双向长程DNA语言模型

## 适用范围

**触发条件**：
- 需要使用RC等变双向DNA语言模型进行基因组功能预测
- 需要获取Caduceus预训练权重并加载到模型架构中
- 需要区分Caduceus-Ph（预训练）和Caduceus-Vi（变异效应预测）变体的适用场景

**适用场景**：
- DNA序列变异效应预测（如SNP功能注释、非编码变异分类）
- 基因组调控元件识别（如增强子、启动子活性预测）
- 长程基因组建模（如增强子-启动子远距离相互作用）
- DNA序列嵌入特征提取用于下游任务

**不适用场景**：
- 非DNA序列的蛋白质或RNA建模
- 短序列（<1kb）且无需双向上下文的简单分类任务
- 不支持RC等变约束的非基因组序列任务

## 输入

**输入数据格式**：
- DNA序列：单链或多链FASTA格式
- 序列长度：支持最长131,072 bp（Caduceus标准输入窗口）
- 编码方式：ACGT→{0,1,2,3}整数编码，或one-hot编码

**预处理要求**：
- 序列必须为正链方向（5'→3'）
- 序列长度需padding到模型输入长度（如8192或131072）
- 如需双向输入，需同时提供正向链和反向互补链

## 输出

**输出产物**：
- 序列嵌入：形状为[batch, seq_len, hidden_dim]的张量
- 变异效应分数：预测的致病性/功能影响分数
- 注意力权重（可选）：用于可解释性分析

**验证标准**：
- 加载checkpoint后模型参数量约1.7M（Caduceus-Ph）或3.2M（Caduceus-Vi）
- 预测结果应与论文报告的AUPRC≥0.6基准可比
- 正反链预测应满足RC等变性约束

## 流程节点

### Step 1：权重下载与验证
- **操作**：从GitHub releases或HuggingFace Hub下载caduceus.ckpt
- **参数**：版本=最新release，检查包含的key与模型架构匹配
- **工具**：wget/curl + torch.load()
- **质量门禁**：checkpoint加载无key mismatch错误

### Step 2：模型架构初始化
- **操作**：实例化Caduceus模型，配置MambaDNA层参数
- **参数**：d_model=256, n_layers=4, d_state=16, d_conv=4
- **工具**：PyTorch + mamba-ssm
- **质量门禁**：模型参数量与预期一致

### Step 3：权重加载
- **操作**：调用model.load_state_dict(checkpoint)
- **参数**：strict=True（严格匹配模式）
- **工具**：torch.nn.Module.load_state_dict()
- **质量门禁**：无missing/unexpected keys

### Step 4：推理执行
- **操作**：输入DNA序列，获取嵌入或预测
- **参数**：batch_size=1, seq_len≤131072
- **工具**：model.forward()
- **质量门禁**：输出shape正确，无NaN/Inf

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型变体 | Caduceus-Ph, Caduceus-Vi | [1] | Ph=预训练，Vi=变异效应预测 |
| d_model | 256 | [1] | 隐藏层维度 |
| n_layers | 4 | [1] | MambaDNA层数 |
| d_state | 16 | [1] | SSM状态维度 |
| d_conv | 4 | [1] | 局部卷积宽度 |
| 最大序列长度 | 131,072 bp | [1] | 支持百万碱基对级别建模 |
| RC等变约束 | W_{m,n,i}=W_{-m,-n,-i} | [1] | 反向互补群作用下的权重对称 |
| checkpoint格式 | PyTorch state_dict | [1] | 包含model和optimizer状态 |

## 边界与分流

**异常处理**：
- 权重文件缺失：从GitHub releases页面检查最新版本
- CUDA不可用：Caduceus支持CPU推理，但速度显著降低
- 序列过长：自动分块处理，保持坐标连续性

**降级策略**：
- 如mamba-ssm不可用，可使用causal-conv1d作为降级选项，但丧失长程建模能力
- 如RC等变约束难以实现，可先使用标准双向Mamba作为过渡方案

**分支条件**：
- 任务为变异效应预测→使用Caduceus-Vi变体
- 任务为通用DNA嵌入→使用Caduceus-Ph变体
- 需要RC等变性→确保使用MambaDNA组件

## 质量检查

**验证点**：
1. checkpoint加载成功：`torch.load('caduceus.ckpt')`无异常
2. 参数匹配：`model.load_state_dict(checkpoint)`无key mismatch
3. 推理正确：输入随机序列，输出无NaN且shape正确
4. RC等变验证：`f(x_rc) ≈ flip(f(x))`（近似满足）

**阈值**：
- 加载成功率：100%
- 参数匹配率：100%
- 推理成功率：100%

## 回退策略

**失败替代方案**：
- 权重下载失败→联系论文作者或检查ModelZoo
- mamba-ssm安装失败→使用WSL2+conda环境或causal-conv1d降级
- CUDA内存不足→减小batch_size或seq_len

## 资源召回建议

**何时召回**：
- 任务涉及DNA序列建模且需要RC等变性
- 需要长程（>10kb）基因组建模能力
- 需要预训练的DNA语言模型权重

**配套资源**：
- mamba-ssm：选择性状态空间模型实现
- DNALONGBENCH：评估基准数据集
- MambaDNA：RC等变卷积层实现

## 证据来源

[1] "Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling", Schiff et al., ICML 2024, DOI: 10.48550/arXiv.2403.03234

## 补充证据

[D1] "Caduceus GitHub Repository", kuleshov-group, main branch, URL: https://github.com/kuleshov-group/caduceus（accessed 2026-09-21，官方代码仓库）