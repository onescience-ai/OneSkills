# 预训练蛋白质语言模型集成

## 适用范围
- **触发条件**：需要加载ESM-2、AlphaFold2等预训练模型进行蛋白质表征提取
- **适用场景**：多模态蛋白功能预测、蛋白质表征学习、迁移学习
- **不适用场景**：仅需简单序列编码（one-hot）、蛋白质结构预测本身

## 输入
- 蛋白质氨基酸序列（ACDEFGHIKLMNPQRSTVWY字符集）
- 模型版本选择：ESM-2 650M/3B/15B
- 可选：AlphaFold2预测结构文件（PDB/cif格式）

## 输出
- 序列表征：ESM-2 embedding（640/1280维）
- 结构表征：AlphaFold2 pLDDT分数（0-100）或结构特征向量
- 融合表征：多模态特征拼接/注意力融合

## 流程节点

### 节点1：ESM-2模型加载
**操作**：下载并加载ESM-2预训练权重
**参数**：model_name（esm2_t33_650M_UR50D/esm2_t36_3B_UR50D）
**工具**：fair-esm（pip install fair-esm）
**质量门禁**：模型加载成功、权重版本正确

### 节点2：序列Tokenize
**操作**：将氨基酸序列转换为ESM-2输入token
**参数**：max_length=1024、padding/truncation策略
**工具**：esm.Alphabet.from_pretrained
**质量门禁**：token序列正确、长度匹配

### 节点3：序列表征提取
**操作**：前向传播获取ESM-2 embedding
**参数**：output_layer（倒数第2层）、pooling策略（mean/CLS）
**工具**：PyTorch
**质量门禁**：输出维度正确（640/1280）、无NaN

### 节点4：AlphaFold2结构特征提取
**操作**：从AlphaFold2预测结构提取pLDDT和几何特征
**参数**：pLDDT阈值（70）、特征维度
**工具**：BioPython、pandas
**质量门禁**：pLDDT分数在0-100范围、特征维度匹配

### 节点5：多模态特征融合
**操作**：拼接/注意力融合序列和结构表征
**参数**：融合策略（concat/attention）、输出维度
**工具**：PyTorch
**质量门禁**：融合后维度匹配分类器输入

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| esm2_model | esm2_t33_650M_UR50D | [Lin et al. 2023] | 650M参数模型 |
| embedding_dim | 640 (650M) / 1280 (3B) | [Lin et al. 2023] | 输出表征维度 |
| max_seq_len | 1024 | [CAFA4] | 输入序列长度上限 |
| pLDDT_threshold | 70 | [Jumper et al. 2021] | 结构置信度阈值 |
| pooling | mean | [Chen et al. 2025] | 序列表征池化策略 |

## 边界与分流
- ESM-2不可用：降级为ProtTrans或one-hot编码
- 无结构数据：仅使用序列表征
- GPU内存不足：使用ESM-2 650M或CPU推理
- 序列>1024：滑动窗口分块处理

## 质量检查
- ESM-2权重加载成功（检查model.load_state_dict）
- forward pass输出维度正确
- 表征无NaN/Inf值
- 与融合层输入维度匹配

## 回退策略
- ESM-2下载失败：使用HuggingFace镜像或本地缓存
- GPU不足：CPU推理（速度慢但可行）
- 维度不匹配：调整融合层输入维度

## 资源召回建议
- 模型：`edge:resource:bio/models/bio-esm2-protein-language-model`、`edge:resource:bio/models/bio-alphafold2-structure-features`

## 证据来源
[1] Lin et al., "Evolutionary-scale prediction of atomic-level protein structure with a language model", Science, 2023, DOI: 10.1126/science.ade2574
[2] Jumper et al., "Highly accurate protein structure prediction with AlphaFold", Nature, 2021, DOI: 10.1038/s41586-021-03819-2
[3] Chen et al., "Evaluating the advancements in protein language models for encoding strategies in protein function prediction", Frontiers in Bioengineering and Biotechnology, 2025, DOI: 10.3389/fbioe.2025.1506508