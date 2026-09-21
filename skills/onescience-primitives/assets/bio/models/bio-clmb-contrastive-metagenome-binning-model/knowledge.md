# CLMB 对比学习宏基因组分箱模型

## 适用范围
本卡片描述CLMB（Contrastive Learning for Metagenomic Binning）模型的架构、接口和推理流程。适用于需要加载CLMB预训练权重并执行宏基因组分箱推理的任务。CLMB是COMEBin论文中提出的对比学习分箱方法的核心模型，使用多视图对比学习学习contig的低维嵌入表示。不适用于CLMB模型的训练（需参考训练流程文档），也不适用于其他对比学习分箱工具（如SemiBin2、VAMB）。

## 输入
- **k-mer特征**：每个contig的四核苷酸频率（TNF）向量，维度136（k=4，考虑反向互补）
- **覆盖度特征**：每个contig在各样本中的覆盖度均值和标准差，维度2M（M=样本数）
- **复合特征**：将TNF和覆盖度向量拼接，总维度136+2M
- **预训练权重**：CLMB模型的PyTorch权重文件（.pt格式，通常MB到GB级别）

## 输出
- **嵌入向量**：每个contig的低维嵌入表示（用于后续聚类分箱）
- **中间表示**：Coverage Network和Combine Network的中间层输出

## 模型架构

### 整体结构
CLMB模型由两个核心网络组成：
1. **Coverage Network**：处理覆盖度特征，学习样本特异性表示
2. **Combine Network**：融合k-mer特征和覆盖度特征，生成最终嵌入

### 网络细节
- **Coverage Network**：3层前馈网络，输入维度2M，输出维度128
- **Combine Network**：3层前馈网络，输入维度128+136（覆盖度嵌入+k-mer），输出维度128
- **激活函数**：ReLU
- **归一化**：L2归一化（用于对比学习）

### 推理流程
```
输入特征 (n_contigs × (136+2M))
    ↓
Coverage Network → 覆盖度嵌入 (n_contigs × 128)
    ↓
拼接 [覆盖度嵌入, k-mer特征] → (n_contigs × (128+136))
    ↓
Combine Network → 最终嵌入 (n_contigs × 128)
    ↓
L2归一化 → 归一化嵌入 (n_contigs × 128)
```

## 权重加载

### 官方发布渠道
- **GitHub**：https://github.com/CAMI-challenge/COMEBin（推荐，包含完整代码和预训练权重）
- **Zenodo**：论文补充材料中可能提供
- **注意**：CLMB权重文件应为PyTorch格式（.pt），大小通常在MB到GB级别；如文件仅几百字节，可能是模拟/占位文件

### 加载方法
```python
import torch

# 加载预训练权重
model = CLMBModel(...)  # 初始化模型架构
checkpoint = torch.load('clmb.pt', map_location='cpu')
model.load_state_dict(checkpoint)
model.eval()  # 设置为推理模式
```

### 权重验证
- 文件大小检查：真实权重通常>1MB
- 可加载性检查：`torch.load()`不报错
- 键名匹配检查：`model.load_state_dict()`不报missing keys

## 推理代码示例

```python
import torch
import numpy as np

def run_clmb_inference(tnf_matrix, coverage_matrix, model_path):
    """
    CLMB模型推理
    
    参数:
        tnf_matrix: numpy array, shape (n_contigs, 136), TNF特征
        coverage_matrix: numpy array, shape (n_contigs, 2M), 覆盖度特征
        model_path: str, CLMB预训练权重路径
    
    返回:
        embeddings: numpy array, shape (n_contigs, 128), 嵌入向量
    """
    # 1. 特征拼接
    features = np.concatenate([tnf_matrix, coverage_matrix], axis=1)
    features_tensor = torch.FloatTensor(features)
    
    # 2. 加载模型
    model = CLMBModel(input_dim=136 + coverage_matrix.shape[1], hidden_dim=128)
    checkpoint = torch.load(model_path, map_location='cpu')
    model.load_state_dict(checkpoint)
    model.eval()
    
    # 3. 推理
    with torch.no_grad():
        embeddings = model(features_tensor)
        # L2归一化
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
    
    return embeddings.numpy()
```

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| TNF维度 | 136 | [1] | k=4, 反向互补 |
| 覆盖度维度 | 2M | [1] | M=样本数 |
| 嵌入维度 | 128 | [1] | 最终输出维度 |
| 隐藏层维度 | 128 | [1] | 网络中间层 |
| 网络层数 | 3 | [1] | 前馈网络层数 |
| 激活函数 | ReLU | [1] | 标准选择 |
| 聚类算法 | 迭代medoid | [1] | CLMB专用 |
| 最小bin大小 | 200kbp | [1] | 过滤过小bin |

## 边界与分流
- **权重文件不可用时**：使用COMEBin仓库中的预训练权重；如无法获取，标记BLOCKED
- **GPU不可用时**：CLMB支持CPU推理，但速度较慢
- **输入维度不匹配时**：检查样本数M是否正确，确保覆盖度维度=2M
- **内存不足时**：分批处理contigs，或减少同时处理的contig数量
- **与其他工具集成时**：CLMB输出的嵌入可直接输入Leiden/medoid聚类算法

## 质量检查
- **权重文件验证**：文件大小>1MB，可正常`torch.load()`
- **推理输出验证**：嵌入维度=128，无NaN值，L2范数≈1
- **下游聚类验证**：嵌入质量通过t-SNE可视化和聚类纯度评估
- **端到端验证**：使用CAMI基准数据集验证分箱F1-score

## 回退策略
- **CLMB权重不可用**：使用COMEBin的预训练权重（功能等价）
- **模型架构不兼容**：检查PyTorch版本，必要时升级/降级
- **推理失败**：检查输入维度、数据类型（float32）、设备（CPU/GPU）
- **分箱质量差**：调整聚类参数，或使用集成方法

## 资源召回建议
- 当任务涉及CLMB模型推理或宏基因组分箱实现时召回本卡片
- 配套资源：`bio-metagenome-contrastive-learning-implementation`（对比学习实现）、`bio-metagenome-binning-evaluation-methodology`（评估方法）、`bio-metagenome-data-model-sources`（数据与模型获取）
- 相关卡片：`bio-contrastive-metagenome-binning-workflow`（工作流规划框架）

## 补充证据（开源文档/用户自有，可选）
[D1] COMEBin GitHub仓库, https://github.com/CAMI-challenge/COMEBin, CAMI-challenge GitHub Organization, accessed 2026-09-21（交叉验证：与论文[1]中的方法描述一致）

## 证据来源
[1] Wang Z, You R, Han H, Liu W, Sun F, Zhu S. Effective binning of metagenomic contigs using contrastive multi-view representation learning. Nature Communications, 2024, 15:585. DOI: 10.1038/s41467-023-44290-z
[2] Han H, Wang Z, Zhu S. Benchmarking metagenomic binning tools on real datasets across sequencing platforms and binning modes. Nature Communications, 2025, 16:2865. DOI: 10.1038/s41467-025-57957-6
