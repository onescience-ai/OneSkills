## 核心结论

先按实现与 checkpoint 选择接口：OneScience NeMo/Megatron 分支使用 MambaModel；ArcInstitute Evo2/Vortex 分支使用 StripedHyena2 与官方 Evo2 封装。将选定分支的配置、权重、tokenizer 和状态契约一起交给推理实现，勿按同名模型互换接口。[official-map, official-model, official-weights]

### architecture_overview（OneScience NeMo/Megatron）

OneScience 的 NeMo/Megatron 路线以 `onescience.models.evo2.models.mamba.MambaModel` 为核心。该类继承 Megatron Core `GPTModel`，将 token embedding、Mamba decoder 与输出层组织为长序列语言模型；`Evo2StyleMCoreMambaModel` 扩展了带 `loss_mask` 的重加权训练损失，`mamba_forward_step` 定义训练 batch 到模型参数的标准映射。

### architecture_structure（OneScience NeMo/Megatron）

```text
FASTA or token records
  -> tokenizer / FASTA dataset
  -> input_ids + position_ids
  -> token embedding
  -> Mamba decoder stack
  -> output layer
  -> logits, or loss when labels are provided
```

训练时 `mamba_forward_step` 从 batch 读取 `tokens`、`position_ids`、`labels` 与 `loss_mask`；推理可通过 `get_inference_wrapper` 建立 Megatron inference wrapper。

## 适用条件

- 用于 DNA/genome 序列建模的训练或推理准备；先绑定实现版本、配置内容 hash、checkpoint 格式/内容 hash、来源 revision、tokenizer 和运行设备。文件名相同不足以认证权重。
- 官方分支的事实以 source_refs 的捕获 hash 为准；main URL 没有固定 commit，部署时另记实际 evo2/vtx 版本或 commit。HF config 的 revision 不代表 GitHub 源码版本，也不证明本地权重已加载。
- 容量规格不保证设备、依赖、显存或吞吐就绪；完整上下文必须经真实加载与 prefill 验证。官方 CUDA 路线与 OneScience 的 GPU/DCU 环境分别验证，不能由 DTK 或设备名称推定兼容。[official-runtime]

## 关键参数与公式

### 官方模型身份与容量

| 调用标识 | HF 仓库 | 随包配置 | 上下文 |
|---|---|---|---|
| `evo2_7b` | `arcinstitute/evo2_7b` | `configs/evo2-7b-1m.yml` | `max_seqlen=1048576` |
| `evo2_7b_base` | `arcinstitute/evo2_7b_base` | `configs/evo2-7b-8k.yml` | 8K，不能代替长型号 |

对照官方映射和所装包的 YAML 选择型号；1M 配置含 `vocab_size=512`、`hidden_size=4096`、`num_layers=32`、`max_batch_size=1`，并组合 hcs/hcm/hcl 与 attention 层。即使 YAML 的内部 `model_name` 含 8k，也须以调用标识、CONFIG_MAP、配置内容和配套权重共同判定，不能只看名字。[official-map, official-config, official-runtime]

### 官方输入与返回

- 构造 `Evo2(model_name, local_path=None, use_kernels=False)`；`local_path` 只指定权重，配置仍按 `model_name` 从包内选择。显式提供已验证本地路径以避免缺缓存时自动下载；官方 `.pt` 与 NeMo distcp 不直接互换。[official-model, official-weights]
- 使用 `CharLevelTokenizer(512)`：`tokenize` 返回 UTF-8 字节 ID；大写 A/C/G/T 为 65/67/71/84，`eod_id=eos_id=0`、`pad_id=1`。仅 ASCII DNA 且不额外加 BOS/padding 时，一碱基对应一 token；记录大小写、N/其他符号策略，勿把任意 Unicode 字符数当 token 数。[official-tokenizer]
- 将 token 转为整型 `input_ids[B,L]`，放到所选实现的输入设备；调用 `forward(input_ids, return_embeddings=False, layer_names=None)` 得到 `(logits, None)`，logits 为 `[B,L,512]`。若请求 embedding，先从实际模型确认 `layer_names`，返回 `(logits, embeddings_dict)`；普通评分/续写无需计算 embedding。[official-model]
- BOS/padding 由实际调用路径决定：scoring 的 `prepend_bos=True` 会前置 `eod_id`；不要假定 tokenizer 有独立 BOS 属性，调用前核对生成与评分实现。detokenize 有 clamp 行为，保留原始 ID，不能仅凭可见文本认证原始 token。[official-tokenizer, official-scoring, official-generation]

