# 并行线性层使用指南

```python
from onescience.distributed.megatron.core.tensor_parallel.layers import (
    ColumnParallelLinear,
    RowParallelLinear,
)
from onescience.distributed.megatron.core.tensor_parallel import DistributedMlp
```

---

## 三种使用模式

### 模式一：两层组合（MLP / Attention Projection）最常见

通信开销最小，中间无需 all-gather/all-reduce。

```python
# 原始代码
self.fc1 = nn.Linear(in_features, hidden_features, bias=True)
self.fc2 = nn.Linear(hidden_features, in_features, bias=True)

# 替换后
self.fc1 = ColumnParallelLinear(
    input_size=in_features,
    output_size=hidden_features,
    config=config,
    init_method=init_method,
    bias=True,
    gather_output=False,       # 不聚合，局部输出直接传给 fc2
)
self.fc2 = RowParallelLinear(
    input_size=hidden_features,
    output_size=in_features,
    config=config,
    init_method=init_method,
    bias=True,
    input_is_parallel=True,    # 告知输入已按 TP 切分
    skip_bias_add=False,
)

# forward（返回 tuple，第二个是 bias）
def forward(self, x):
    x, _ = self.fc1(x)
    x, _ = self.fc2(x)
    return x
```

### 模式二：单层 ColumnParallelLinear（需要完整输出）

```python
self.proj = ColumnParallelLinear(
    input_size=in_features,
    output_size=out_features,
    config=config,
    bias=True,
    gather_output=True,   # 执行 all-gather，所有 rank 得到完整输出
)

# forward
x, _ = self.proj(x)
```

### 模式三：单层 RowParallelLinear（输入未切分）

```python
self.proj = RowParallelLinear(
    input_size=in_features,
    output_size=out_features,
    config=config,
    bias=True,
    input_is_parallel=False,  # 输入未切分，内部负责切分
    skip_bias_add=False,
)

# forward
x, _ = self.proj(x)
```

### 模式四：DistributedMlp（推荐用于 MLP 替换）

```python
from onescience.distributed.megatron.core.tensor_parallel import DistributedMlp

self.mlp = DistributedMlp(
    in_features=dim,
    hidden_features=mlp_hidden_dim,
    config=config,
)

# forward（接口与普通 Mlp 相同）
x = self.mlp(x)
```

---

## Attention 中的 TP 替换

```python
# 原始代码
self.qkv = nn.Linear(dim, 3 * dim)
self.proj = nn.Linear(dim, dim)

# 替换后
self.qkv = ColumnParallelLinear(
    input_size=dim,
    output_size=3 * dim,
    config=config,
    bias=True,
    gather_output=False,
)
self.proj = RowParallelLinear(
    input_size=dim,
    output_size=dim,
    config=config,
    bias=True,
    input_is_parallel=True,
)

# forward
def forward(self, x):
    B, N, C = x.shape
    qkv, _ = self.qkv(x)          # [B, N, 3*dim/tp]
    # 注意：dim 已被 TP 切分，需要按实际分片 dim 计算 heads
    tp_size = mpu.get_tensor_model_parallel_world_size()
    head_dim = self.head_dim
    num_heads = self.num_heads // tp_size
    qkv = qkv.reshape(B, N, 3, num_heads, head_dim).permute(2, 0, 3, 1, 4)
    q, k, v = qkv.unbind(0)
    attn = (q @ k.transpose(-2, -1)) * self.scale
    attn = attn.softmax(dim=-1)
    x = (attn @ v).transpose(1, 2).reshape(B, N, -1)
    x, _ = self.proj(x)
    return x
```

---

## 参数速查表

### ColumnParallelLinear

| 参数 | 值 | 含义 |
|------|-----|------|
| `gather_output` | `True` | 前向结束后 all-gather，所有 rank 得到完整输出 |
| `gather_output` | `False` | 每个 rank 只保留局部输出（与 RowParallel 组合时用） |
| `skip_bias_add` | `True` | 不在层内加 bias，将 bias 返回给调用方（用于融合优化） |

### RowParallelLinear

| 参数 | 值 | 含义 |
|------|-----|------|
| `input_is_parallel` | `True` | 输入已按 TP 切分（通常接在 ColumnParallel 之后） |
| `input_is_parallel` | `False` | 输入是完整的，内部切分后计算 |
| `skip_bias_add` | `True` | 不在层内加 bias，将 bias 返回给调用方 |

---

## 通信模式对比

```
模式一（两层组合）：1次通信
input(full) → Column(gather=False) → local_out → Row(parallel=True) → all-reduce → output(full)

模式二（Column 单层）：1次通信
input(full) → Column(gather=True) → all-gather → output(full)

模式三（Row 单层）：1次通信
input(full) → 切分 → Row(parallel=False) → all-reduce → output(full)
```

---

## input_is_parallel 判断规则（关键）

```python
# ✅ 正确：来自 ColumnParallel → input_is_parallel=True
x, _ = self.col_linear(x)          # x 是分片的
x, _ = RowParallelLinear(..., input_is_parallel=True)(x)

# ✅ 正确：来自 concat → input_is_parallel=False
x = torch.cat([x1, x2], dim=-1)    # concat 后不是并行的
x, _ = RowParallelLinear(..., input_is_parallel=False)(x)

# ❌ 错误：concat 后用 input_is_parallel=True 会导致维度错误
x = torch.cat([x1, x2], dim=-1)
x, _ = RowParallelLinear(..., input_is_parallel=True)(x)  # 报错！
```