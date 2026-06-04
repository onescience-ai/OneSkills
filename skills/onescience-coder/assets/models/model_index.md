# Model Index

## 使用建议

- 用户明确提到模型名时，先读这里，再跳到对应模型卡。
- 若用户没提模型名，但目标很像已有案例，也先在这里找最接近的基线。
- 先分清楚模型吃的是哪种协议：`(x, fx)`、`PyG Data`、`DGLGraph`，还是 `(node_features, edge_features, graph)`。
- 领域专项的默认候选、任务路由和硬边界优先由 `onescience-role` 下对应领域目录承接；本文只做跨领域模型卡索引。
- 材料领域模型必须显式登记数据协议和训练入口；当前 MACE 是材料模型卡的标准样板，后续新增材料模型优先按 MACE 卡结构补齐。
## 已登记模型

| 模型 | 任务类型 | 输入协议摘要 | 主干类型 | 状态 | 模型卡 |
| --- | --- | --- | --- | --- | --- |
| `Transolver` | CFD / pointwise field regression | `PyG Data.x + Data.pos` | pointwise physics transformer | `stable` | [transolver.md](./transolver.md) |
| `Transolver (CFD_Benchmark)` | CFD / benchmark token regression | `(x, fx, T)` | token transformer with slicing | `stable` | [transolver_benchmark.md](./transolver_benchmark.md) |
| `MeshGraphNet` | CFD / graph rollout & regression | `DGLGraph + node/edge features` | encode-process-decode graph net | `stable` | [meshgraphnet.md](./meshgraphnet.md) |
| `MeshGraphNet (CFD_Benchmark)` | CFD / explicit graph regression | `(node_features, edge_features, graph)` | encode-process-decode graph net | `stable` | [meshgraphnet_benchmark.md](./meshgraphnet_benchmark.md) |
| `MACE` | materials / MLIP fine-tuning & atomistic simulation | extxyz -> PyG `AtomicData` / MACE Batch | E(3)-equivariant high-order MPNN potential | `stable` | [mace.md](./mace.md) |
| `UMA` | materials / universal MLIP multi-task fine-tuning & inference | `custom_stack AtomicData` / Hydra dataloader | Hydra + eSCNMD equivariant backbone + task heads | `stable` | [uma.md](./uma.md) |
| `FNO` | CFD / operator learning | `(x, fx)` | Fourier operator trunk | `stable` | [fno.md](./fno.md) |
| `F_FNO` | CFD / operator learning | `(x, fx)` | factorized Fourier trunk | `stable` | [f_fno.md](./f_fno.md) |
| `GFNO` | CFD / 2D operator learning | `(x, fx)` | group-equivariant Fourier trunk | `stable` | [gfno.md](./gfno.md) |
| `U_FNO` | CFD / operator learning | `(x, fx)` | Fourier trunk with parallel U-branch | `stable` | [u_fno.md](./u_fno.md) |
| `U_NO` | CFD / operator learning | `(x, fx)` | U-shaped neural operator | `stable` | [u_no.md](./u_no.md) |
| `U_Net (CFD_Benchmark)` | CFD / operator learning | `(x, fx)` | U-shape encoder/decoder | `stable` | [u_net_operator.md](./u_net_operator.md) |
| `MWT` | CFD / operator learning | `(x, fx)` | multiwavelet transform trunk | `stable` | [mwt.md](./mwt.md) |
| `LSM` | CFD / hybrid operator learning | `(x, fx)` | U-Net + latent spectral blocks | `stable` | [lsm.md](./lsm.md) |
| `DeepONet` | CFD / operator learning | `(x, fx)` | branch-trunk MLP operator | `stable` | [deeponet.md](./deeponet.md) |
| `ONO` | CFD / operator learning | `(x, fx)` | orthogonal neural operator blocks | `stable` | [ono.md](./ono.md) |
| `GNOT` | CFD / operator learning | `(x, fx)` | MoE-style transformer operator | `stable` | [gnot.md](./gnot.md) |
| `Transformer` | CFD / token baseline | `(x, fx)` | standard self-attention trunk | `stable` | [transformer.md](./transformer.md) |
| `Galerkin_Transformer` | CFD / token baseline | `(x, fx)` | linear-attention transformer | `stable` | [galerkin_transformer.md](./galerkin_transformer.md) |
| `Factformer` | CFD / token baseline | `(x, fx)` | factorized-attention transformer | `stable` | [factformer.md](./factformer.md) |
| `Swin_Transformer` | CFD / structured 2D baseline | `(x, fx)` | windowed transformer trunk | `stable` | [swin_transformer.md](./swin_transformer.md) |
| `GraphSAGE` | CFD / graph baseline | `(x, fx, edge_index)` | PyG message passing | `stable` | [graphsage.md](./graphsage.md) |
| `Graph_UNet` | CFD / graph baseline | `(x, fx, edge_index)` | hierarchical graph U-Net | `stable` | [graph_unet.md](./graph_unet.md) |
| `PointNet` | CFD / point baseline | `(x, fx)` | pointwise MLP + global pooling | `stable` | [pointnet.md](./pointnet.md) |
| `RegDGCNN` | CFD / point baseline | `(x, fx)` | dynamic kNN EdgeConv trunk | `stable` | [regdgcnn.md](./regdgcnn.md) |
| `Pangu` | weather / global forecasting | surface 2D + upper-air 3D | 3D token trunk | `stable` | [pangu.md](./pangu.md) |
| `FourCastNet` | weather / global forecasting | 2D fields | AFNO trunk | `stable` | [fourcastnet.md](./fourcastnet.md) |
| `Fuxi` | weather / spatiotemporal forecasting | multi-step 2D/3D blocks | U-shape Swin trunk | `stable` | [fuxi.md](./fuxi.md) |
| `FengWu` | weather / medium-range forecasting | multi-branch 2D inputs | encoder-decoder + 3D fuser | `stable` | [fengwu.md](./fengwu.md) |
| `AlphaFold` | biosciences / protein folding | AlphaFold v2 FASTA/MSA/template features | JAX/Haiku Evoformer + StructureModule | `stable` | [alphafold.md](./alphafold.md) |
| `OpenFold` | biosciences / protein folding | OpenFold AF2 batch dict | PyTorch Evoformer + StructureModule | `stable` | [openfold.md](./openfold.md) |
| `AlphaFold3` | biosciences / biomolecular structure | AF3 JSON / JAX feature batch | JAX/Haiku Pairformer + diffusion | `stable` | [alphafold3.md](./alphafold3.md) |
| `Protenix` | biosciences / biomolecular structure | Protenix / AF3 feature dict | PyTorch Pairformer + diffusion | `stable` | [protenix.md](./protenix.md) |
| `SimpleFold` | biosciences / protein folding | `noised_pos + t + feats dict` | flow-matching FoldingDiT | `stable` | [simplefold.md](./simplefold.md) |
| `RFdiffusion` | biosciences / protein backbone generation | Hydra contig / PDB / diffusion config | RoseTTAFold + diffusion sampler | `stable` | [rfdiffusion.md](./rfdiffusion.md) |
| `ProteinMPNN` | biosciences / inverse folding | backbone atoms + sequence/masks | graph-conditioned encoder-decoder | `stable` | [proteinmpnn.md](./proteinmpnn.md) |
| `PT-DiT` | biosciences / protein co-design | ProToken + AA embeddings, diffusion timesteps | JAX/Flax diffusion transformer | `stable` | [pt_dit.md](./pt_dit.md) |
| `ProToken` | biosciences / protein structure tokenizer | PDB-derived residue features / VQ codes | VQ encoder-decoder + structure decoder | `stable` | [protoken.md](./protoken.md) |
| `Evo2` | biosciences / genome LM | `tokens, position_ids, labels, loss_mask` | NeMo/Megatron Mamba | `stable` | [evo2.md](./evo2.md) |
| `MolSculptor` | biosciences / molecular design | SMILES / molecule graph features / latent tokens | graph encoder + decoder + DiT | `stable` | [molsculptor.md](./molsculptor.md) |
| `SE3Transformer` | biosciences / equivariant component | DGL graph + fiber features + `rel_pos` | SE(3)-equivariant graph attention | `component_only` | [se3_transformer.md](./se3_transformer.md) |