### 官方因果位置与目标 mask

按完整词表计算 `log_softmax(logits, dim=-1)`，用位置 `j-1` 的输出读取 token `x[j]` 的概率；无 BOS 的首 token 没有此前位置，padding 不参与目标。若只评估目标集合 M，按相同 token/BOS 坐标建立 mask，计算 `sum(log p(x[j] | x[:j]) for j in M) / |M|` 并保存逐 token 值及分母；不要把前缀计入目标平均。[official-scoring]

`score_sequences` 的 mean/sum 聚合针对整条输入的可评分序列，不是任意留出子区间指标；目标条件似然应从对齐的原始 logits 取出目标位置。评分使用完整 512 维词表归一化；生成时的 temperature/top-k/top-p 或字母白名单会改变采样分布，不能用其代替原模型似然。[official-scoring, official-generation]

### parameter_scale（OneScience NeMo/Megatron）

- `get_inference_wrapper` 的 `inference_max_seq_length` 默认是 `8192`。
- 层数、hidden size、state-space 与并行配置由 Megatron/Mamba config 决定。
- `HybridMambaConfig8BEvo2Loss` 是源码提供的配置类之一；实际构建必须以选择的配置和 checkpoint 为准。

### input_schema（OneScience NeMo/Megatron）

- `forward(input_ids, position_ids, attention_mask=None, labels=None, decoder_input=None, inference_context=None, packed_seq_params=None, inference_params=None, runtime_gather_output=None, loss_mask=None)`。
- 提供 `decoder_input` 时，`input_ids` 与 `position_ids` 被忽略。
- `mamba_forward_step` 期望 batch 至少包含 `tokens`、`position_ids`、`labels`、`loss_mask`。
- FASTA 输入需要先通过 `data/fasta_dataset.py` 与 `data/tokenizer.py` 转为模型张量。

### output_schema（OneScience NeMo/Megatron）

- `labels is None` 时返回底层模型输出，通常是 token logits 或配置指定的 hidden output。
- 提供 `labels` 时返回语言模型损失；Evo2 扩展实现会结合 `loss_mask` 计算重加权损失。
- inference wrapper 的返回协议由 Megatron Core wrapper 管理。

### shape_transformations（OneScience NeMo/Megatron）

1. DNA token ids 与 position ids 进入 embedding。
2. embedding 沿 sequence 维通过 Mamba decoder。
3. post-process 输出 vocabulary 维 logits。
4. 有 labels 时按 token 对齐计算损失，并由 `loss_mask` 排除无效位置。

### key_dependencies（OneScience NeMo/Megatron）

- `evo2_mamba`

### common_modification_points（OneScience NeMo/Megatron）

- 更换 tokenizer 或 vocabulary 时同步修改 embedding、输出层和 checkpoint。
- 调整上下文长度时同步检查数据切片、position ids、推理 wrapper 和并行内存。
- 训练代码复用 `mamba_forward_step` 的 batch 字段，避免自定义字段漂移。
- 推理代码根据 checkpoint 的并行配置构建模型，不把单卡假设写入模型资源。

## 常见误用

- 把 `evo2_7b_base`、NeMo MambaModel 或提高 wrapper 长度当成官方长模型 → 配置/状态不等价 → 核对分支、原生配置与真实长前缀状态。
- 将含留出目标的评分缓存交给生成 → 条件泄漏 → 为生成重建或经验证地重置全部相关状态，仅以允许前缀初始化；状态生命周期未核验时停止该执行分支。
- 将 `top_k=4` 当作 ACGT 白名单 → 四个高概率 ID 未必是 ACGT → 按调用契约单独实施约束并保存原始 ID 和实际采样分布。
- 将序列似然或生成成功表述为功能/临床结论 → 超出模型证据 → 保留科学验证边界，见 usage.md。

