## 何时使用本卡

- 当需要 DNA/genome token 的 logits、条件似然、续写或语言模型训练时，先查本卡选择实现分支；不直接接收蛋白 token、结构坐标或分子图。
- 当已有 OneScience Evo2/Mamba checkpoint 时，复用 NeMo/Megatron 训练/推理接口；当请求官方 `evo2_7b`、Vortex 或百万 token 上下文时，使用官方配置/权重/tokenizer 契约。短 `evo2_7b_base` 请求仍限于其 8K 规格。
- 用于实现、验证和调试；来源及版本条件见 [spec.md](spec.md#source_refs)，执行衔接见 [workflow_planning.md](workflow_planning.md)。

## 前置依赖

### execution_resources（OneScience NeMo/Megatron）

- 依赖 PyTorch、NeMo、Megatron Core、BioNeMo 及与 checkpoint 匹配的 tokenizer。
- 长序列和大参数模型通常需要 GPU/DCU；并行组必须在构造模型前初始化。
- checkpoint 的模型规模、词表、序列长度和并行切分必须与配置一致。

### 官方分支的运行条件

按 official-runtime 捕获版核对 Linux/有限 WSL2、CUDA 12.1+ 与兼容 NVIDIA 驱动、cuDNN 9.3+、C++17 编译器、Python 3.11/3.12；该版推荐 Torch 2.6.x/2.7.x。7B 可走无需 Transformer Engine 的 bf16 分支；`use_kernels=True` 的可选 Triton HC 内核要求 vtx>=1.1.0，启用后验证输出，不能把该条件推广到所有版本。[official-runtime, official-model]

先核对真实进程的设备可见性、包版本、权重格式/hash、配置与显存，再做加载和 prefill；DTK/GPU/DCU 目录或 import 成功不证明 Vortex CUDA 后端可用。多 GPU 的官方模型由 Vortex 放置，不要再整体 `.to(device)`。[official-model]

## 使用方式

本卡为接口与流程指南。按调用方 handoff 传递准确型号、长度、采样参数、容差和网络约束；下例中的 `verified_*`、`approved_*` 是预先核验的调用输入，不是本机资源就绪声明。

### 官方离线加载与 forward

```python
import torch
from evo2 import Evo2

# 先核实该权重与指定型号及包内 YAML 配套；不要省略 local_path 触发下载。
evo = Evo2(model_name=approved_model_name, local_path=verified_checkpoint_path,
           use_kernels=approved_use_kernels)
evo.model.eval()
ids = evo.tokenizer.tokenize(prefix_seq)
input_ids = torch.tensor(ids, dtype=torch.long, device=verified_input_device).unsqueeze(0)
logits, embeddings = evo(input_ids, return_embeddings=False)
assert embeddings is None
assert logits.shape == (1, len(ids), 512)
```

模型名、词表与长度条件见 spec.md；真实运行还需检查 finite logits、输入长度及加载日志。若请求 embedding，另传已核验层名；不为普通续写额外计算表征。[official-model]

### 官方生成与状态隔离

- 调用 `Evo2.generate(prompt_seqs=[prefix_seq], n_tokens=..., temperature=..., top_k=..., top_p=..., batched=..., cached_generation=..., force_prompt_threshold=...)`；所有值取自 handoff，记录实际配置、随机种子/随机状态及输出对象类型。[official-model]
- 该捕获版 Evo2.generate 的类型注解是旧 `Tuple`，实际直接转发 Vortex 输出；所核 Vortex 返回 `GenerationOutput(sequences, logits, logprobs_mean)`。按已安装版本检查这些字段，勿盲拆二元组。保存原始生成 ID、logits/采样证据并验证解码长度/字符；不要从有 clamp 的可见文本反推原始 ID。[official-generation, official-tokenizer]
- `cached_generation` 使用的不仅是 attention KV，还包括 hcl/hcm/hcs 的递归/FIR 状态与各自 `seqlen_offset`。评分与生成、不同前缀及长短对照各用独立状态；生成前按该版本重建/重置全部相关状态，只输入允许前缀，勿复用 teacher-forced 目标缓存。[official-generation]
- `force_prompt_threshold` 是保留提示顺序、逐步强制消费剩余提示的策略，不是丢弃前缀的短窗口；它不能保证任意设备可承载全长。若用底层 Generator，注意其 `max_seqlen` 分支会切取输入尾部，固定长条件任务必须显式排除这类截断。分块计算须验证状态贯穿全部条件 token，不能无状态滑窗冒充长上下文。[official-generation]
- `top_k/top_p` 只作概率筛选，不构成 ACGT 白名单；仅在调用契约要求时另行施加字母约束并记录归一化与采样轨迹。评分保留完整词表似然，生成报告实际约束分布；`logprobs_mean` 不自动等于留出目标评分。[official-generation, official-scoring]

### launch（OneScience NeMo/Megatron）

Evo2 在 OneScience 中是基于 NeMo/Megatron Mamba 的基因组语言模型。训练和推理代码应直接构造 `MambaModel`，批处理适配使用 `mamba_forward_step`，checkpoint、tokenizer 和并行配置由调用方传入。

```sh
python -c "from onescience.models.evo2.models.mamba import MambaModel, mamba_forward_step; import inspect; print(inspect.signature(MambaModel)); print(inspect.signature(MambaModel.forward)); print(inspect.signature(MambaModel.get_inference_wrapper)); print(inspect.signature(mamba_forward_step))"
```

### input_schema（OneScience NeMo/Megatron）

- `tokens`：整型 DNA token，形状通常为 `[batch, sequence_length]`。
- `position_ids`：与 `tokens` 同形状的位置编号。
- 训练还需要 `labels` 和 `loss_mask`；四个键必须同时出现在传给 `mamba_forward_step` 的字典中。
- 主要配置包括词表大小、隐藏维度、层数、状态空间参数、`sequence_length`，以及 tensor/pipeline/context parallel 大小。
- 推理输出为下一个 token 的 logits；带 `labels` 和 `loss_mask` 的训练调用返回模型计算的损失张量。
- DNA 字符表、大小写、BOS/EOD 与 padding 策略必须和 checkpoint 的 tokenizer 一致。

### runtime_interfaces（OneScience NeMo/Megatron）

- `MambaModel`：NeMo `GPTModel` 兼容封装，负责模型构建、训练与推理。
- `MambaModel.forward(input_ids, position_ids, attention_mask=None, labels=None, ..., loss_mask=None)`：核心前向接口。
- `MambaModel.get_inference_wrapper(...)`：创建 Megatron 推理包装器。
- `mamba_forward_step(model, batch)`：把标准训练 batch 映射为模型参数。
- `Evo2Tokenizer` 与 FASTA 数据集接口负责 DNA 文本到 token batch 的转换。

### main_functions（OneScience NeMo/Megatron）

- `mamba_forward_step`
- `MambaModel.forward`
- `MambaModel.get_inference_wrapper`

## 应用后的预期产物

- 交付实现/版本、模型名、权重与配置 hash、tokenizer/BOS/padding、张量形状、返回对象和状态生命周期组成的最小模型契约；落盘给 infer 的 model_knowledge/loading plan，并核验 codegen 实际消费的文件。
- 已执行时保存加载/prefill/评分/生成各自日志、输入长度与来源、目标 mask/分母、原始输出和作业终态；未执行时明确标记原因与未执行产物，不用知识已供给或短 smoke test 宣称完整任务成功。
- 训练进入分布式 runtime 和 checkpoint 保存；推理进入概率、生成或可选 embedding 后处理。保留以下操作边界。

### operation_limits（OneScience NeMo/Megatron）

- 该模型只接受基因组/DNA token，不接受蛋白质 token、结构坐标或分子图。
- logits 和序列似然是模型分数，不等价于变异致病性、表达量或临床结论。
- 生成长度受训练上下文窗口和推理显存限制；不能在不匹配的 tokenizer 之间复用 token id。

