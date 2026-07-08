# description

Evo2 的规划知识用于判断何时把 DNA/genome 序列任务交给基因组语言模型，并把用户目标组织成推理、训练、微调或分析链路中的序列评分节点。它的核心产物是生成序列、logits、sequence log probability、variant effect 类打分、训练 loss 或 checkpoint。

# when_to_use

- 用户明确提到 Evo2、genome language model、DNA token model、基因组语言模型、Evo2 generation、predict、logits、score、variant effect。
- 用户要求训练 Evo2、微调 Evo2、继续训练 genome LM、使用自己的 genome FASTA/JSON/mmap 数据、调整 `seq_length`、checkpoint 或 batch 协议。
- 用户希望在基因组分析链路中加入候选 DNA 序列生成、序列似然排序、变异上下文模型打分、病原/微生物/比较基因组候选片段的模型证据。
- 输入是 DNA prompt、DNA FASTA、consensus genome、assembly/contig 片段、候选调控区、变异上下文序列或 Evo2 训练数据，且目标需要 genome LM 建模。
- 不因“基因组/变异/组装/监测”这些泛词自动召回 Evo2；传统 FASTQ、BAM、VCF、assembly、RNA-seq、single-cell、蛋白结构、蛋白设计、小分子或临床解读按对应生信分析路线处理。

# inputs

- 用户目标：prompt generation、FASTA logits、sequence scoring、variant scoring、training、finetuning、checkpoint 恢复、候选序列评分节点。
- 生物输入：DNA prompt、FASTA、变异上下文序列、assembly/consensus/contig、候选片段、训练 JSON/mmap 数据。
- 模型输入：checkpoint、tokenizer、`seq_length`、model size、checkpoint format、BOS/EOD 策略、并行参数、batch size。
- 训练输入：dataset config、dataset dir、`tokens`、`position_ids`、`labels`、`loss_mask`、学习率、训练步数、输出目录。
- 上下游输入：上游可来自序列清洗、组装、共识序列、变异上下文构造或候选片段筛选；下游可进入变异解释、比较基因组、病原监测、调控序列筛选，或经 ORF/CDS 翻译后进入蛋白模型路线。

# outputs

- 召回决策：是否使用 Evo2，以及 `inference`、`training`、`finetuning`、`scoring_node` 或 `not_evo2` 模式。
- 执行计划：入口脚本、checkpoint、输入文件、生成/打分/训练参数、并行配置、输出目录和资源策略。
- 结果产物：generated sequence、logits、sequence log probability、variant score、score table、`seq_idx_map.json`、training loss、checkpoint、日志和失败诊断。
- 下游计划：把 Evo2 结果作为模型证据或候选排序列，交给变异/比较基因组/病原监测/调控筛选等分析；若接蛋白模型，先做 ORF/CDS/reading frame/翻译检查。

# procedure

1. 判断用户是否明确需要 Evo2 或 genome LM 能力；若只是传统生信分析，保持原分析路线。
2. 选择模式：DNA prompt 续写走 `infer.py`；FASTA logits、序列似然、variant scoring 和候选排序走 `predict.py`；训练或微调走 `train_one_node.py` 或集群训练脚本。
3. 检查输入语义：确认是 DNA/genome 序列或 Evo2 token batch，记录物种/参考版本、序列 ID、坐标、方向、长度和非 DNA 字符处理。
4. 检查运行条件：checkpoint、tokenizer、`seq_length`、checkpoint format、并行参数、NeMo/Megatron/BioNeMo 环境、输入路径和输出目录。
5. 生成命令或交接计划，并写清 `usage_mode`、入口、输入产物、输出产物和预期观察项。
6. 解析 observation：生成文件、logits/score table、`seq_idx_map.json`、checkpoint、日志、失败序列、训练 loss 是否完整。
7. 衔接下游：Evo2 输出只作为 genome LM 证据；需要进入蛋白模型时，先把 DNA/CDS 转为蛋白序列并检查 reading frame，再转 ESM、OpenFold、Protenix、ProteinMPNN 或 SimpleFold。

# constraints

- Evo2 不处理蛋白结构、蛋白设计、小分子、PDB、MSA、SMILES、AF2/AF3 feature dict 或 ProteinMPNN/RFdiffusion batch。
- 推理前必须匹配 checkpoint、entrypoint、tokenizer、模型规模、`seq_length` 和并行配置。
- 训练/微调不能只用普通 FASTA prediction 样本；必须确认 `labels/loss_mask`、label offset、sample length 和 dataset config。
- Evo2 不能替代 variant calling、genome assembly、系统发育、数据库注释、临床解释、公共卫生判断或湿实验验证。
- 不为了使用模型而强行插入 Evo2；只有当用户意图和数据对象同时命中 genome LM 能力时才召回。

# next_phase_recommendation

- 独立推理：固定 `infer.py` 或 `predict.py`、checkpoint、输入、输出目录、preflight 和输出校验。
- 训练/微调：进入 OneScience 生信模型开发路线，读取 Evo2 模型卡、Evo2Mamba 合约和 genome datapipe 说明，先固化数据预处理和 batch 协议。
- 分析链路评分：让上游产出可追踪 FASTA 或候选序列，Evo2 输出 score table 后再交给原分析路线消费。
- 与蛋白模型衔接：先完成 ORF/CDS/翻译和 reading frame 检查，再进入 ESM、OpenFold、Protenix、ProteinMPNN 或 SimpleFold。
- 与临床、病原监测或转化分析衔接：Evo2 结果只进入证据表或排序特征，不写成诊断、治疗或传播结论。

# fallback

- 用户意图模糊：如果只说基因组分析、变异、组装或监测，默认走对应生信 workflow；只有补充 Evo2/genome LM/打分/生成/训练/微调后才召回 Evo2。
- 环境缺失：NeMo/Megatron/BioNeMo、checkpoint 或 tokenizer 不可用时，先做运行交接和 preflight，不直接承诺可执行。
- checkpoint 不匹配：切换到匹配的 checkpoint/model size/脚本版本，或先做 checkpoint conversion。
- 训练数据协议不满足：退回数据预处理，补齐 JSON/mmap、`labels/loss_mask`、label offset、sample length 和大小写策略。
- 显存或长上下文失败：降低 `seq_length`、batch 或并行规模，先用小样本/mock data 验证。
- 下游无法消费输出：保留 Evo2 score table 和序列映射，回到原分析路线，不强行传递到不兼容模型。
