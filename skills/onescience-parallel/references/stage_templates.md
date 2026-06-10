# Stage 代码模板

## Stage 0（首阶段：含 Embedding）

```python
import math
import numpy as np
import torch
import torch.nn as nn
from onescience.modules import OneEmbedding, OneFuser
from onescience.distributed.megatron.training import get_args
from onescience.distributed.megatron.training.arguments import core_transformer_config_from_args
from onescience.distributed.megatron.core.tensor_parallel import checkpoint
from physicsnemo.Module import Module
from physicsnemo.models.meta import MetaData


class MyModel_stage0(Module):
    def __init__(self, img_size, patch_size, embed_dim, num_heads, window_size, config=None):
        super().__init__(meta=MetaData())
        self.l1d = 4
        self.l2d = 8
        self.l3d = 8
        self.l4d = 4
        self.pre_process = None
        self.share_embeddings_and_output_weights = None
        self.input_tensor = None

        if config is None:
            args = get_args()
            config = core_transformer_config_from_args(args)
        self.config = config

        # drop_path 基于总深度计算，保证权重可从原模型加载
        drop_path = np.linspace(0, 0.2, self.l1d + self.l2d + self.l3d + self.l4d).tolist()

        H_out = math.ceil(img_size[0] / patch_size[0])
        W_out = math.ceil(img_size[1] / patch_size[1])

        # Embedding 只在 Stage 0 初始化
        self.patchembed = OneEmbedding(
            style="MyModelEmbedding",
            img_size=img_size,
            patch_size=patch_size,
            embed_dim=embed_dim,
        )

        # 使用 Distributed Fuser（TP > 1 时）
        self.layer1 = OneFuser(
            style="MyModelDistributedFuser",   # Distributed 版本
            dim=embed_dim,
            input_resolution=(H_out, W_out),
            depth=self.l1d,
            num_heads=num_heads,
            window_size=window_size,
            drop_path=drop_path[:self.l1d],    # 取前 l1d 个
            config=config,                     # 传递 config
        )

    def set_input_tensor(self, input_tensor):
        self.input_tensor = input_tensor

    def forward(self, x):
        # Stage 0 直接处理原始输入
        x = self.patchembed(x)
        B, N, C = x.shape
        H_out = int(math.sqrt(N))
        W_out = H_out

        x = checkpoint(self.layer1, False, x)

        skip = x  # 保存 skip connection

        # shape meta 必须是 tensor（pipeline 通信不支持 Python int）
        meta = torch.tensor([H_out, W_out, C], device=x.device, dtype=x.dtype)

        return (x, skip, meta)  # 必须返回 tuple
```

---

## Stage 1（中间阶段：含 Downsample）

```python
class MyModel_stage1(Module):
    def __init__(self, img_size, patch_size, embed_dim, num_heads, window_size, config=None):
        super().__init__(meta=MetaData())
        self.l1d = 4
        self.l2d = 8
        self.l3d = 8
        self.l4d = 4
        self.pre_process = None
        self.share_embeddings_and_output_weights = None
        self.input_tensor = None

        if config is None:
            args = get_args()
            config = core_transformer_config_from_args(args)
        self.config = config

        drop_path = np.linspace(0, 0.2, self.l1d + self.l2d + self.l3d + self.l4d).tolist()

        H_out = math.ceil(img_size[0] / patch_size[0])
        W_out = math.ceil(img_size[1] / patch_size[1])

        # 只初始化本 stage 需要的层
        self.downsample = OneSample(style="MyModelDownSample", ...)
        self.layer2 = OneFuser(
            style="MyModelDistributedFuser",
            dim=embed_dim * 2,
            input_resolution=(H_out // 2, W_out // 2),
            depth=self.l2d,
            drop_path=drop_path[self.l1d:self.l1d + self.l2d],  # 取对应切片
            config=config,
        )

    def set_input_tensor(self, input_tensor):
        self.input_tensor = input_tensor

    def forward(self, x):
        # 中间 Stage：从 input_tensor 解包（必须处理 list 类型）
        if self.input_tensor is not None:
            if isinstance(self.input_tensor, list):
                x, skip, meta = tuple(self.input_tensor)
            else:
                x, skip, meta = self.input_tensor

        x = self.downsample(x)
        x = checkpoint(self.layer2, False, x)

        # skip 和 meta 原样透传，直到被末 Stage 消费
        return (x, skip, meta)
```

