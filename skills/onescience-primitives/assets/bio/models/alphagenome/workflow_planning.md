# description

AlphaGenome 规划知识用于从本地 checkpoint 构建 DNA 序列、基因组区间和变异预测/评分代码，并按所需方法装配 organism metadata、参考序列和注释资源。

# when_to_use

- 需要对 DNA 字符串预测 AlphaGenome 输出 tracks。
- 需要对基因组 interval 或 variant 预测，且可提供对应 organism 资源。
- 需要调用 interval、variant 或 ISM scorer。
- 不用于蛋白结构或小分子模型任务。

# inputs

- 本地 AlphaGenome checkpoint path。
- `ModelSettings` 与可选 JAX device。
- organism、requested output types 和可选 ontology terms。
- 预测对象：DNA sequence、genome interval、variant 或 ISM variants。
- 按方法需要提供 FASTA、GTF、PAS 与 splice-site annotation paths。

# outputs

- 由 `create` 构建的 `AlphaGenomeModel`。
- `dna_output.Output`、variant output 或 scorer 结果。
- 对可用 organism 资源、请求 tracks 和缺失 scorer 依赖的记录。

# procedure

1. 确定调用 `predict_sequence`、`predict_interval`、`predict_variant` 或评分方法。
2. 仅为该方法准备必要的 `OrganismSettings` 资源。
3. 调用 `create(checkpoint_path, organism_settings=..., model_settings=..., device=...)`。
4. 传入真实 organism、requested outputs、ontology terms 和预测对象。
5. 检查返回对象中的 metadata 与 track shape。
6. 评分任务再调用对应 score 方法，并保留 scorer 名称与参数。

# constraints

- checkpoint、测试区间和轨迹列表均由调用方显式提供。
- 区间预测依赖 `FastaExtractor`；相关 scorer 依赖各自注释资源。
- CPU 运行需要显式传入 CPU JAX device。
- requested outputs 必须来自源码定义的 `dna_output.OutputType`。

# next_phase_recommendation

- 将输出 tracks 转交下游统计、可视化或变异排序。
- 对大量 variants 使用批处理与稳定的 interval 对齐策略。
- 需要微调时以 `finetuning/finetune.py` 的源码接口另建训练计划。

# fallback

- checkpoint restore 失败时核验 checkpoint tree 与 metadata，而不是更改参数名。
- 缺少 FASTA/annotation 时退回仅需 DNA 字符串的 `predict_sequence`，前提是满足用户目标。
- scorer 不可用时返回原始 prediction output，并明确缺少的注释依赖。