## 生信覆盖对照

当前生信模型卡按 `onescience` 中的源码目录和 `examples/biosciences` 交叉覆盖。新增或维护生信内容时，先按本表核对，不要只从 `Protenix` 分支出发。

| OneScience 位置 | skill 覆盖 | 拆解策略 |
| --- | --- | --- |
| `src/onescience/flax_models/alphafold` + `examples/biosciences/alphafold` | `AlphaFold` | JAX/Haiku AF2 推理流水线，拆到 `AlphaFoldJAXComponents`，不虚构 `One*` wrapper |
| `src/onescience/models/openfold` + `examples/biosciences/openfold` | `OpenFold` | PyTorch AF2/OpenFold，拆成 Evoformer 与 StructureModule 两个高层内部契约 |
| `src/onescience/flax_models/alphafold3` + `examples/biosciences/alphafold3` | `AlphaFold3` | JAX/Haiku AF3 JSON 推理，拆到 AF3 JAX trunk / diffusion / confidence 组件组 |
| `src/onescience/models/protenix` + `examples/biosciences/protenix` | `Protenix` | OneScience PyTorch AF3 风格模型，保留已有 `One*` 组件契约 |
| `src/onescience/models/simplefold` + `examples/biosciences/simplefold` | `SimpleFold` | flow matching FoldingDiT，拆到 FoldingDiT 主干契约 |
| `src/onescience/models/rfdiffusion` + `examples/biosciences/RFdiffusion` | `RFdiffusion` | Hydra 采样 / RoseTTAFold / diffusion 工作流，拆成采样与结构轨道组件组 |
| `src/onescience/models/proteinmpnn` + `examples/biosciences/ProteinMPNN` | `ProteinMPNN` | backbone graph inverse folding，拆成特征、encoder/decoder 与采样约束组件组 |
| `src/onescience/flax_models/Pt_DiT` + `examples/biosciences/pt_dit` | `PT-DiT` | ProToken/AA latent diffusion transformer，拆到 PT-DiT 组件组 |
| `src/onescience/flax_models/protoken` | `ProToken` | 结构 tokenizer / VQ encoder-decoder，拆到 ProToken 组件组 |
| `src/onescience/models/evo2` + `examples/biosciences/evo2` | `Evo2` | genome LM / Mamba，拆到 Evo2Mamba 契约 |
| `src/onescience/flax_models/MolSculptor` + `examples/biosciences/molsculptor` | `MolSculptor` | 小分子生成与优化，拆到 graph encoder / decoder / diffusion / reward 组件组 |
| `src/onescience/models/se3_transformer` | `SE3Transformer` | RFdiffusion 内部等变图层，仅作为 `component_only` |

