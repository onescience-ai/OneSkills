---
name: onescience-parallel
description: >
  将 PyTorch 模型改造为支持 Pipeline Parallelism (PP) + Tensor Parallelism (TP) 的分布式训练模型。
  适用场景：单机单卡模型改多卡分布式、模型拆分为多个 pipeline stage、替换 nn.Linear 为并行线性层、
  编写 forward_step_func / model_provider / dataset_provider、配置 PipelineTensorShapeConfig、
  创建 Distributed 版本模块（DistributedFuser / DistributedAttention / DistributedMlp）。
  当用户提到以下任何关键词时，务必使用此 skill：
  "流水线并行"、"pipeline parallel"、"模型并行改造"、"分布式训练"、"stage 拆分"、
  "ColumnParallelLinear"、"RowParallelLinear"、"pretrain 接口"、"forward_step_func"、
  "model_provider"、"TP 并行"、"张量并行"、"多卡训练"、"Megatron"。
---

# Pipeline Parallel 改造 Skill

## 重要原则（必读）

1. **复用 OneScience 模块**：所有基础模块必须使用 `onescience` 已有实现，禁止重复实现
2. **先读后写**：开始前必须阅读 `context.md` 和 `architecture.md`
3. **参考已有实现**：必须参考 `examples/earth/pangu_weather_distributed/` 的 pangu 实现
4. **保持参数一致性**：进行并行改造时，各 Stage 类的 `__init__` 参数签名和内部初始化逻辑应尽可能与原模型保持完全一致（如 `config`、`mask` 等参数的处理），避免随意更改参数名或逻辑。
5. **严禁循环导入**：在创建 Distributed 模块（如 `{StyleName}DistributedFuser`）时，**禁止**在模块内部导入 `OneFuser`、`OneTransformer` 等顶层包装类，因为这些包装类通常已经导入了你的 Distributed 模块，会导致 `ImportError`。应直接导入具体的子模块类（如 `from .{stylename}distributedlocalsiefuser import {StyleName}DistributedLocalSIEFuser`）。

---

## 改造三步流程

```
步骤1：模型拆分 (PP)  →  步骤2：TP 并行模块  →  步骤3：训练接口对接
```

---

## 步骤1：模型拆分（Pipeline Parallel）

### 1.1 切分策略

按前向执行顺序找**计算串行边界**，切点满足：
- 数据依赖最少（只有一个 tensor 出口）
- 跨 stage 传输的中间 tensor 尽量小
- 各 stage 计算量尽量均衡

典型 4-stage 切分（U-Net/Encoder-Decoder 结构）：

| Stage | 内容 | 说明 |
|-------|------|------|
| 0 | Embedding + Encoder 前半 | 首阶段，产生 skip connection |
| 1 | Downsample + 中间层 | 下采样后的计算密集区 |
| 2 | 解码层 + Upsample | 解码器前半段 |
| 3 | Decoder 后半 + Recovery | 消费 skip，产出最终结果 |

### 1.2 每个 Stage 的必要属性

```python
class MyModel_stageN(Module):
    def __init__(self, original_arg1, original_arg2, ..., megatron_config=None):
        """
        参数签名应尽可能与原模型保持一致。
        如果原模型第一个参数是 config (yaml配置)，则保持不变；
        额外传入的 Megatron 核心配置建议命名为 megatron_config 避免冲突。
        """
        super().__init__(meta=MetaData())

        # ① 必须有这三个属性，均设为None
        self.pre_process = None
        self.share_embeddings_and_output_weights = None
        self.input_tensor = None          # Stage 0 也要有

        # ② 必须初始化 config（Megatron get_model_config() 需要）
        # 使用传入的 megatron_config，若无则从 args 获取
        if megatron_config is None:
            args = get_args()
            megatron_config = core_transformer_config_from_args(args)
        self.config = megatron_config
        
        # ③ 保持原模型的初始化逻辑
        self.arg1 = original_arg1
        # ... 原模型的参数处理 ...

    def set_input_tensor(self, input_tensor):
        """Megatron pipeline 调度钩子，所有 Stage 都必须实现"""
        self.input_tensor = input_tensor
```

### 1.3 forward 方法规范

**Stage 0**（首阶段）：直接处理输入，不读 `input_tensor`
```python
def forward(self, x):
    x = self.embed(x)
    x = self.block1(x)
    skip = x
    meta = torch.tensor([B, Pl, Lat, Lon], device=x.device, dtype=x.dtype)
    return (x, skip, meta)   # 必须返回 tuple
```

