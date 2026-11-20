## 执行流程

按本卡选择实现并形成可执行交接；参数来自调用方，官方来源及适用版本见 [spec.md](spec.md#source_refs)。保留 OneScience 的训练/推理职责，勿混用官方 Vortex 接口。

### 步骤 1: 选择实现与版本

- 输入：DNA/genome 任务、训练/推理目的、准确模型标识、上下文要求和执行约束。
- 动作：将 OneScience NeMo/Megatron 与官方 Evo2/Vortex 分开；官方按 CONFIG_MAP 绑定模型名/HF仓库/包内配置，明确 `evo2_7b` 与 `evo2_7b_base`。NeMo 选择 Mamba/Megatron 配置及并行布局。
- 输出：带来源、版本或捕获 hash 的分支选择与最小模型契约草案。
- 验证：任务所需长度与配置容量一致；不能由同名或提高 wrapper 上限推出等价。对照 spec.md 的官方映射与 NeMo 默认 8192 的适用条件。

### 步骤 2: 配对权重、配置与 tokenizer

- 输入：选定分支、本地/onestore 候选与调用方允许的获取方式。
- 动作：先核对已提供的本地/onestore 路径、配置内容、词表、checkpoint 格式/hash 和 revision；官方通过显式 local_path 加载匹配 `.pt`，NeMo 按 checkpoint 规格与并行切分构造。未认证候选如实记录；确需获取时参考官方 HF 仓库与 ArcInstitute README，冻结无网络任务不得隐式下载或安装。
- 输出：资源身份清单与来源/不确定性记录。
- 验证：配置/tokenizer/checkpoint 属于同一规格；NeMo distcp 与官方 `.pt` 不直接互换，转换另需配置、参数映射与数值等价证据。文件名与局部维度一致不算加载证明。

### 步骤 3: 构造并核验输入

- 输入：经上游规范化的序列或 FASTA、选定 tokenizer、长度/目标/采样 handoff。
- 动作：将 FASTA 转成所选接口的 token 张量，不把裸 FASTA 字符串直接送入 MambaModel。NeMo 使用源码 tokenizer/FASTA dataset 构造 tokens/position_ids；训练构造 tokens、position_ids、labels、loss_mask 四字段 batch。官方核对 UTF-8 字节 ID、[B,L]、BOS/padding、目标 mask 与位置偏移。
- 输出：张量契约、真实 token 长度、目标坐标/分母和独立生成前缀。
- 验证：对新数据检查 tokenizer round-trip（官方特殊 ID 还须保留原始 ID），NeMo 的 logits/labels/loss_mask sequence shape 对齐；官方 ASCII DNA 的字符/token 长度对应且不隐式截断，目标不进入生成输入。

### 步骤 4: 验证加载并交接前向接口

- 输入：分支契约、配对资源、实际隔离进程可见设备与依赖版本。
- 动作：核对设备/包/后端并保存探测；就绪时真实加载 checkpoint。NeMo 无 labels 调 forward，可建 get_inference_wrapper；训练复用 mamba_forward_step 或等价映射。官方按 usage.md 解包 forward 的 logits 与可选 embeddings，关闭非必要表征计算。将契约与来源落盘给 infer model_knowledge/loading plan，由 codegen 读取。
- 输出：加载日志、最小 loss/logits 验证及消费者知识文件引用。
- 验证：NeMo 并行组在构造前初始化，decoder_input 非空时 input_ids/position_ids 不参与 embedding；官方检查 [B,L,512] 和有限值。确认正式召回与下游实际收到所选分支；import、计划和文件存在均不代替真实加载/prefill。

### 步骤 5: 分离评分与生成状态

- 输入：已加载模型、允许前缀、独立目标及调用方长度/采样/容差。
- 动作：评分用因果移位和完整词表归一化，仅按目标 mask 聚合；长短对照各建独立状态。独立生成前按所选版本重建/重置 attention、Hyena/FIR 与 offset 等状态，只让允许前缀条件化；按 handoff 调用 generate 并核验 GenerationOutput。保存全长 prefill、状态贯穿、原始 logits/生成 ID 与采样记录。
- 输出：分开的评分结果、生成候选及各自执行证据。
- 验证：生成未接收目标或目标缓存，分块/强制提示未丢失条件，未把独立短窗口当完整上下文。核对 BOS 偏移、目标分母、采样参数和实际字母约束；状态生命周期无法核验则停止相关执行分支，不填造结果。

### 步骤 6: 核对产物与终态

- 输入：各分支实际日志、作业状态、原始产物与资源清单。
- 动作：分别报告知识供给、资源就绪、加载、prefill、评分与生成状态；保留失败/部分结果。训练继续规划分布式 runtime 和 checkpoint 保存，推理进入概率/生成/可选 embedding 后处理。
- 输出：可复核的计算或明确未执行记录、消费者交接和后续责任。
- 验证：结果来自真实执行；短测试/历史结果不替代完整终态；结论限定于计算范围，模型分数不等价于功能/表达/临床验证。

## 决策分支

- 若知识可供给而设备/依赖/资源未就绪，则保留契约并报告实际缺项，交环境/资源责任方；不要把某次历史探测写死为永久 BLOCKED。
- 若 NeMo 依赖版本不匹配，则对齐 NeMo/Megatron/BioNeMo；loss 异常先查 labels 与 loss_mask，不先改输出层。
- 若显存不足且原任务允许缩小范围，则缩短 sequence、减小 micro batch 或采用 checkpoint 原生并行配置；若固定长条件，则保留原长度要求并报告实际失败，不能将短型号/短窗口结果宣告为原任务成功。
- 若资源恢复，则依据真实预检进入可达模型分支；未就绪保留部分产物，不以空 token/空文件或自报成功替代模型执行。

## 不可跳过的约束

- 将实现、配置、tokenizer、checkpoint、并行布局和版本作为同一契约；OneScience 分支才使用 onescience.models.evo2 类与函数，官方分支才使用已核验的 Evo2/Vortex 原生入口。
- 不只提高 wrapper 长度；同时核对模型容量、真实状态和并行内存。官方 CUDA/可选 kernel 条件单独验证，不能由 GPU/DCU/DTK 名称类推。
- 保留 decoder_input 优先级、四字段训练 batch 与 loss_mask/label offset；生成与评分隔离状态及目标，记录全部 BOS/padding/截断策略。
- 区分官方模型完整词表概率与经过采样/白名单约束的分布；将模型似然与生成结果限制在模型证据范围内。
