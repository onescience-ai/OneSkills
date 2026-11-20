# 骨架任务：序列过滤与模型准备

- domain: bio
- 复用场景数: 7
- 实例任务数: 7

## 步骤描述（跨场景聚合去重）
- 加载权重并进行长度过滤、分词和参考信息编码。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}和{REFERENCE_DB}，过滤短于{MIN_CONTIG_LENGTH}的序列并生成模型特征。
- 先核对 `{CHECKPOINT}` 的实际模型身份、revision 与当前任务路线，读取下列匹配实例正文及其同版 config、tokenizer、隐藏态接口和配套权重依据，再形成模型准备/编码交接。把来源、适用条件、输入预算和输出契约传给规划/编码消费者；固定模型参数仅在匹配实例条件下采用。
- 按既有[模型加载契约](../../../../../onescience-infer/references/phase_4_model_loading.md)核对配置与真实权重、预处理资产、device/dtype 和 smoke load。将方法接口已知、实现是否具备成功路径、物理资源是否就绪及实际 forward 是否完成分别记录；缺资源时仍提供已核验方法知识，勿报告已加载或已生成表征。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=cross_species_amr.pt
- {MIN_CONTIG_LENGTH} | required=False | type=int | var_name=最短序列长度 | hint=设置最短序列碱基数 | default=1000
- {REFERENCE_DB} | required=False | type=doc | var_name=参考数据库 | hint=参考数据库名称 | default=GTDB_R220
- 按当前输入绑定上述示例名与路径，勿由默认名称推断资源已存在。以 bp 解释 `{MIN_CONTIG_LENGTH}`，另按匹配 tokenizer 计算含特殊 token 的模型上下文预算；明确当前输入是否适用长度过滤，并记录过滤/截断决定。`{REFERENCE_DB}` 仅在参考编码需要时使用，不能替代必需的模型配置、tokenizer 与权重。

## 产出
- 序列表征
- 过滤后序列
- 过滤统计
- 对真实序列表征附逐行 `row_id`、实际 shape、模型/tokenizer 版本、池化 mask/特殊 token 政策及截断统计；与过滤后序列和样本保持对应。把可追溯接口说明与真实加载/forward 证据分别交给下游，勿将准备说明当作已产生的向量。

## 质量门禁 quality_gate
- 参考版本可追溯
- 序列与样本映射保持
- 过滤阈值已记录
- 按匹配实例核验隐藏态接口和实际维度；冻结表征任务核对参数冻结、eval、有效 token 聚合及 padding/特殊 token 政策。保存逐行映射与验证证据；区分资源受阻、尚未实现和已执行成功，未验证项保留未验证状态，不以空产物或替代向量充当真实表征。

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- bio-sequence-filtering-model-contrastive-learning-driven-inst
- bio-sequence-filtering-model-cross-species-antimicrobial-inst
- bio-sequence-filtering-model-dna-sequence-driven-microbia-inst
- bio-sequence-filtering-model-function-guided-metageneome-inst
- [bio-sequence-filtering-model-pathogen-monitoring-metageno-inst](../bio-sequence-filtering-model-pathogen-monitoring-metageno-inst/knowledge.md)：当 `{CHECKPOINT}` 确认为该实例覆盖的 METAGENE-1 及其固定 revision 时，读取正文中的配置、分词、最后隐藏态、池化和权重配套依据，并传给模型准备/编码消费者；FGBERT 及其他模型须另核对各自来源，勿继承 METAGENE-1 数值。
- bio-sequence-filtering-model-phage-and-prokaryotic-host-inst
- bio-sequence-filtering-model-phage-lifestyle-classificati-inst

## 复用场景
- B95
- B93
- B91
- B96
- B92
- B94
- B97
