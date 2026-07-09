# 蛋白设计与结构验证工作流

- workflow_id: `protein-design-structure-validation`

## 适用范围

用于从设计目标到 backbone generation、sequence design、structure prediction、complex validation、candidate ranking 和失败恢复的端到端蛋白设计规划。典型触发包括 RFdiffusion、ProteinMPNN、binder design、motif scaffolding、SimpleFold、OpenFold、AlphaFold、Protenix、AlphaFold3 和结构验证。

## 输入

- 必需：设计目标；起点类型；目标长度/contig/motif/binder 约束；已有 backbone PDB 或序列 FASTA；计算资源约束。
- 分支输入：target/motif PDB、chain ID、fixed residues/positions、sampling 数量、complex stoichiometry、ligand/nucleic acid definition。
- 可选：MSA/template 资产、model asset 路径、候选过滤阈值、界面/接触约束。

## 输出

- generated backbones。
- designed sequences。
- predicted structures 或 complex structures。
- 置信度指标、motif RMSD、interface/contact、clash、diversity。
- ranked candidate table、failure table、复现记录。

## 流程节点

1. 判定目标：binder design、motif scaffolding、fixed-backbone redesign、sequence-to-structure validation 或 complex validation。
2. 若需要生成 backbone，规划 RFdiffusion 分支。
3. 对 backbone 进行 ProteinMPNN 序列设计，记录固定位置和采样参数。
4. 根据分子类型选择 fold validation 或 complex validation。
5. 综合结构置信度、设计分数、motif 保真、界面接触、clash 和多样性排序。
6. 输出候选表和失败恢复建议。

## 边界与分流

- 单独“给序列预测结构”直接召回结构预测模型，不必使用完整工作流。
- 分子生物学 primer、plasmid、CRISPR 设计转到 `bio_molecular_design_app`。
- RFdiffusion、ProteinMPNN、AlphaFold/OpenFold/SimpleFold、AlphaFold3/Protenix 各自承担不同节点，不能互相替代。

## 模型与工具选择边界

- RFdiffusion：生成或 scaffold backbone；不输出最终序列设计。
- ProteinMPNN：从 backbone 设计序列；不是结构预测模型。
- AlphaFold/OpenFold/SimpleFold：蛋白-only fold validation。
- AlphaFold3/Protenix：蛋白-配体、蛋白-核酸、多分子复合物验证。
- Evo2/ESM：仅在序列生成、embedding 或表示学习分支需要时使用，设计候选仍需结构/功能验证。

## 质量检查

- motif/contig/chain ID 和固定残基正确。
- ProteinMPNN 输出满足固定位置约束。
- fold validation 的 pLDDT/PAE 或等价置信度可解释。
- complex validation 检查 interface/contact、ligand/nucleic acid placement 和 clashes。
- 输入协议与模型要求一致，模型资产可用。

## 回退策略

- RFdiffusion 失败：降低约束复杂度或改用已有 backbone。
- ProteinMPNN 多样性不足：调整 temperature、sampling 或 fixed positions。
- fold validation 失败：检查 FASTA/PDB 格式、MSA/template 假设和模型输入。
- complex 输入不兼容：切换到 AlphaFold3/Protenix 兼容格式准备。

## 资源召回建议

- backbone generation：`rfdiffusion`。
- sequence design：`proteinmpnn`。
- fold validation：`alphafold`、`openfold`、`simplefold`。
- complex validation：`alphafold3`、`protenix`。
- 数据管线：`biology_protein_dataset`、`openfold_data_pipeline`、`protenix_data_pipeline`、`biology_protenix_infer_adapter`、`simplefold_data_pipeline`。