## 选型提示

- 生物分子结构预测：
  - 原版 AF2 JAX 推理、AlphaFold/Multimer FASTA + MSA/template 流水线，先看 `AlphaFold`
  - AF2/OpenFold PyTorch 特征流水线、训练或微调，先看 `OpenFold`
  - AF3 JAX JSON 推理、JackHmmer/MMseqs data pipeline，先看 `AlphaFold3`
  - AF3 风格 PyTorch/OneScience 组件化结构预测，先看 `Protenix`
  - flow matching 折叠、SimpleFold example 或 ESM 条件折叠，先看 `SimpleFold`
- 蛋白设计 / inverse folding：
  - 从 PDB 骨架设计序列、固定链、PSSM、tied positions，先看 `ProteinMPNN`
- 蛋白骨架生成 / motif scaffolding / binder design：
  - 无条件骨架生成、基序支架、对称性设计、结合体骨架、partial diffusion，先看 `RFdiffusion`
  - 若 RFdiffusion 生成骨架后要补序列，下一步再看 `ProteinMPNN`
- 蛋白序列-结构协同生成 / 结构 tokenizer：
  - PDB 到结构 token、ProToken index 或结构重建，先看 `ProToken`
  - ProToken + AA embedding 的 de novo co-design、RePaint 或 latent evolution，先看 `PT-DiT`
