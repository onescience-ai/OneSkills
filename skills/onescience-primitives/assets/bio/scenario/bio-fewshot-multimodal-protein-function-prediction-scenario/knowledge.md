# 低样本多模态蛋白功能预测场景

## 适用范围
- **触发条件**：用户需要在标注数据稀缺（few-shot）条件下预测蛋白质的Gene Ontology功能标签
- **适用场景**：CAFA挑战赛基准测试、新蛋白家族功能注释、跨物种功能迁移预测
- **不适用场景**：大规模标注数据场景（>1000样本/类）、单模态纯序列预测、蛋白质结构预测本身

## 输入
- 蛋白质氨基酸序列（UniProt格式）
- 可选：AlphaFold2预测的3D结构或pLDDT置信度分数
- 可选：蛋白质功能描述文本（PubMed摘要或Gene Ontology定义）
- 参考数据：UniProtKB功能注释、Gene Ontology本体文件

## 输出
- 多标签GO功能预测结果（BP/MF/CC三个命名空间）
- 预测置信度分数
- 分层评估指标（per-class F1、macro F1、AUPR）

## 流程节点
1. **数据准备** → 公开数据集获取与GO标签验证
2. **多模态表征** → ESM-2序列编码 + AlphaFold2结构特征 + 文本编码
3. **模型融合** → 多模态特征融合与分类器训练
4. **评估验证** → 分层性能评估、不确定度估计、跨家族泛化测试

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| max_seq_len | 1024 | [CAFA4] | 覆盖95%蛋白序列长度 |
| esm2_embedding_dim | 640/1280 | [Lin et al. 2023] | ESM-2 650M/3B模型输出维度 |
| pLDDT_threshold | 70 | [Jumper et al. 2021] | 结构置信度阈值 |
| batch_size | 32 | [CAFA4] | 标准训练批次 |
| macro_f1_threshold | 0.7 | [任务要求] | 验收硬性门槛 |

## 边界与分流
- 序列长度>1024：滑动窗口分块处理，取平均表征
- 无结构数据：仅使用序列+文本双模态
- 标注极度稀疏（<5样本/类）：启用元学习或度量学习策略
- 跨物种预测：使用序列相似性<30%的蛋白进行泛化测试

## 质量检查
- GO标签唯一性验证：每个GO ID功能描述唯一
- 序列字符合法性：仅包含ACDEFGHIKLMNPQRSTVWY
- 数据切分分层：各GO类别在train/val/test中比例一致
- 验收指标：macro_f1 > 0.7

## 回退策略
- 公开数据集不可用：使用UniProtKB REST API动态获取
- ESM-2加载失败：降级为ProtTrans或one-hot编码
- 分层评估不达标：增加数据增强或调整阈值

## 资源召回建议
- 数据集：`edge:resource:bio/datasets/bio-cafa-dataset`、`edge:resource:bio/datasets/bio-uniprotkb-reference`
- 模型：`edge:resource:bio/models/bio-esm2-protein-language-model`、`edge:resource:bio/models/bio-alphafold2-structure-features`
- 组件：`edge:resource:bio/components/bio-go-ontology-validator`

## 证据来源
[1] Ramola et al., "On the state of protein function prediction: a report on the fourth CAFA challenge", bioRxiv, 2024, DOI: 10.64898/2026.05.06.722942
[2] Chen et al., "Evaluating the advancements in protein language models for encoding strategies in protein function prediction", Frontiers in Bioengineering and Biotechnology, 2025, DOI: 10.3389/fbioe.2025.1506508
[3] Zhao et al., "PANDA-3D: protein function prediction based on AlphaFold models", NAR Genomics and Bioinformatics, 2024, DOI: 10.1093/nargab/lqae094