# 蛋白质功能预测模型训练

## 适用范围
- **触发条件**：需要执行蛋白质功能预测模型的训练流程
- **适用场景**：few-shot多标签蛋白功能分类、多模态融合模型训练
- **不适用场景**：仅需推理、仅需数据准备

## 输入
- 多模态特征表征（ESM-2序列 + AlphaFold2结构）
- GO功能标签（多标签）
- 训练配置：batch_size、seed、lr、epochs

## 输出
- 训练好的模型权重（multimodal_protein.pt）
- 训练日志（loss曲线、指标变化）
- 分层数据切分记录

## 流程节点

### 节点1：分层数据切分
**操作**：按GO类别分层抽样划分train/val/test
**参数**：train:val:test = 60%:20%:20%
**工具**：sklearn.model_selection.train_test_split（stratify参数）
**质量门禁**：各GO类别在各子集中均有样本

### 节点2：随机种子固定
**操作**：设置所有随机源确保可复现性
**参数**：seed=11
**工具**：torch.manual_seed、np.random.seed、random.seed
**质量门禁**：所有随机源可追溯

### 节点3：模型初始化
**操作**：初始化多模态融合模型
**参数**：ESM-2 embedding_dim、分类器维度
**工具**：PyTorch
**质量门禁**：模型参数正确加载

### 节点4：训练循环
**操作**：执行训练循环，保存最佳checkpoint
**参数**：batch_size=32、lr=1e-4、epochs=50
**工具**：PyTorch DataLoader、Optimizer
**质量门禁**：训练损失收敛、权重保存为multimodal_protein.pt

### 节点5：异常处理与恢复
**操作**：处理训练异常，支持断点恢复
**参数**：checkpoint间隔、异常日志
**工具**：try/except、torch.save
**质量门禁**：异常被捕获、checkpoint可恢复

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| seed | 11 | [任务要求] | 可复现性种子 |
| batch_size | 32 | [任务要求] | 训练批次大小 |
| lr | 1e-4 | [经验] | 学习率 |
| epochs | 50 | [经验] | 训练轮数 |
| weight_name | multimodal_protein.pt | [任务要求] | 权重文件名 |
| stratify | True | [任务要求] | 分层抽样开关 |

## 边界与分流
- GPU内存不足：减小batch_size或使用梯度累积
- 训练不收敛：调整lr、增加epochs、检查数据质量
- 权重保存失败：使用atomic写入模式（先写临时文件再重命名）
- ndarray序列化错误：使用.tolist()转换

## 质量检查
- 分层切分：各GO类别在train/val/test中至少1个样本
- 权重文件名：multimodal_protein.pt（非best_model.pt）
- 随机种子：torch.manual_seed(11)已设置
- 异常处理：训练脚本包含try/except

## 回退策略
- 训练失败：从最近checkpoint恢复
- 权重文件缺失：重新训练并检查保存路径
- 可复现性失败：记录所有随机种子设置

## 资源召回建议
- 模型：`edge:resource:bio/models/bio-esm2-protein-language-model`
- 工作流：`edge:workflow:bio-fewshot-protein-function-prediction-workflow`

## 证据来源
[1] Genome Medicine, "Multi-label transcriptional classification of colorectal cancer reflects tumor cell population heterogeneity", 2023, DOI: 10.1186/s13073-023-01176-5
[2] Piovesan et al., "CAFA-evaluator: a Python tool for benchmarking ontological classification methods", Bioinformatics Advances, 2024, DOI: 10.1093/bioadv/vbae043