### implementation_risks（OneScience NeMo/Megatron）

- NeMo、Megatron Core、BioNeMo 与 checkpoint 版本需要匹配。
- `labels` 与 `loss_mask` 必须与 token 序列对齐；offset 错误会产生无效训练目标。
- `decoder_input` 分支会绕过 token embedding，错误同时传参可能掩盖输入问题。
- 超长序列的显存和并行需求由配置决定，不能只修改 wrapper 的最大长度。

## source_refs

官方增量来自已冻结的源码正文；下表 `sha256` 为捕获文本 hash，非权重 hash。main 不代表固定 commit；更新依赖时重核接口。usage.md 与 workflow_planning.md 复用以下来源标识。

| kid | uri | version | locator |
|---|---|---|---|
| official-map | https://raw.githubusercontent.com/ArcInstitute/evo2/main/evo2/utils.py | main 捕获; sha256:1f59e32e38cac3f20f8dc48a51041950184268eb4a0dbfa618316a9c5af3fc66 | HF_MODEL_NAME_MAP; CONFIG_MAP |
| official-config | https://raw.githubusercontent.com/ArcInstitute/evo2/main/evo2/configs/evo2-7b-1m.yml | main 捕获; sha256:9637f84ffd796f42cce3f926832b3999ff34a82686beba04505327162b288b1a | vocab_size; hidden_size; num_layers; max_seqlen; max_batch_size |
| official-model | https://raw.githubusercontent.com/ArcInstitute/evo2/main/evo2/models.py | main 捕获; sha256:0b757fcc42b37a52b0c3f508e876a52356331392ae8aa16a923576265043b78c | Evo2.__init__; forward; generate; load_evo2_model |
| official-tokenizer | https://raw.githubusercontent.com/Zymrael/vortex/main/vortex/model/tokenizer.py | main 捕获; sha256:32898671727d85b55bffae5e2eddf2b6c3f725292fe6dd064a8797b3ed4b1c03 | CharLevelTokenizer.__init__; tokenize; decode_token |
| official-weights | https://huggingface.co/arcinstitute/evo2_7b/raw/bda0089f92582d5baabf0f22d9fc85f3588f6b58/config.json | revision=bda0089f92582d5baabf0f22d9fc85f3588f6b58; sha256:7f2e195e156de678b6d7db090dca19b37e88671f72ea7c9e1866e103946b69b2 | architecture; _name_or_path |
| official-generation | https://raw.githubusercontent.com/Zymrael/vortex/main/vortex/model/generation.py | main 捕获; sha256:d39c1bb66b036f7e61c0ff4f44390c1b655661fc8cf7f9f4d8a4c7bceb4a1e4f | Generator.generate; GenerationOutput; generate |
| official-runtime | https://raw.githubusercontent.com/ArcInstitute/evo2/main/README.md | main 捕获; sha256:58787c8ef5cb4fba4c04322a4ceb9f174e2233ec22d4193622fb6bc67d651d89 | System requirements; FP8 requirements; model table |
| official-scoring | https://raw.githubusercontent.com/ArcInstitute/evo2/main/evo2/scoring.py | main 捕获; sha256:17e6985cef3a62c2a488133ab5a65050dcf0abeec2f55d1c0b068dfe37c44de6 | prepare_batch; logits_to_logprobs; _score_sequences |

### code_references（OneScience NeMo/Megatron）

- `{onescience_path}/onescience/src/onescience/models/evo2/models/mamba.py`
- `{onescience_path}/onescience/src/onescience/models/evo2/data/fasta_dataset.py`
- `{onescience_path}/onescience/src/onescience/models/evo2/data/tokenizer.py`
- `{onescience_path}/onescience/src/onescience/models/evo2/utils/config.py`

以上 OneScience 引用保留自基线资源卡；`{onescience_path}` 由调用环境解析，实际源码与依赖版本仍须在加载前核对。
