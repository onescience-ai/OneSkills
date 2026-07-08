# component_info

AlphaGenome 是面向调控基因组学的 DNA 序列模型组件，核心功能是在长序列上下文中同时预测多类基因组功能轨迹、接触图和剪接信号，并为变异效应评分、区间评分和微调提供统一模型接口；它处理的是 DNA/基因组区间，不是蛋白结构、蛋白设计或小分子生成任务。

# architecture_overview

AlphaGenome 采用 U-Net + Transformer 混合架构，硬性基准来自 `examples/biosciences/alphagenome/README.md` 中的模型架构描述。

DNA 序列: `(1 Mbp, 4)`
  -> DnaEmbedder: 卷积嵌入 `4 -> 768`
  -> DownResBlock x7: `1 bp -> 128 bp`, `768 -> 1536`
  -> TransformerTower x9: MHABlock + MLPBlock + PairUpdateBlock
  -> SequenceToPairBlock: 序列表示转成成对表示
  -> UpResBlock x7: 融合 skip connection, `128 bp -> 1 bp`
  -> OutputEmbedder: 生物体特异调整
  -> GenomeTracksHead / ContactMapsHead / SpliceSitesHead

# parameter_scale

- 支持最长约 `1,048,576` bp 输入窗口。
- 1 bp 分辨率输出包括 ATAC、DNase、CAGE、RNA-seq、PRO-cap 和剪接相关输出。
- 128 bp 分辨率输出包括 ChIP-TF、ChIP-Histone 等轨迹。
- 2048 bp 分辨率输出包括 Hi-C contact map。
- README 示例中模型版本支持 `FOLD_0` 到 `FOLD_4` 以及 `all_folds`。

# architecture_structure

- `DNAOneHotEncoder`: DNA 字符串到 `(L, 4)` one-hot。
- `DnaEmbedder`: 序列卷积嵌入。
- `DownResBlock`: U-Net 下采样编码。
- `TransformerTower`: 长序列 attention 与 pair update。
- `SequenceToPairBlock`: 生成 pair representation。
- `UpResBlock`: 上采样并融合 skip connection。
- `OutputEmbedder`: 输出轨迹的生物体特异性调整。
- `GenomeTracksHead`: ATAC/DNase/CAGE/RNA-seq/ChIP/PRO-cap 等轨迹。
- `ContactMapsHead`: Hi-C 接触图。
- `SpliceSitesClassificationHead`, `SpliceSitesUsageHead`, `SpliceSitesJunctionHead`: 剪接相关输出。

# input_schema

- 核心生物输入:
  - 参考基因组 FASTA，通常需要 `.fai` 索引。
  - genomic interval: chromosome, start, end。
  - organism: `HOMO_SAPIENS` 或 `MUS_MUSCULUS`。
  - model version: `FOLD_0` 到 `FOLD_4` 或 `all_folds`。
- 变异评分输入:
  - SNV 或 VCF。
  - reference interval。
  - requested outputs / ontology terms。
- 微调输入:
  - regions CSV，列包含 chromosome,start,end。
  - BigWig 信号文件。
  - 预训练模型目录。

# output_schema

- 推理输出:
  - 各预测类型保存为 `.npy`。
  - 典型 shape 包括 `(1048576, n_tracks)`、`(8192, n_tracks)` 和 contact map 相关输出。
- 变异评分输出:
  - 每个变异的评分表 CSV。
  - `variant_scoring_summary.csv`。
  - SDK 中可返回 AnnData 风格评分表。
- 评估输出:
  - 包含 `bundle`, `metric`, `value` 的 CSV。
- 微调输出:
  - finetuned model checkpoint 和训练日志。

# shape_transformations

- DNA string -> one-hot: `(L, 4)`
- DnaEmbedder: `(L, 768)`
- DownResBlock x7: `(L / 128, 1536)`
- TransformerTower: `(L / 128, hidden)`
- SequenceToPairBlock: `(L / 2048, L / 2048, pair_channel)`
- UpResBlock x7: `(L, 1536)` 与 `(L / 128, 3072)`
- Genome tracks: 1 bp 或 128 bp 轨迹
- Contact maps: 2048 bp 接触图

# key_dependencies

- `AlphaGenome`
- `AlphaGenomeModel`
- `DNAOneHotEncoder`
- `SequenceEncoder`
- `SequenceDecoder`
- `TransformerTower`
- `GenomeTracksHead`
- `ContactMapsHead`
- `CenterMaskVariantScorer`
- `ContactMapScorer`
- `GeneVariantScorer`
- `DataPipeline`

# common_modification_points

- 新轨迹预测任务优先改 output metadata、head 配置和数据束，不改核心 trunk。
- 变异效应任务优先选择合适的 scorer，例如 center mask、contact map、gene mask、polyadenylation 或 splice junction。
- 微调任务优先调整 regions CSV、BigWig 输入、batch size、learning rate 和训练步数。
- 物种切换必须同步 organism、参考基因组、metadata 和 model version。

# implementation_risks

- AlphaGenome 只处理 DNA/基因组区间，不处理蛋白 FASTA、PDB、小分子或复合物结构。
- 输入窗口长度、染色体坐标和 FASTA 索引错误会直接导致抽取失败或 shape 不匹配。
- 变异评分必须保证 reference allele 与参考基因组一致。
- `all_folds` 推理资源消耗高于单 fold。
- BigWig 微调数据需要和训练区间、track metadata 对齐。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/model/model.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/model/dna_model.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/model/heads.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/model/attention.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/model/convolutions.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/model/variant_scoring/variant_scoring.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/finetuning/finetune.py`
- `{onescience_path}/onescience/examples/biosciences/alphagenome/README.md`
