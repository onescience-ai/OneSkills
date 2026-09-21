# CAME-AB Pretrained Weights for Antibody Binding Site Prediction

## 适用范围
CAME-AB is a multimodal deep learning model for antibody binding site prediction on antigens. Use pretrained weights when performing antibody-antigen binding site prediction tasks requiring high accuracy across multiple metrics (Precision, Recall, F1, AUC-ROC, MCC). The model is specifically designed for computational immunology and therapeutic antibody design applications.

## 输入
- **Antibody sequences**: Heavy and light chain amino acid sequences
- **Antigen sequences/structures**: Antigen amino acid sequences or 3D structures
- **Modality features**: Five biologically grounded modalities (amino acid encodings, BLOSUM profiles, language model embeddings, structure-aware features, GCN-refined graphs)

## 输出
- **Binding site predictions**: Per-residue binding probability scores on antigen
- **Confidence scores**: Model confidence for each prediction
- **Feature representations**: Learned multimodal embeddings

## 流程节点
1. **Data preprocessing** → Encode sequences and extract five modality features
2. **Adaptive modality fusion** → Dynamically weight each modality based on input-specific contribution
3. **Transformer encoding** → Process fused features through Transformer encoder
4. **MoE processing** → Apply Mixture-of-Experts for feature specialization
5. **Contrastive learning** → Shape latent space geometry for intra-class compactness
6. **Prediction head** → Generate binding site probability scores
7. **Post-processing** → Apply stochastic weight averaging for optimization stability

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| Modalities | 5 | [1] | Amino acid, BLOSUM, LM embeddings, structure, GCN |
| Architecture | Transformer + MoE | [1] | Cross-modal attention with mixture-of-experts |
| Loss | Supervised contrastive + classification | [1] | Intra-class compactness, inter-class separability |
| Weight averaging | Stochastic (SWA) | [1] | Optimization stability and generalization |
| Input features | 258D per residue | [1] | 256D sequence + 2D chain type |

## 边界与分流
- **Data requirements**: Requires both antibody and antigen sequences; single-chain prediction not supported
- **Computational cost**: GPU recommended for inference due to multimodal architecture
- **Preprocessing**: BLOSUM profiles and language model embeddings must be pre-computed
- **Structure features**: If antigen structure unavailable, sequence-only features can be used with reduced accuracy

## 质量检查
- Verify weight file integrity (SHA256 checksum from official source)
- Validate input format matches training data specifications
- Check that all five modality features are available and properly formatted
- Monitor prediction confidence scores for anomalous outputs

## 回退策略
- If CAME-AB weights unavailable, consider alternative models: Phys-AbGAT, MVSF-AB, or AbFlex
- For sequence-only inputs, use models that do not require structure features
- Fallback to simpler models if computational resources limited

## 资源召回建议
- When performing antibody-antigen binding site prediction
- When multimodal feature integration is required
- When comparing antibody binding specificities across antigens
- Pair with ANARCI for CDR region identification and SAbDab for training data

## 证据来源
[1] Li H, Ma J, Shi Z, et al. CAME-AB: Cross-Modality Attention with Mixture-of-Experts for Antibody Binding Site Prediction. arXiv:2509.06465. 2025.