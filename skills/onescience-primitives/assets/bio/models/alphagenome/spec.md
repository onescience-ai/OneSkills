# architecture_overview

AlphaGenome 资源由 Haiku 网络 `model.AlphaGenome` 和高层接口 `dna_model.AlphaGenomeModel` 组成。`create_model` 生成参数初始化、主预测和 junction 预测函数；`create` 从本地 Orbax checkpoint 恢复参数与状态，并把 organism metadata、参考序列和可选注释资源装配为可调用模型。

# parameter_scale

- `ModelSettings.num_splice_sites=512`。
- `ModelSettings.splice_site_threshold=0.1`。
- 参数规模由 checkpoint 与 `model.AlphaGenome` 定义决定，不在 `AlphaGenomeModel` 构造器中重新指定。
- `create` 用 `(1, 2048, 4)` 的 DNA shape 和 `(1,)` 的 organism index 推导 checkpoint 目标树；这不是所有公开预测方法的固定输入长度声明。

# architecture_structure

```text
DNA sequence / genomic interval / variant
  -> DNAOneHotEncoder or FastaExtractor
  -> Haiku AlphaGenome trunk
  -> sequence and pair representations
  -> output heads and splice-junction branch
  -> Output / VariantOutput
  -> optional interval or variant scorers
```

网络层定义位于 `model/model.py`，卷积、注意力和输出 heads 分别位于相应模块；高层数据抽取、输出过滤和评分编排位于 `model/dna_model.py`。

# input_schema

- `create(checkpoint_path, organism_settings=None, model_settings=ModelSettings(), device=None)` 从本地 checkpoint 构造模型。
- `predict_sequence` 接收 DNA 字符串、organism、`requested_outputs`、可选 ontology terms 与 interval。
- `predict_interval` 依赖对应 organism 的 `FastaExtractor`。
- `predict_variant` 接收变异与上下文信息，并可使用参考序列、剪接位点和注释。
- `score_interval`、`score_variant`、`score_ism_variants` 在预测输入基础上接收相应 scorer 配置。

# output_schema

- 序列和区间预测返回 `dna_output.Output`。
- 变异预测返回包含 reference/alternate 预测的变异输出对象。
- 评分方法返回 scorer 生成的映射或表结构，具体字段由选择的 interval/variant scorer 决定。
- 输出 tracks 会按 organism metadata、requested output types 和 ontology terms 过滤。

# shape_transformations

1. DNA 字符串被编码为末维为 4 的 one-hot 数组并增加 batch 维。
2. trunk 生成多尺度序列表征和成对表征。
3. heads 按 metadata 产生不同 output type 的 tracks；padding tracks 在高层接口中被过滤。
4. 变异路径对 reference 与 alternate 序列分别预测，再由 scorer 比较或聚合。

# key_dependencies

当前没有与 AlphaGenome 内部模块一一对应的独立 bio component primitive；构建代码时应直接使用本模型架构说明和源码引用中的接口。

# common_modification_points

- 用 `OrganismSettings` 绑定非默认 metadata、FASTA、GTF、PAS 和 splice-site feather 文件。
- 通过 `requested_outputs` 和 ontology terms 缩小输出范围，避免无关 track 计算与搬运。
- 新增评分逻辑时扩展 scorer 层，不修改主模型输出头的张量协议。
- 需要低层模型调用时使用 `create_model` 返回的函数；常规预测优先使用 `create` 和 `AlphaGenomeModel`。

# implementation_risks

- 未配置 `FastaExtractor` 时，区间和需要参考序列的变异方法会失败。
- 某些 scorer 只有在提供 GTF、PAS 或剪接注释后才可用。
- 自动设备选择要求 GPU 或 TPU；若明确使用 CPU，必须显式传入 JAX device。
- checkpoint metadata 与外部 metadata 不匹配会导致输出 track 解释错误。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/model/model.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/model/dna_model.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/model/heads.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/model/attention.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/model/convolutions.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/model/variant_scoring/variant_scoring.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphagenome/finetuning/finetune.py`