**Stage 1/2**（中间阶段）：解包 input_tensor，原样透传 skip/meta
```python
def forward(self, x):
    if self.input_tensor is not None:
        # 必须处理 list 类型（recv_forward 返回 list）
        if isinstance(self.input_tensor, list):
            x, skip, meta = tuple(self.input_tensor)
        else:
            x, skip, meta = self.input_tensor
    x = self.process(x)
    return (x, skip, meta)   # skip/meta 原样透传
```

**Stage 3**（末阶段）：消费 skip，返回最终结果（不是 tuple）
```python
def forward(self, x):
    if self.input_tensor is not None:
        x, skip, meta = ...
    B = int(meta[0].item())   # 从 meta 恢复 shape
    x = torch.concat([x, skip], dim=-1)
    return self.recovery(x)   # 返回最终结果，不打包 tuple
```

### 1.4 关键细节

- **shape meta 必须是 tensor**，不能是 Python int（pipeline 通信只支持 tensor）
- **Pipeline 并行中 micro-batch size = 1**，不能使用动态 batch size
- **drop_path 必须基于总深度计算**，各 stage 取对应切片，保证权重可从原模型加载：
  ```python
  drop_path = np.linspace(0, 0.2, l1d + l2d + l3d + l4d).tolist()
  stage0_drop_path = drop_path[:l1d]   # 前 l1d 个
  stage1_drop_path = drop_path[l1d:l1d+l2d]
  ```
- **重计算层用 `checkpoint()` 包裹**节省显存

> 完整 Stage 代码模板 → 见 `references/stage_templates.md`

---

## 步骤2：TP 并行模块改造

### 2.1 检测哪些层需要 TP

从 Stage 类开始，逐层检查调用链，遇到以下模式需创建 Distributed 版本：

| 原始代码 | 替换方案 |
|---------|---------|
| `nn.Linear(in, out)` | `ColumnParallelLinear` 或 `RowParallelLinear` |
| `Mlp(in, hidden)` | `DistributedMlp(config=config)` |
| `nn.MultiheadAttention(...)` | 手动实现：qkv→Column，proj→Row |
| 调用含上述模式的模块 | 为该模块创建 Distributed 版本 |

### 2.2 创建 Distributed 模块的步骤

**通用命名规则**：`{ModuleStyle}Distributed{ModuleType}`
- `{ModuleStyle}`：原模块风格名（如 Pangu、Earth、Xihe 等）
- `{ModuleType}`：模块类型（Fuser、Transformer、Attention 等）

