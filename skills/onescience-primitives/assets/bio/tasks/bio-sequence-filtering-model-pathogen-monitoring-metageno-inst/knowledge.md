# 实例任务：序列过滤与模型准备 @ B94

- domain: bio
- 骨架: bio-sequence-filtering-model-preparation-task
- 场景: bio-pathogen-monitoring-metagenomic-foundation-model-scenario (B94)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B94
- 关联论文: METAGENE-1: Metagenomic Foundation Model for Pandemic Monitoring | doi:; FGBERT: Function-Driven Pre-trained Gene Language Model for Metagenomics | doi:

## 本实例步骤描述
加载权重并进行长度过滤、分词和参考信息编码。
若选择 METAGENE-1 冻结表征分类路线，按论文 v1 §5.3 对最后层隐藏态取均值，再由下游逻辑回归消费表征；保持编码器冻结。将此路线与 §5.2 的 METAGENE-1 LoRA 微调区分，按任务明确选择，勿混用两种方法或用论文历史成绩代替本次结果。FGBERT 及其他模型仍须使用各自匹配的接口与来源。

## 本实例执行 prompt
加载{CHECKPOINT}和{REFERENCE_DB}，过滤短于{MIN_CONTIG_LENGTH}的序列并生成模型特征。
在执行原有动作前，先按输入槽核验模型身份与版本，明确长度过滤是否适用；仅在需要参考编码时加载可选参考库。对身份匹配下述固定版本的 METAGENE-1 冻结分支，依次执行：
1. 读取同 revision 的 config、tokenizer 配置、tokenizer 正文及权重索引，核对所有索引分片和实际本地路径；按既有[模型加载契约](../../../../../onescience-infer/references/phase_4_model_loading.md)记录 device、dtype、后端和 smoke-load 证据。示例 `metagene1.pt` 不证明它与官方分片等价；缺实物时保留已核验的接口说明，并如实标记加载未完成。
2. 使用配套 BPE；让 tokenizer 执行 `^` 替换为 `_` 的前缀处理、`Whitespace` 预分词和单序列末尾 `[EOS]` 模板，勿手动重复加前缀或 EOS。读取 `[PAD]=0`、`[EOS]=4`，记录 padding、特殊 token 和截断策略；以含特殊 token 的实际 token 数核对预算，勿把 bp 当 token。
3. 冻结编码器参数，设置 `eval()`，在 `no_grad()` 或 `inference_mode()` 中调用。作者 wrapper 使用 `AutoModel` 的 `last_hidden_state`，并删除输入中的 `token_type_ids`；按实际接口传参，若使用 CausalLM 则显式取得最后层 hidden states，勿将词表 logits 当表征。核验实际隐藏态为 `[batch, tokens, 4096]` 后，按质量门禁声明的政策池化并恢复输入行序。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=metagene1.pt
- {MIN_CONTIG_LENGTH} | required=False | type=int | var_name=最短序列长度 | hint=设置最短序列碱基数 | default=1000
- {REFERENCE_DB} | required=False | type=doc | var_name=参考数据库 | hint=参考数据库名称 | default=GTDB_R220
- 将上述默认值视为原场景示例，按当前输入绑定实际资源：`MIN_CONTIG_LENGTH` 以 bp 计，1000 bp 不是短读段任务的默认筛选要求；`REFERENCE_DB` 为可选参考编码依赖，不能代替必需的模型配置、tokenizer 与权重。
- 仅当 `{CHECKPOINT}` 核实为 `metagene-ai/METAGENE-1@ad8a1e0ee62b85058bfc05d823d8e8d4759edc48` 时，采用该版本配置：`architectures=[LlamaForCausalLM]`、32 层、32 个注意力头、`hidden_size=4096`、`vocab_size=1024`。配置的 `max_position_embeddings=512` 与 tokenizer 的 `model_max_length=512` 相符，作者 wrapper 也采用 512-token 上限；以此安排输入预算。并列存在的 `max_sequence_length=2048` 和 `rope_scaling=null` 不能证明可扩展上下文；不要据此直接启用 2048 token。换 revision 或模型时重新核对，勿继承本分支数值。