---

## Stage 2（中间阶段：含 Upsample）

```python
class MyModel_stage2(Module):
    def __init__(self, img_size, patch_size, embed_dim, num_heads, window_size, config=None):
        super().__init__(meta=MetaData())
        self.l1d = 4
        self.l2d = 8
        self.l3d = 8
        self.l4d = 4
        self.pre_process = None
        self.share_embeddings_and_output_weights = None
        self.input_tensor = None

        if config is None:
            args = get_args()
            config = core_transformer_config_from_args(args)
        self.config = config

        drop_path = np.linspace(0, 0.2, self.l1d + self.l2d + self.l3d + self.l4d).tolist()

        H_out = math.ceil(img_size[0] / patch_size[0])
        W_out = math.ceil(img_size[1] / patch_size[1])

        self.layer3 = OneFuser(
            style="MyModelDistributedFuser",
            dim=embed_dim * 2,
            input_resolution=(H_out // 2, W_out // 2),
            depth=self.l3d,
            drop_path=drop_path[self.l1d + self.l2d:self.l1d + self.l2d + self.l3d],
            config=config,
        )
        self.upsample = OneSample(style="MyModelUpSample", ...)

    def set_input_tensor(self, input_tensor):
        self.input_tensor = input_tensor

    def forward(self, x):
        if self.input_tensor is not None:
            if isinstance(self.input_tensor, list):
                x, skip, meta = tuple(self.input_tensor)
            else:
                x, skip, meta = self.input_tensor

        x = checkpoint(self.layer3, False, x)
        x = self.upsample(x)

        return (x, skip, meta)  # skip/meta 继续透传
```

---

## Stage 3（末阶段：消费 skip，产出最终结果）

```python
class MyModel_stage3(Module):
    def __init__(self, img_size, patch_size, embed_dim, num_heads, window_size, config=None):
        super().__init__(meta=MetaData())
        self.l1d = 4
        self.l2d = 8
        self.l3d = 8
        self.l4d = 4
        self.pre_process = None
        self.share_embeddings_and_output_weights = None
        self.input_tensor = None

        if config is None:
            args = get_args()
            config = core_transformer_config_from_args(args)
        self.config = config

        drop_path = np.linspace(0, 0.2, self.l1d + self.l2d + self.l3d + self.l4d).tolist()

        self.layer4 = OneFuser(
            style="MyModelDistributedFuser",
            dim=embed_dim,
            depth=self.l4d,
            drop_path=drop_path[-self.l4d:],   # 取最后 l4d 个
            config=config,
        )

        # Recovery 只在末 Stage 初始化
        self.recovery = OneRecovery(style="MyModelRecovery", ...)

    def set_input_tensor(self, input_tensor):
        self.input_tensor = input_tensor

    def forward(self, x):
        if self.input_tensor is not None:
            if isinstance(self.input_tensor, list):
                x, skip, meta = tuple(self.input_tensor)
            else:
                x, skip, meta = self.input_tensor

        # 从 meta 恢复 shape 信息
        H_ = int(meta[0].item())
        W_ = int(meta[1].item())
        C  = int(meta[2].item())

        x = checkpoint(self.layer4, False, x)

        # 消费 skip connection
        x = torch.concat([x, skip], dim=-1)

        # 最终 recovery
        output = self.recovery(x)

        # 末 Stage 直接返回结果，不打包 tuple
        return output
```

---

## 注意事项

### drop_path 切片对照表（4-stage，总深度 = l1d+l2d+l3d+l4d）

| Stage | drop_path 切片 |
|-------|--------------|
| 0 | `drop_path[:l1d]` |
| 1 | `drop_path[l1d:l1d+l2d]` |
| 2 | `drop_path[l1d+l2d:l1d+l2d+l3d]` |
| 3 | `drop_path[-l4d:]` |

### Pipeline micro-batch size = 1

Pipeline 并行中 micro-batch size 始终为 1，所有 shape 中的 batch 维固定为 1：
```python
# ❌ 错误：动态 batch size
B = x.shape[0]
mask = mask.repeat(B, 1, 1, 1)

# ✅ 正确：固定为 1
mask = mask.unsqueeze(0).unsqueeze(0)  # shape: [1, 1, H, W]
```