**创建步骤**（以 {StyleName 风格为例）：

1. 创建 `{StyleName}DistributedFuser` → `src/onescience/modules/fuser/{stylename}distributedfuser.py`
2. 创建 `{StyleName}DistributedTransformer` → `src/onescience/modules/transformer/`
3. 创建 `{StyleName}DistributedAttention` → `src/onescience/modules/attention/`
4. 在对应的 `onefuser.py` / `onetransformer.py` / `oneattention.py` 中注册

```python
# onefuser.py 注册示例
_FUSER_REGISTRY = {
    "{StyleName}Fuser": {StyleName}Fuser,                   # 原版本
    "{StyleName}DistributedFuser": {StyleName}DistributedFuser,  # Distributed 版本
}
```

### 2.3 config 传递链路（关键）

config 必须从 Stage 一路传递到每个并行层：

```
Stage(config)
  → OneFuser(style="{StyleName}DistributedFuser", config=config)
    → {StyleName}DistributedFuser(config=config)
      → OneTransformer(style="{StyleName}DistributedTransformer", config=config)
        → {StyleName}DistributedAttention(config=config)
          → ColumnParallelLinear(config=config)  ← 最终使用
          → RowParallelLinear(config=config)
        → DistributedMlp(config=config)          ← 最终使用
```

> 说明：将 `{StyleName}` 替换为实际模块风格名，如：`Pangu`、`Earth`、`Xihe` 等。

### 2.4 并行线性层使用规范

**MLP 模式（两层组合）**：
```python
self.fc1 = ColumnParallelLinear(
    input_size=in_features, output_size=hidden_features,
    config=config, bias=True,
    gather_output=False,       # 不聚合，传给 fc2
)
self.fc2 = RowParallelLinear(
    input_size=hidden_features, output_size=in_features,
    config=config, bias=True,
    input_is_parallel=True,    # 输入已按 TP 切分
)
# forward: x, _ = self.fc1(x); x, _ = self.fc2(x)
```

**单层使用**：
```python
# 需要完整输出时
self.proj = ColumnParallelLinear(..., gather_output=True)
# 或
self.proj = RowParallelLinear(..., input_is_parallel=False)
```

**input_is_parallel 关键规则**：
- 输入来自 `ColumnParallelLinear` → `input_is_parallel=True`
- 输入来自 `concat` 等非并行操作 → `input_is_parallel=False`

> 完整并行层参数说明 → 见 `references/parallel_linear.md`

---

## 步骤3：训练接口对接

必须使用框架导入：
```python
from onescience.distributed.megatron.training import pretrain, get_args
from onescience.distributed.megatron.core import mpu
from onescience.distributed.megatron.training.arguments import core_transformer_config_from_args
from onescience.distributed.pipelinetensorshapeconfig import PipelineTensorShapeConfig
```

### 3.1 model_provider

```python
def model_provider(pre_process=False, post_process=True):
    config = para_init()
    pp_rank = mpu.get_pipeline_model_parallel_rank()
    stages = {0: MyModel_stage0, 1: MyModel_stage1, 2: MyModel_stage2, 3: MyModel_stage3}
    model = stages[pp_rank](config=config, ...)

    # 配置跨 stage 通信 tensor 的 shape（必须与 forward 返回的 tuple 一一对应）
    pp_config = PipelineTensorShapeConfig(
        num_stages=4,
        stage_shapes=[
            # stage0→1: forward 返回 (x, skip) 的 shape
            [[1, seq_len, dim], [1, seq_len, dim]],
            # stage1→2
            [[1, seq_len//2, dim*2], [1, seq_len, dim]],
            # stage2→3
            [[1, seq_len, dim], [1, seq_len, dim]],
        ]
    )
    get_args().pipeline_tensor_shape_config = pp_config
    return model
```

**stage_shapes 填写规则**：
- 长度 = `num_stages - 1`（最后一个 stage 不发送）
- 每项 shape 与该 stage `forward` 返回 tuple 中各 tensor 严格对应
- batch_size 填实际值（通常为 1）

### 3.2 forward_step_func

```python
def forward_step_func(data_iterator, model):
    data = next(data_iterator)                  # 直接用，不要 try-except
    invar = data[0].cuda().float()             # 必须转 float32
    outvar = data[1].cuda().float()

    output = model(invar)

    def loss_func(output):                     # 通过闭包捕获 outvar
        loss = LpLoss()(outvar, output)
        num_tokens = torch.tensor(1, device="cuda")
        reporting_loss = torch.cat([loss.clone().detach().view(1), num_tokens.view(1)])
        return loss, num_tokens, {'lm loss': reporting_loss}

    return output, partial(loss_func)
```

**注意**：只有 pipeline 的第一个和最后一个 stage 实际需要数据，但 `forward_step_func` 中可以统一调用 `next(data_iterator)`，框架会处理数据分发。

### 3.3 dataset_provider

```python
def train_valid_test_dataset_provider(train_val_test_num_samples):
    # 必须返回 Dataset，不是 DataLoader
    train_dataset = MyDataset(mode='train')
    val_dataset   = MyDataset(mode='val')
    test_dataset  = MyDataset(mode='test')
    return train_dataset, val_dataset, test_dataset
```

### 3.4 pretrain 入口

```python
if __name__ == "__main__":
    train_valid_test_dataset_provider.is_distributed = True  # 必须设置

    pretrain(
        train_valid_test_dataset_provider=train_valid_test_dataset_provider,
        model_provider=model_provider,
        model_type=None,                          # 必须
        forward_step_func=forward_step_func,      # 注意参数名
        args_defaults={'dataloader_type': 'cyclic'}  # 必须
    )
```

---

## 重要补充约束

### 文件结构对应原则
> **与原模型文件结构一一对应**
>
> 原模型有 N 个模块文件，分布式就对应创建 N 个分布式模块文件：
>
> **例1：Pangu 模式（单文件）**
> ```
> 原文件: pangufuser.py          (1个文件)
> 分布式: pangudistributedfuser.py  (对应1个文件)
> ```
>
> **例2：Xihe 模式（多文件）**
> ```
> 原文件: xihefuse.py
>        xihelocalsiefuser.py      (共3个文件)
>        xiheglobalsiefuser.py
> ------------------------------------------------
> 分布式: xihedistributedfuser.py
>        xihedistributedlocalsiefuser.py  (对应3个文件)
>        xihedistributedglobalsiefuser.py
> ```
>
> **规则**：每个 `{StyleName}Xxx.py` 对应创建 `{StyleName}DistributedXxx.py`
>
> 所有分布式模块都要在对应的 registry 中注册。

### 训练脚本位置原则
> **参考原模型的训练脚本所在目录**，创建对应 `_distributed` / `_distributed_4stage` 子目录：
>
> ```
> examples/{domain}/
>   {model_name}/                    # 原训练脚本目录
>   {model_name}_distributed/        # 分布式训练脚本目录
>   {model_name}_distributed_4stage/ # 4阶段流水线训练脚本目录
> ```
>
> **例**：`examples/earth/pangu_weather/` → `examples/earth/pangu_weather_distributed_4stage/`

**原则8：Stage 类参数接口规范**

⚠️ **Stage 的 `__init__` 只接收标量参数 + `config`（megatron config），禁止传入 yaml config 对象！**

**错误做法**：
```python
class MyModel_stage0(Module):
    def __init__(self, yaml_cfg, img_size, ..., config=None):  # ❌ yaml_cfg 不应传入
```

**正确做法**：
```python
class MyModel_stage0(Module):
    def __init__(self, img_size, patch_size, embed_dim, num_heads, ..., config=None):  # ✅
```

**训练脚本 `build_model` 函数**：从 yaml 中提取标量后逐一传入，不传整个 cfg 对象：
```python
model = stage_cls(
    img_size=cfg_data.dataset.img_size,
    patch_size=cfg.patch_size,
    embed_dim=cfg.embed_dim,
    num_heads=cfg.num_heads,
    # ... 其他标量参数
    config=config,   # ✅ 只传 megatron config
)
```

**`{StyleName}DistributedFuser` 的 `num_heads` 接口规范**：

使用单个 `num_heads` 参数，所有子模块（local、global 等）共用，由 Stage 按 `num_heads[i]` 索引传入。禁止拆分为 `num_heads_local` / `num_heads_global` 等多个参数。

```python
# Stage 调用
OneFuser(style="{StyleName}DistributedFuser", num_heads=num_heads[i], ...)

# DistributedFuser 内部
class {StyleName}DistributedFuser(nn.Module):
    def __init__(self, ..., num_heads=8, ...):  # ✅ 单一参数
        self.local_blocks = ...Fuser(num_heads=num_heads, ...)
        self.global_blocks = ...Fuser(num_heads=num_heads, ...)
```

**强制约束**：`num_heads` 所有值必须能被 `tp_size` 整除。

---

**原则9：并行线性层返回值处理**

⚠️ **`ColumnParallelLinear` / `RowParallelLinear` 返回的是 tuple，不是 tensor！**

典型错误：
```python
TypeError: dropout(): argument 'input' (position 1) must be Tensor, not tuple
```

**错误写法**：
```python
x = self.proj_drop(self.proj(x))  # ❌ proj 返回 tuple，直接传 dropout
```

**正确写法**：
```python
x = self.proj(x)[0]               # ✅ 取 [0] 提取 tensor
x = self.proj_drop(x)
```

**强制性检测命令**：
```bash
# 检查所有 forward 中的调用
grep -n "\.proj(" src/onescience/modules/**/*.py
grep -n "RowParallelLinear\|ColumnParallelLinear" src/onescience/modules/**/*.py -A 1
```

| 检查点 | 要求 |
|--------|------|
| `self.proj(x)[0]` | ✅ 必须加 `[0]` |
| `self.fc1(x)[0]` | ✅ 必须加 `[0]` |
| 所有并行层调用后立即接 `[0]` | ✅ |

**原则9：DistributedFuser 参数接口统一原则**

⚠️ **`{StyleName}DistributedFuser` 必须使用单个 `num_heads` 参数，禁止拆分为 `num_heads_local` / `num_heads_global`！**

参考 `PanguDistributedFuser` 的接口规范：所有子模块（local、global）共用同一个 `num_heads`，由外部 Stage 按 `num_heads[i]` 索引传入。

**错误做法**：
```python
class XiheDistributedFuser(nn.Module):
    def __init__(self, ..., num_heads_local=6, num_heads_global=12, ...):  # ❌
        self.local_blocks = XiheLocalFuser(num_heads=num_heads_local, ...)
        self.global_blocks = XiheGlobalFuser(num_heads=num_heads_global, ...)
```

**正确做法**（与 PanguDistributedFuser 一致）：
```python
class XiheDistributedFuser(nn.Module):
    def __init__(self, ..., num_heads=6, ...):  # ✅ 单一参数
        self.local_blocks = XiheLocalFuser(num_heads=num_heads, ...)
        self.global_blocks = XiheGlobalFuser(num_heads=num_heads, ...)
```

**Stage 调用方式**（与 pangu_distributed_4stage 一致）：
```python
# stage0
OneFuser(style="XiheDistributedFuser", num_heads=num_heads[0], ...)
# stage1
OneFuser(style="XiheDistributedFuser", num_heads=num_heads[1], ...)
```

**强制约束**：`num_heads` 必须能被 `tp_size` 整除，config.yaml 中的 `num_heads` 所有值都必须满足此条件。

---

**原则9：Pipeline Parallel Stage 负载均衡原则**

⚠️ **OOM 90% 来自 stage 计算量不均衡！**

典型错误：
```
stage0: 1 个 Fuser (num_local=1)
stage1: 1 个 Fuser (num_local=2)
stage2: 2 个 Fuser (num_local=2) ❌ 是 stage0 的 4 倍！
stage3: 1 个 Fuser (num_local=1)
```

**均衡要求**：每个 stage 的计算量差异控制在 ±20% 以内

**强制性 Checklist**：
```bash
# 1. 统计每个 stage 的 Fuser 数量
grep -n "OneFuser" src/onescience/models/*_distributed*/*.py

# 2. 检查每个 Fuser 的 num_local / num_global
grep -n "num_local\|num_global" src/onescience/models/*_distributed*/*.py
```

**4 stage 通用负载均衡配置**：
| Stage | 计算量 | num_local / num_global |
|-------|--------|------------------------|
| stage0 | 输入 embedding + 第一个 Fuser | 统一 = 1 |
| stage1 | Downsample + 中间 Fuser | 统一 = 1 |
| stage2 | 中间 Fuser | 统一 = 1 |
| stage3 | Upsample + Skip connection + Recovery | 统一 = 1 |

**内存优化额外技巧**：
- ❌ 不要创建不必要的 tensor 副本：`x1 = x.contiguous(); x = x.contiguous()`
- ✅ 共享 tensor：`x = x.contiguous(); x1 = x`
- ✅ 所有 Fuser 都必须用 checkpoint

**原则10：MHA 内部完整张量并行原则**

⚠️ **仅把 proj 改成并行 = MHA 没有真正张量并行！**

**错误做法**（只改一半）：
```python
self.attn = nn.MultiheadAttention(...)  # ❌ 内部没有张量并行！
self.proj = RowParallelLinear(...)     # 只有这层并行
```

**正确做法**（参考 Pangu EarthDistributedAttention3D）：
```python
# Q, K, V 投影全部用 ColumnParallelLinear
self.q_proj = ColumnParallelLinear(dim, dim, config=config, ...)
self.k_proj = ColumnParallelLinear(dim, dim, config=config, ...)
self.v_proj = ColumnParallelLinear(dim, dim, config=config, ...)

# 输出用 RowParallelLinear
self.proj = RowParallelLinear(dim, dim, config=config, input_is_parallel=True, ...)

# 每个 rank 只算自己分到的 heads
self.num_heads_per_rank = self.num_heads // self.tp_size
```

**强制性 Checklist**：
```bash
# 检查是否还在用原生 MHA
grep -n "nn.MultiheadAttention" src/onescience/modules/**/*distributed*.py

# 检查 Q/K/V 是否都并行化了
grep -n "q_proj\|k_proj\|v_proj" src/onescience/modules/**/*distributed*.py
```

| 检查点 | 要求 |
|--------|------|
| `nn.MultiheadAttention` | ❌ 必须删除，不能在分布式模块中使用 |
| `q_proj = ColumnParallelLinear` | ✅ |
| `k_proj = ColumnParallelLinear` | ✅ |
| `v_proj = ColumnParallelLinear` | ✅ |
| `proj = RowParallelLinear(input_is_parallel=True)` | ✅ |
| `num_heads_per_rank` | ✅ 必须存在 |

**原则11：流水线张量传递原则**

⚠️ **流水线之间只传特征张量，不传非张量，不传可计算的信息！**

**核心思想**：跨 GPU 通信带宽是最宝贵的资源

**错误做法**：
```python
return (x, x1, mask1, mask2)  # ❌ 传 4 个 tensor
# mask1, mask2 都是确定性可计算的！不需要传！
```

**正确做法**：
```python
# stage0 -> stage1 -> stage2 -> stage3
# 所有 stage 之间只传 (x, x1) 两个特征张量
# mask 在每个 stage 内部根据分辨率计算
```

**优化前后对比**：
| | 传递张量数量 | 通信量比例 |
|---|-----------|-----------|
| 优化前 | 3-4 个 | 100% + 额外开销 |
| 优化后 | 2 个 | ~50% |

**强制性 Checklist**：
```bash
# 检查每个 stage 的 return 语句张量数量
grep -n "return " src/onescience/models/*_4stage/*.py

# 检查是否在传递 mask
grep -n "mask" src/onescience/models/*_4stage/*.py | grep "return\|input_tensor"
```

| 检查点 | 要求 |
|--------|------|
| 流水线传 mask | ❌ 绝对禁止 |
| 每个 stage 传特征数量 | 控制在 2-3 个以内 |
| 非张量跨 stage 传递 | ❌ 绝对禁止 |
| 可计算的信息（如分辨率、常数模式） | 本地计算，不传 |

⚠️ **致命陷阱1：模型和训练脚本不同步！**

```
模型 stage return (x, x1)                  ✅ 2 个张量
训练脚本 PipelineTensorShapeConfig:        ❌ 还写着 3-4 个张量！
```

**强制性同步检查**：
```bash
# 模型文件
grep "return (" src/onescience/models/*_4stage/*.py

# 训练脚本
grep -A5 "stage_shapes" examples/*/*_4stage/train*.py

# 两者张量数量必须一一对应！
```

⚠️ **致命陷阱2：不传 mask ≠ 改变 mask 逻辑！**

**错误做法**（本地逻辑变了）：
```python
# 为了"简化"，直接变成全1 mask
mask_coarse = torch.ones((H_out, W_out))  # ❌ 原模型逻辑被改变了！
```

**正确做法**（本地计算完全复现原逻辑）：
```python
# mask 不跨 stage 传递，但是每个 stage 内部完全复现原计算逻辑
self.mask_full = mask_full  # __init__ 时保存常量

def forward(self, x):
    mask2 = None
    if self.mask_full is not None:
        # ✅ 完全复现原模型的 change_mask 逻辑
        mask2 = self.change_mask(self.mask_full, x, h_out=H_out, w_out=W_out)
```

| 项目 | 要求 |
|------|------|
| 跨 stage 传递 mask | ❌ 禁止 |
| mask 计算逻辑 | ✅ 必须与原模型 100% 一致 |
| change_mask 函数 | ✅ 每个需要的 stage 都要有 |
| mask_full is None 判断 | ✅ 必须保留分支 |

⚠️ **致命陷阱3：mask_full 可能是字符串路径！**

**错误**：
```python
patch = mask_full[i*2:(i+1)*2, j*2:(j+1)*2]
# TypeError: string indices must be integers
# 因为 mask_full = "dataset/mask.npy" 是路径！
```

**正确**：所有用到 mask_full 的地方都必须先处理类型：
```python
if not torch.is_tensor(mask_full):
    if isinstance(mask_full, str):  # 路径字符串
        mask_full = np.load(mask_full)
    mask_full = torch.tensor(mask_full, dtype=torch.float32)
```

**强制检查**：
```bash
grep -n "isinstance.*str" src/onescience/models/*_4stage/*.py
# 必须每个 stage 都有字符串路径处理！
```

⚠️ **致命陷阱4：Module 签名严格校验！**

OneScience 的 `Module` 基类在 `__new__` 时会做**严格的参数绑定检查**：
```python
# Module.__new__ 中会执行：
bound_args = sig.bind_partial(*args, **kwargs)
# ❌ 只要有一个多余参数，就直接 TypeError!
```

**解决方案：所有 Stage 的 __init__ 必须加 **kwargs**：
```python
def __init__(
    self,
    config,
    img_size=(...),
    ...,
    megatron_config=None,
    **kwargs,  # ✅ 必须加！吸收所有多余参数
):
```

| 没有 **kwargs | 有 **kwargs |
|-------------|------------|
| ❌ 直接 TypeError | ✅ 参数静默吸收 |
| ❌ 训练脚本传新参数就崩 | ✅ 前向兼容 |

**强制检查**：
```bash
grep -A10 "class.*_stage" src/onescience/models/*/*.py | grep "**kwargs"
# 每个 Stage 都要有！
```

⚠️ **致命陷阱5：只有 stage0 需要读数据！其他 stage 会死锁！**

**90% 的人都会踩的坑！**

```python
# ❌ 错误写法：所有 stage 都在调用 next(data_iterator)
def forward_step_func(data_iterator, model):
    invar, outvar = next(data_iterator)  # ❌ stage1/2/3 卡在这里！
    output = model(invar)
```

**每个 stage 运行在独立进程中！它们都在试图读数据，但数据 iterator 是有状态的！**
stage0 读完数据后，stage1 就拿不到了，直接死锁！

**✅ 正确写法：**
```python
def forward_step_func(data_iterator, model):
    from onescience.distributed.megatron.core import parallel_state
```

---

**原则12：Fuser 模块 forward 方法统一接口规范**

⚠️ **Fuser 模块必须同时支持 dict 和 object 属性访问！**

**错误做法**（会导致 KeyError/AttributeError）：
```python
def forward(self, obj):
    if isinstance(obj, dict):
        x = obj["x"]
        mask = obj["mask"]  # ❌ KeyError if mask not present!
    else:
        x = obj.x
        mask = obj.mask     # ❌ AttributeError if mask not present!
    ...
    x = blk(x, mask)        # ❌ 子模块期望接收 dict！
```

**✅ 正确写法：**
```python
def forward(self, obj):
    if isinstance(obj, dict):
        x = obj["x"]
        mask = obj.get("mask")           # ✅ 安全获取，不存在返回 None
    else:
        x = obj.x
        mask = getattr(obj, 'mask', None) # ✅ 安全获取，不存在返回 None
        obj = {"x": x, "mask": mask}     # ✅ 统一转成 dict

    for blk in self.blocks:
        x = blk(obj)                      # ✅ 始终传递 dict 给子模块
        obj["x"] = x

    return x
```

**强制检查**：
```bash
grep -A15 "def forward.*obj" src/onescience/modules/fuser/*distributed*.py
# 检查是否使用了 .get() 和 getattr(..., None)
```

| 检查点 | 要求 |
|--------|------|
| `obj["mask"]` | ❌ 必须改成 `obj.get("mask")` |
| `obj.mask` | ❌ 必须改成 `getattr(obj, 'mask', None)` |
| `blk(x, mask)` | ❌ 必须改成 `blk(obj)` |
| 子模块调用 | ✅ 始终传递 dict 格式 |
    is_first_stage = parallel_state.is_pipeline_first_stage()

    if is_first_stage:
        # 只有 stage0 读真实数据
        invar, outvar = next(data_iterator)
        output = model(invar)
    else:
        # stage1/2/3 不传输入，由 set_input_tensor 负责
        output = model(None)
```

**配合每个 Stage 的 forward：**
| Stage | 写法 |
|-------|------|
| stage0 | `def forward(self, x):` 使用真实的 x |
| stage1/2/3 | `def forward(self, x=None):` **忽略 x，只用 input_tensor！** |

```python
# stage1/2/3 forward 第一行：
assert self.input_tensor is not None, "必须通过 set_input_tensor 设置!"
x, x1 = tuple(self.input_tensor)  # 从流水线前一阶段来的 tensor
```

### 模块调用链深度分析方法
从 Stage 类开始，**逐层追踪完整调用链**，画出模块依赖树，所有叶子节点都要检查：

```
MyModel_stageN
  ↳ OneFuser(style="MyDistributedFuser")
      ↳ MyDistributedFuser
          ↳ MyDistributedSubModuleA
              ↳ OneTransformer(style="...Distributed...")
              ↳ OneAttention(style="...Distributed...")  ✅ 都要并行
              ↳ OneMlp(style="...Distributed...")
```

**关键检查点**：
1. 所有含 `nn.Linear` 的子模块都要有分布式版本
2. 从 Stage 到最内层并行层，`config` 参数必须完整传递
3. 优先复用已有的 Earth/Pangu 分布式模块（如 TransformerBlock）

---

## 严格检测流程（必须执行，避免漏改）

### 第一步：文件级枚举检测

**必须运行此命令列出该模型的所有相关文件**：

```bash
# 1. 找出所有带模型名的源文件
find src -name "*{model_name}*.py" | sort
find examples -name "*{model_name}*" | sort

# 2. 通用检测命令示例（替换 {model_prefix} 为实际前缀）
ls src/onescience/modules/**/{model_prefix}*.py
ls src/onescience/modules/**/*{ModelPrefix}*.py
```

**检测结果必须做成对照表**（将 {Model} 替换为实际模型名）：
| 类型 | 原文件 | 分布式文件命名规范 | 是否已创建 |
|------|--------|------------------|-----------|
| Transformer | {model}transformer.py | {model}distributedtransformer*.py | ☐ |
| Fuser | {model}fuse*.py | {model}distributedfuser*.py | ☐ |
| Attention | {model}*attention.py | {model}distributed*attention.py | ☐ |
| MLP | {model}mlp.py | {model}distributedmlp.py | ☐ |

**命名规范：** 原文件名 + `distributed` + 可选后缀
- 例：`xihefeaturegroupattention.py` → `xihedistributedfeaturegroupattention.py`
- 例：`pangutransformer3d.py` → `pangudistributedtransformer3d.py`

> **违反此步骤后果：漏改文件**

### 第二步：调用链递归检测

**必须从 Stage 入口递归追踪所有调用**：

```
Stage 层入口
  ↳ 检查每个 OneFuser / OneAttention / OneMlp / OneTransformer
      ↳ 进入对应分布式模块的 __init__
          ↳ 检查内部所有子模块调用
              ↳ 是否都使用了 Distributed 版本？
              ↳ config 是否层层传递了？
```

**递归检测 checklist（必须逐项打勾）**：
- [ ] 所有 `OneTransformer(style="...")` 都使用分布式 style
- [ ] 所有 `OneAttention(style="...")` 都使用分布式 style
- [ ] 所有 `OneMlp(style="...")` 都使用分布式 style
- [ ] 所有 `Mlp()` 都替换为 `DistributedMlp()`
- [ ] 所有 `nn.Linear` 都替换为并行 Linear
- [ ] 每个分布式模块都接收 `config=None` 参数
- [ ] config 参数都传递到所有子模块调用

### 第三步：Registry 完整性检测

**必须检查所有 registry 文件**：
```bash
grep -l "_REGISTRY" src/onescience/modules/**/one*.py
```

| Registry 文件 | 分布式模块是否已注册 |
|--------------|---------------------|
| onetransformer.py | ✅ |
| oneattention.py | ✅ |
| onemlp.py | ✅ |
| onefuser.py | ✅ |

---

**检查清单**：
- [ ] ✅ **第一步：文件枚举检测，生成对照表**
- [ ] ✅ **第二步：调用链递归追踪，逐层检查**
- [ ] 为每个叶子节点创建 Distributed 版本
- [ ] 验证 config 在整个链路中正确传递
- [ ] ✅ **第三步：Registry 完整性检查**

---

## 改造检查清单

**Stage 拆分**
- [ ] 每个 Stage 包含 `pre_process=None`、`share_embeddings_and_output_weights=None`、`config`、`input_tensor`
- [ ] 每个 Stage 实现 `set_input_tensor`
- [ ] 首 Stage 不读 `input_tensor`（直接处理原始输入）
- [ ] 中间 Stage 解包后**原样透传** skip/meta
- [ ] 末 Stage 返回最终结果（非 tuple）
- [ ] shape meta 以 `torch.tensor` 传递，不用 Python int
- [ ] drop_path 切片与原模型保持一致
- [ ] 重计算层用 `checkpoint()` 包裹

**TP 并行**
- [ ] 所有 Distributed 模块已创建并注册到对应 One* 文件
- [ ] config 在整个调用链路中正确传递
- [ ] 两层组合：`gather_output=False` + `input_is_parallel=True`
- [ ] 单层独立：明确设置 `gather_output=True` 或 `input_is_parallel=False`
- [ ] concat 后的 tensor 使用 `input_is_parallel=False`

**训练接口**
- [ ] `stage_shapes` 与各 Stage `forward` 返回的 tensor shape 完全一致
- [ ] `dataset_provider` 返回 Dataset，不是 DataLoader
- [ ] `loss_func` 通过闭包/partial 捕获 label
- [ ] 数据转换为 `.float()`
- [ ] `is_distributed = True` 已设置
- [ ] `args_defaults={'dataloader_type': 'cyclic'}` 已配置

---

## 常见错误速查

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `_get_attr_wrapped_model couldn't find attribute config` | Stage 缺少 `self.config` | 所有 Stage 添加 config 初始化 |
| `mat1 and mat2 shapes cannot be multiplied` | `input_is_parallel` 设置错误 | concat 后的 tensor 用 `input_is_parallel=False` |
| `Input type (double) and bias type (c10::Half)` | 数据类型不匹配 | 加 `.float()` 转换 |
| `RuntimeError: list` 解包错误 | 未处理 list 类型的 `input_tensor` | 添加 `isinstance(self.input_tensor, list)` 判断 |

---

## 参考资料

- `references/stage_templates.md` — 完整 Stage 0/1/2/3 代码模板
- `references/parallel_linear.md` — 并行线性层详细参数和通信模式
- `references/train_interface.md` — pretrain 接口完整模板（model_provider / forward_step_func / dataset_provider）

**参考实现**（代码库中）：
- 模型：`src/onescience/models/pangu_distributed_4stage/`
- 训练：`examples/earth/pangu_weather_distributed/train_distributed_4stage.py`
- Distributed Fuser：`src/onescience/modules/fuser/pangudistributedfuser.py`
- Distributed Attention：`src/onescience/modules/attention/earthdistributedattention3d.py`