## 本实例产出
- 过滤后序列
- 序列表征
- 过滤统计
- 对冻结分支保存真实 `N×4096` 表征及逐行 `row_id` 对应关系，附模型/tokenizer revision、实际 shape、池化 mask、特殊 token 政策、过滤与截断统计，交给下游分类消费者。加载失败或无有效 token 的行保留失败/unknown 状态，勿填充伪向量；接口准备记录不等于已生成表征。

## 本实例质量门禁
- 过滤阈值已记录
- 参考版本可追溯
- 序列与样本映射保持
- 区分作者 wrapper 的 `last_hidden_state.mean(dim=1)` 与异长 padding 的工程适配：前者直接平均序列维，不能据此证明 padding 稳健。采用有效 token 均值时，明确 `z_i = sum_t(m_it * h_it) / sum_t(m_it)`，其中 `m` 由 `attention_mask` 与已声明的特殊 token 政策共同决定；排除 padding，分母为 0 则返回失败/unknown。
- 明确并固定 EOS 纳入或排除政策；`attention_mask` 本身不会排除 EOS，改变该政策会改变表征定义，须披露与作者直接均值的区别。用可手算矩阵先核对 mask 与零分母处理，再在真实权重就绪后检验单条、异长 batch、额外右 padding 及行序恢复的一致性，记录容差、实际维度和冻结状态；未执行时保留未验证。

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）
- 使用以下固定版本资料核对接口；这些是资料引用，不是新增 `edge:resource`，也不证明本地权重已取得。按索引检查 `model-00001-of-00006.safetensors` 至 `model-00006-of-00006.safetensors` 六个分片与同版配置/tokenizer 配套；索引 `total_size=25938640896` 字节表示 FP32 tensor 体积，不能当作峰值显存。另行核验文件可读性、完整性、实际运行 dtype、后端、设备内存与吞吐，勿由资料直接推断可运行。

| 资料 | 固定版本与定位 | SHA256（来源正文） |
|---|---|---|
| [METAGENE-1 论文](https://arxiv.org/html/2501.02045v1) | arXiv:2501.02045v1，§5.3 冻结表征/逻辑回归，§5.2 LoRA 边界 | `a426c77d137138cfc33410a1e54a1cce521007bdc9e3176f4774d0105424a7fe` |
| [Gene-MTEB README](https://raw.githubusercontent.com/metagene-ai/gene-mteb/cdfacab370d8ec49370a78d3ab283f6a27d98cf0/README.md) | commit `cdfacab370d8ec49370a78d3ab283f6a27d98cf0`，Example Using METAGENE-1 / LlamaWrapper | `958694f15eeab0a8cab2f51f71f54393658839e8c2295f2828a772e0dc00c5c4` |
| [config.json](https://huggingface.co/metagene-ai/METAGENE-1/raw/ad8a1e0ee62b85058bfc05d823d8e8d4759edc48/config.json) | revision `ad8a1e0ee62b85058bfc05d823d8e8d4759edc48`，架构、维度、长度与 dtype 字段 | `dc3751f8648b4ab24a3c0c42026267e1a2561b93249f54b460c0374e62d33f98` |
| [tokenizer_config.json](https://huggingface.co/metagene-ai/METAGENE-1/raw/ad8a1e0ee62b85058bfc05d823d8e8d4759edc48/tokenizer_config.json) | 同一 revision，model_max_length、tokenizer_class、特殊 token | `520cd0838fd728266a9791264e418a93cf10b019224faf8b5aed85d60bcea332` |
| [tokenizer.json](https://huggingface.co/metagene-ai/METAGENE-1/raw/ad8a1e0ee62b85058bfc05d823d8e8d4759edc48/tokenizer.json) | 同一 revision，BPE、normalizer、pre_tokenizer、post_processor | `3fd754434de0e3aa76ad233e1bcbe1562a21a91a4e13dda947fd7dce401f0b88` |
| [model.safetensors.index.json](https://huggingface.co/metagene-ai/METAGENE-1/raw/ad8a1e0ee62b85058bfc05d823d8e8d4759edc48/model.safetensors.index.json) | 同一 revision，metadata.total_size 与 weight_map | `a5957f6e6126ead8147acc48ee650770368c0ae2c86bbdd516fb041300149077` |

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
