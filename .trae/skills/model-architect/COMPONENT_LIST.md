# OneScience 组件名单

本组件名单基于 `/root/myapp/oneskills/component_knowledge/modules/` 目录下的所有组件文件整理而成，按照 markdown 文件中的 `name` 字段进行组织。

---

## 目录

1. [Attention (注意力机制)](#attention-注意力机制)
2. [Decoder (解码器)](#decoder-解码器)
3. [Diffusion (扩散模型)](#diffusion-扩散模型)
4. [Encoder (编码器)](#encoder-编码器)
5. [Embedding (嵌入层)](#embedding-嵌入层)
6. [Evolution (演化模型)](#evolution-演化模型)
7. [Fuser (特征融合器)](#fuser-特征融合器)
8. [Head (预测头)](#head-预测头)
9. [Layer (层组件)](#layer-层组件)
10. [Linear (线性层)](#linear-线性层)
11. [MLP (多层感知机)](#mlp-多层感知机)
12. [Node (节点更新)](#node-节点更新)
13. [PairFormer (配对形成器)](#pairformer-配对形成器)
14. [Pooling (池化)](#pooling-池化)
15. [Processor (处理器)](#processor-处理器)
16. [Recovery (恢复模块)](#recovery-恢复模块)
17. [Sample (采样模块)](#sample-采样模块)
18. [Transformer (Transformer模块)](#transformer-transformer模块)
19. [Utils (工具函数)](#utils-工具函数)
20. [其他组件](#其他组件)

---

## Attention (注意力机制)

| Name | Alias | Category |
|------|-------|----------|
| SelfAttention | Efficient Linear Self-Attention | attention_mechanism |
| ProtenixAttentionMechanisms | AlphaFold3 Pair-Biased Attention | attention_mechanism |
| PhysicsAttentionMechanisms | Physics Attention (Irregular & Structured) | attention_mechanism |
| NystromAttention | Nyström Low-Rank Attention | attention_mechanism |
| EarthDistributedAttention3D | Distributed 3D Earth Position Bias Window Attention | distributed_attention_mechanism |
| MultiHeadAttention | Standard Multi-Head Self-Attention | attention_mechanism |
| EarthAttention3D | 3D Earth Position Bias Window Attention | attention_mechanism |
| EarthAttention2D | 2D Earth Position Bias Window Attention | attention_mechanism |
| LinearAttentionMechanisms | Linear Attention (Vanilla & Generalized) | attention_mechanism |
| FlashAttention | Memory-Efficient Exact Attention | attention_mechanism |
| FactAttention | Factorized Attention (2D/3D) | attention_mechanism |
| FeatureUngroupingAttention | Global SIE Ungrouping Attention / Cross-Attention Broadcast | attention_mechanism |
| FeatureGroupingAttention | Global SIE Grouping Attention / Cross-Attention Pooling | attention_mechanism |
| WindowAttention | - | attention_mechanism |
| XiheFeatureUngroupAttention | - | attention_mechanism |
| XiheFeatureGroupAttention | - | attention_mechanism |

---

## Decoder (解码器)

| Name | Alias | Category |
|------|-------|----------|
| UNetDecoder | U-Net Decoder Family | decoder |
| GraphViTDecoder | Graph Vision Transformer Decoder | graph_decoder |
| FengWuDecoder | FengWu Weather Decoder | decoder |
| MeshGraphDecoder | Mesh Graph Decoder | graph_decoder |
| ProtenixAtomAttentionDecoder | AlphaFold3 Atom Attention Decoder | protein_decoder |

---

## Diffusion (扩散模型)

| Name | Alias | Category |
|------|-------|----------|
| ProtenixDiffusionSystem | ProtenixDiffusion | generative_model |
| AlphaFold3DiffusionModule | DiffusionModule | generative_model |

---

## Encoder (编码器)

| Name | Alias | Category |
|------|-------|----------|
| UNetEncoder | U-Net Encoder Family | encoder |
| GraphViTEncoder | Graph Vision Transformer Encoder | graph_encoder |
| FengWuEncoder | FengWu Weather Encoder | encoder |
| MeshGraphEncoder | Mesh Graph Encoder | graph_encoder |
| ProtenixEncoding | - | - |

---

## Embedding (嵌入层)

| Name | Alias | Category |
|------|-------|----------|
| GraphCastEncoderEmbedder | GraphCastEmbedder | embedding |
| FuxiEmbedding | Fuxi3DPatchEmbedding | embedding |
| XiheEmbedding | Xihe2DPatchEmbedding | embedding |
| FourierPosEmbedding | FourierPositionEncoder | embedding |
| FourCastNetEmbedding | FourCastNetPatchEmbedding | embedding |
| UnifiedPosEmbedding | UnifiedDistanceBasedPosEncoding | embedding |
| TimestepEmbedder | MLPTimeEmbedder | embedding |
| TimestepEmbedding | SinusoidalEmbedding | embedding |
| ProtenixEmbeddingModules | AF3Embeddings | embedding |
| PanguEmbedding3D | Pangu3DPatchEmbedding | embedding |
| PanguEmbedding2D | Pangu2DPatchEmbedding | embedding |
| OneEmbedding | EmbeddingRegistry | embedding |

---

## Evolution (演化模型)

| Name | Alias | Category |
|------|-------|----------|
| nowcastnet | NowcastNetUNet | evolution_model |

---

## Fuser (特征融合器)

| Name | Alias | Category |
|------|-------|----------|
| XiheLocalSIEFuser | Xihe Local SIE Fuser | local_attention |
| XiheGlobalSIEFuser | Xihe Global SIE Fuser | global_attention |
| XiheFuser | Xihe Ocean Model Feature Fuser | ocean_fusion |
| PanguFuser | Pangu-Weather Feature Fuser | feature_fusion |
| PanguDistributedFuser | Pangu-Weather Distributed Feature Fuser | distributed_fusion |
| FourCastNetFuser | FourCastNet AFNO Transformer Block | feature_fusion |
| FengWuFuser | FengWu Weather Feature Fuser | feature_fusion |
| OneFuser | Unified Fuser Interface | fuser_factory |

---

## Head (预测头)

| Name | Alias | Category |
|------|-------|----------|
| UNetPredictionHeads | UNetHead | prediction_head |
| MaskedMSAHead | MSAHead | prediction_head |

---

## Layer (层组件)

| Name | Alias | Category |
|------|-------|----------|
| UNetComponents | UNetLayers | semantic_segmentation |
| PanguTransformerLayers | PanguLayer | transformer_block |
| GraphNeuralNetworkLayer | GNNLayer | graph_neural_network |
| AdvancedActivationFunctions | Activations | activation_function |

---

## Linear (线性层)

| Name | Alias | Category |
|------|-------|----------|
| ProtenixLinear | - | - |

---

## MLP (多层感知机)

| Name | Alias | Category |
|------|-------|----------|
| GMLP | - | - |
| XiheMLP | - | - |
| MeshGraphMLP | - | - |
| FullyConnected | - | - |
| StandardMLP | - | - |
| componet | - | - |

---

## Node (节点更新)

| Name | Alias | Category |
|------|-------|----------|
| MeshNodeBlock | NodeBlock | node_update |

---

## PairFormer (配对形成器)

| Name | Alias | Category |
|------|-------|----------|
| ProtenixPairformer | PairformerStack | pair_single_fusion |

---

## Pooling (池化)

| Name | Alias | Category |
|------|-------|----------|
| RNNClusterPooling | ClusterGRUPooling | hierarchical_pooling |

---

## Processor (处理器)

| Name | Alias | Category |
|------|-------|----------|
| BistrideGraphMessagePassing | BiStrideProcessor | hierarchical_processor |

---

## Recovery (恢复模块)

| Name | Alias | Category |
|------|-------|----------|
| XihePatchRecovery | XiheRecovery | decoder_component |
| PanguPatchRecovery3D | PatchRecovery3D | decoder_component |
| PanguPatchRecovery2D | PatchRecovery2D | decoder_component |

---

## Sample (采样模块)

| Name | Alias | Category |
|------|-------|----------|
| XiheUpSample | - | - |
| PanguUpSample3D | - | - |
| PanguUpSample2D | - | - |
| PanguDownSample3D | - | - |
| PanguDownSample2D | - | - |
| FuxiUpSample | - | - |
| FuxiDownSample | - | - |
| SpatialGraphUpsample | - | - |
| SpatialGraphDownsample | - | - |

---

## Transformer (Transformer模块)

| Name | Alias | Category |
|------|-------|----------|
| XiHeTransformer3D | 3D WeatherLearn Transformer Block | spatial_temporal_block |
| XihelocalTransformer | 3D Earth Swin-Transformer Block | spatial_temporal_block |
| ProtenixTransformer | AlphaFold3DiffusionTransformer | diffusion_transformer |
| PreLNTransformerBlock | PreNormConcatPosBlock | transformer_block |
| OrthogonalNeuralBlock | OrthogonalNeuralOperatorBlock | neural_operator |
| GNOTTransformerBlock | GNOTBlock | neural_operator |
| GalerkinTransformerBlock | GalerkinLinearBlock | linear_transformer |
| FuxiTransformer | FuXiBlock | u_net_transformer |
| FactformerBlock | FactformerEncoderBlock | transformer_encoder |
| EarthTransformer3DBlock | EarthSwinBlock3D_Standard | spatial_temporal_attention |
| EarthTransformer2DBlock | EarthSwinBlock2D | spatial_attention |
| EarthDistributedTransformer3DBlock | EarthSwinBlock3D | spatial_temporal_attention |
| TransolverBlock | Transolver Encoder Block | encoder_block |
| SwinTransformerBlock | SwinBlock | vision_transformer |
| NeuralSpectralBlock | LatentSpectralTransformer | spectral_neural_operator |

---

## Utils (工具函数)

| Name | Alias | Category |
|------|-------|----------|
| MultiwaveletUtilities | wavelet_utils | mathematical_operator |
| CuGraphCSCWrapper | graph | data_structure |
| GNNLayerUtilities | gnnlayer_utils | utility |
| DistributedGraphManager | distributed_graph | distributed_training |
| XiheMaskUtilities | xihe_utils | data_processing |
| PanguUtilities | pangu_utils | model_components_and_spatial_ops |
| FuxiPaddingUtilities | fuxi_utils | spatial_padding |
| LayerUtils | utils | spatial_transform_and_normalization |

---

## 其他组件

| Name | Alias | Category |
|------|-------|----------|
| MSAModule | ProtenixMSA | msa_pair_fusion |
| GroupEquivariantSpectralConv | GSpectralConv | group_equivariant_convolution |
| GeometryAwareSpectralConv | GeoSpectral | irregular_geometry_spectral |
| GroupEquivariantConvolutions | GroupConv | equivariant_operator |
| FuxiFeedForward | FuxiFC | linear_projection |
| FourCastNetFeedForward | FourCastNetFC | feed_forward_network |
| FullyConnectedLayers | FCLayer | core_component |

---

## 统计信息

- **总组件数量**: 100+
- **组件类别**: 20+
- **主要领域**: 气象预报、流体动力学、蛋白质结构预测、图神经网络、Transformer架构

---

## 组件使用说明

所有组件均遵循 OneScience 组件库的统一接口规范，可通过以下方式导入使用：

```python
from onescience.modules import ComponentName
```

具体使用方法请参考各组件的 markdown 文档。

---

*生成日期: 2026-04-02*
