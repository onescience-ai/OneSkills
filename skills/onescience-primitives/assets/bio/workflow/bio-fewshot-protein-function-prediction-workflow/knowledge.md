# 低样本多模态蛋白功能预测工作流

## 适用范围
- **触发条件**：执行few-shot蛋白质功能预测任务，需要完整数据-模型-评估流程
- **适用场景**：CAFA挑战赛、新蛋白功能注释、跨物种功能预测
- **不适用场景**：仅需单步骤知识（如仅获取数据或仅评估模型）

## 输入
- 任务配置：序列长度上限（1024）、批次大小（32）、随机种子（11）、验收阈值（macro_f1>0.7）
- 数据源：CAFA数据集路径或UniProtKB获取配置
- 模型配置：ESM-2模型版本、AlphaFold2特征提取开关

## 输出
- 训练好的多模态蛋白功能预测模型（权重文件：multimodal_protein.pt）
- 预测结果：predictions.csv
- 评估报告：分层F1、置信区间、适用域声明

## 流程节点

### 节点1：数据获取与验证
**操作**：从CAFA或UniProtKB获取蛋白序列和GO注释
**参数**：数据格式（CSV列：protein_id, sequence, structure_features, go_labels）
**工具**：UniProtKB REST API、CAFA-evaluator
**质量门禁**：GO标签唯一性、序列字符合法性、标签与Gene Ontology本体一致

### 节点2：GO标签验证与去重
**操作**：验证GO ID唯一性，去除冗余标签
**参数**：GO OBO文件或API端点
**工具**：Gene Ontology API、go-basic.obo
**质量门禁**：每个GO ID功能描述唯一、无重复映射

### 节点3：分层数据切分
**操作**：按GO类别分层抽样划分train/val/test
**参数**：训练60%/验证20%/测试20%
**工具**：sklearn.model_selection.train_test_split（stratify参数）
**质量门禁**：各GO类别在各子集中均有样本、无数据泄漏

### 节点4：多模态特征编码
**操作**：ESM-2序列编码 + AlphaFold2结构特征 + 文本编码
**参数**：max_seq_len=1024、esm2_embedding_dim=640/1280
**工具**：fair-esm、transformers
**质量门禁**：输出维度匹配融合层输入、无NaN值

### 节点5：模型训练
**操作**：多模态融合模型训练
**参数**：batch_size=32、seed=11、epochs=50、lr=1e-4
**工具**：PyTorch
**质量门禁**：训练损失收敛、权重文件保存为multimodal_protein.pt

### 节点6：分层性能评估
**操作**：per-class F1、macro/micro/weighted F1、AUPR、bootstrap置信区间
**参数**：threshold=0.5、n_bootstrap=1000
**工具**：sklearn.metrics、CAFA-evaluator
**质量门禁**：macro_f1 > 0.7、各GO类别F1明细、置信区间声明

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| max_seq_len | 1024 | [CAFA4] | 覆盖95%蛋白序列长度 |
| batch_size | 32 | [任务要求] | 标准训练批次 |
| seed | 11 | [任务要求] | 可复现性种子 |
| threshold | 0.5 | [任务要求] | 二分类判定阈值 |
| macro_f1_threshold | 0.7 | [任务要求] | 验收硬性门槛 |

## 边界与分流
- 无结构数据：跳过AlphaFold2特征提取，仅用序列+文本
- 标注极度稀少（<5样本/类）：启用元学习或度量学习
- 训练中断：从checkpoint恢复，周期性保存权重
- 评估不达标：增加数据增强、调整阈值、检查标签质量

## 质量检查
- 每个GO类别在train/val/test中至少1个样本
- 训练权重文件名为multimodal_protein.pt
- 所有随机种子可追溯（numpy、torch、Python）
- 完整分层评估报告（per-class F1、置信区间、适用域）

## 回退策略
- CAFA数据集不可用：使用UniProtKB REST API获取
- ESM-2加载失败：降级为ProtTrans或one-hot编码
- macro_f1 < 0.7：检查数据质量、调整模型架构、增加训练轮数

## 资源召回建议
- 数据集：`edge:resource:bio/datasets/bio-cafa-dataset`、`edge:resource:bio/datasets/bio-uniprotkb-reference`
- 模型：`edge:resource:bio/models/bio-esm2-protein-language-model`、`edge:resource:bio/models/bio-alphafold2-structure-features`
- 组件：`edge:resource:bio/components/bio-go-ontology-validator`

## 证据来源
[1] Piovesan et al., "CAFA-evaluator: a Python tool for benchmarking ontological classification methods", Bioinformatics Advances, 2024, DOI: 10.1093/bioadv/vbae043
[2] Lin et al., "Evolutionary-scale prediction of atomic-level protein structure with a language model", Science, 2023, DOI: 10.1126/science.ade2574
[3] Jumper et al., "Highly accurate protein structure prediction with AlphaFold", Nature, 2021, DOI: 10.1038/s41586-021-03819-2