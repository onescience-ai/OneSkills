# pretrain 接口完整模板

## 必要 import

```python
import os
import random
import numpy as np
import torch
import torch.distributed as dist
from functools import partial

from onescience.distributed.megatron.training import pretrain, get_args
from onescience.distributed.megatron.core import mpu
from onescience.distributed.megatron.training.arguments import core_transformer_config_from_args
from onescience.distributed.megatron.core.tensor_parallel.random import model_parallel_cuda_manual_seed
from onescience.distributed.pipelinetensorshapeconfig import PipelineTensorShapeConfig
```

---

## para_init()：初始化并行环境

```python
def para_init():
    if not torch.distributed.is_initialized():
        dist.init_process_group(backend="nccl")

    local_rank = int(os.environ["LOCAL_RANK"])
    torch.cuda.set_device(local_rank)

    seed = 2222
    args = get_args()
    config = core_transformer_config_from_args(args)

    model_parallel_cuda_manual_seed(seed)
    torch.manual_seed(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    return config
```

---

## model_provider

```python
def model_provider(pre_process=False, post_process=True):
    config = para_init()
    pp_rank = mpu.get_pipeline_model_parallel_rank()

    stages = {
        0: MyModel_stage0,
        1: MyModel_stage1,
        2: MyModel_stage2,
        3: MyModel_stage3,
    }

    stage_cls = stages.get(pp_rank)
    if stage_cls is None:
        raise ValueError(f"Unsupported pipeline rank: {pp_rank}")

    model = stage_cls(
        config=config,
        img_size=cfg.img_size,
        patch_size=cfg.patch_size,
        embed_dim=cfg.embed_dim,
        num_heads=cfg.num_heads,
    )

    # stage_shapes：前 num_stages-1 个 stage 的 forward 返回 tuple 的 shape
    # 与 forward 返回的 tuple 顺序严格对应，batch size 填实际值（通常为 1）
    B = 1  # pipeline micro-batch size = 1
    seq_full = H_out * W_out
    seq_half = (H_out // 2) * (W_out // 2)
    dim = cfg.embed_dim

    pp_config = PipelineTensorShapeConfig(
        num_stages=4,
        stage_shapes=[
            # stage0 → stage1: (x, skip, meta)
            [[B, seq_full, dim], [B, seq_full, dim], [3]],
            # stage1 → stage2: (x, skip, meta)，x 经过 downsample
            [[B, seq_half, dim * 2], [B, seq_full, dim], [3]],
            # stage2 → stage3: (x, skip, meta)，x 经过 upsample 恢复
            [[B, seq_full, dim], [B, seq_full, dim], [3]],
        ]
    )
    get_args().pipeline_tensor_shape_config = pp_config

    return model
```

---

## forward_step_func + loss_func

```python
def compute_loss(output, outvar):
    """
    output: 末 Stage forward 的返回值
    outvar:  标签，通过 partial 注入
    返回: (loss, num_tokens, metrics_dict)
    """
    loss = LpLoss()(outvar.cuda().float(), output)
    num_tokens = torch.tensor(1, device="cuda")
    reporting_loss = torch.cat([loss.clone().detach().view(1), num_tokens.view(1)])
    return loss, num_tokens, {'lm loss': reporting_loss}


def forward_step_func(data_iterator, model):
    # 1. 取数据（直接用 next，不要 try-except）
    data = next(data_iterator)
    invar  = data[0].cuda().float()   # 必须转 float32
    outvar = data[1].cuda().float()

    # 2. 前向（pipeline 框架负责跨 stage 调度）
    output = model(invar)

    # 3. 返回 (output, loss_func)
    #    loss_func 必须只接收 output，用 partial 提前绑定 outvar
    return output, partial(compute_loss, outvar=outvar)
```

### 多输出 loss（如 surface + upper_air）

```python
def compute_loss(output, outvar):
    out_surface, out_upper_air = output

    tar_surface   = outvar[:, :4, :, :].cuda().float()
    tar_upper_air = outvar[:, 4:, :, :].cuda().float()
    out_upper_air = out_upper_air.reshape(tar_upper_air.shape)

    loss = L1Loss()(tar_surface, out_surface) * 0.25 + L1Loss()(tar_upper_air, out_upper_air)

    num_tokens = torch.tensor(1, device="cuda")
    reporting_loss = torch.cat([loss.clone().detach().view(1), num_tokens.view(1)])
    return loss, num_tokens, {'lm loss': reporting_loss}
```

---

## train_valid_test_dataset_provider

```python
def train_valid_test_dataset_provider(train_val_test_num_samples):
    # 必须返回 Dataset 对象，不是 DataLoader！
    # 数据集的读取可以参考需改造模型的具体实现
    from onescience.datapipes.climate.cmems import CMEMSHDF5Dataset

    train_dataset = CMEMSHDF5Dataset(dataset=cfg_data.dataset, mode='train')
    val_dataset   = CMEMSHDF5Dataset(dataset=cfg_data.dataset, mode='val')
    test_dataset  = CMEMSHDF5Dataset(dataset=cfg_data.dataset, mode='test')

    return train_dataset, val_dataset, test_dataset
```

---

## pretrain 入口

```python
if __name__ == "__main__":
    # 必须在调用 pretrain 前设置
    train_valid_test_dataset_provider.is_distributed = True

    pretrain(
        train_valid_test_dataset_provider=train_valid_test_dataset_provider,
        model_provider=model_provider,
        model_type=None,                            # 必须为 None
        forward_step_func=forward_step_func,        # 注意：是 forward_step_func 不是 forward_step
        args_defaults={'dataloader_type': 'cyclic'} # 必须包含此项
    )
```

---

## 启动脚本示例（run.sh）

```bash
#!/bin/bash
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

NNODES=1
GPUS_PER_NODE=8
PP=4   # Pipeline Parallel size
TP=2   # Tensor Parallel size

torchrun \
    --nproc_per_node=$GPUS_PER_NODE \
    --nnodes=$NNODES \
    train.py \
    --pipeline-model-parallel-size $PP \
    --tensor-model-parallel-size $TP \
    --num-layers 24 \
    --hidden-size 1024 \
    --train-iters 100000 \
    --lr 1e-4 \
    --bf16 \
    "$@"
```

---

## 常见 pretrain 参数说明

| 参数 | 说明 |
|------|------|
| `--pipeline-model-parallel-size` | PP 并行度，等于 Stage 数量 |
| `--tensor-model-parallel-size` | TP 并行度，设为 1 时不需要 Distributed 模块 |
| `--dataloader-type cyclic` | 循环数据加载（也可通过 args_defaults 设置） |
| `--bf16` | 使用 BF16 混合精度（推荐） |
| `--recompute-granularity full` | 完整激活重计算，节省显存 |