- 基因组长序列建模：
  - DNA token 语言模型、Evo2 训练或推理，先看 `Evo2`
- 小分子 / 药物设计：
  - SMILES/分子图生成、分子优化、QED/SA/LogP/DSDP reward，先看 `MolSculptor`
- 等变结构组件：
  - 只有要改 RFdiffusion structure track 或 SE(3) 等变图层时，再看 `SE3Transformer`
- 材料化学 / 原子势函数路线：
  - 如果用户提到 MACE-MP、MACE-MPA、MACE-OMAT、extxyz、E0s、ASE/LAMMPS 或 MACE fine-tuning，先看 `MACE`
  - 如果用户提到 UMA、OC20、OMAT、OMOL、Hydra、ase_db、elem_refs、normalizer_rmsd、charge/spin 或 FAIRChemCalculator，先看 `UMA`
  - 如果任务只是“把原子数据接入模型”，先同时看对应模型卡和对应 `../datapipes/materials_<model_route>.md`
  - 如果用户提到尚未登记的新材料模型，先标记为 `unregistered_material_model`，再用 `MACE` 卡作为材料模型卡模板提取需要补齐的输入、输出、训练入口和风险点

## 生信模型协议提醒

- `AlphaFold`、`OpenFold`、`AlphaFold3`、`Protenix`、`SimpleFold` 都可能输出结构，但 batch / feature dict / 框架栈不兼容。
- `ProteinMPNN` 是结构到序列的 inverse folding，不要与结构预测模型共用训练 batch。
- `RFdiffusion` 是骨架生成 / 设计框架，不是侧链序列设计模型；生成结果通常需要后接 ProteinMPNN 或筛选流程。
- `PT-DiT` 和 `ProToken` 共享结构 token / embedding 语义，不要把普通 FASTA 或 OpenFold batch 直接送入 PT-DiT。
- `Evo2` 是基因组语言模型，优先对齐 NeMo / Megatron batch 协议，而不是 biology 通用 `aatype` 输出。
- `MolSculptor` 属于小分子/药物设计，不应复用蛋白质 datapipe 或 AF2/AF3 feature dict。

## 材料模型新增接口

新增材料模型时，按同一组文件登记，不要把索引逻辑写死成 MACE/UMA：

1. 在本表新增模型行，写清输入协议和主干类型。
2. 新增 `./<model_route>.md` 模型卡。
3. 新增 `../datapipes/materials_<model_route>.md` 数据卡。
4. 新增 `../contracts/<model_route>_material_stack.md` 组件契约。
5. 同步更新：
   - `../datapipes/datapipe_index.md`
   - `../contracts/component_index.md`
   - `../../onescience-role/assets/matchem/matchem_task_index.md`

材料模型卡建议沿用 `mace.md` 的章节组织：模型定位、输入定义、输出定义、主干结构、依赖组件、shape 变化、默认关键参数、常见修改点、风险点、检索顺序和源码锚点。


## 维护建议

- 新增模型卡时，优先写清输入协议、主干类型、最容易混淆的实现差异。
- 对同名不同实现，优先在索引里直接拆成两行，而不是只在单张卡片里顺带提一句。
