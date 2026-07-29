# GPU 显存溢出（OOM）预防与恢复策略

当推理/训练任务涉及 GPU 且预期可能触发显存溢出时，读取本文件。本文件覆盖**任务进程内**的 GPU OOM 处理，与 SLURM 调度层的 CPU 内存 OOM（由 `onescience-runtime/references/slurm-resource-retry.md` 处理）互补。

## 1. 触发信号识别

从以下证据中识别 GPU OOM：

- 进程 stderr：`OutOfMemoryError`、`CUDA out of memory`、`RuntimeError: CUDA error`、`XLA memory allocation failed`
- JAX 特有：`RESOURCE_EXHAUSTED`、`BFCAllocator`、`LargestFreeBlock: 0B`
- PyTorch 特有：`torch.cuda.OutOfMemoryError`、`Tried to allocate`
- TensorFlow 特有：`OOM when allocating tensor`、`Could not allocate`
- 作业日志中模型加载阶段成功但推理/物化阶段失败，且失败前显存使用接近上限

## 2. 预执行显存预算估算

在执行推理/训练前，根据任务特征估算 GPU 显存需求：

### 2.1 模型权重显存

```
model_memory = 参数量 × 每个参数的字节数
```

| 精度 | 字节/参数 |
|------|----------|
| float32 | 4 |
| float16/bfloat16 | 2 |
| int8 | 1 |

若模型权重已存储在磁盘上，检查文件大小作为验证：
```bash
du -sh <checkpoint_path>
```

### 2.2 输入数据显存

```
input_memory = batch_size × sequence_length × hidden_dim × bytes_per_element
              + token_embedding_memory（如氨基酸编码、核苷酸编码表）
```

对于 AlphaFold 3 等蛋白质结构预测任务：
```
input_memory ≈ num_tokens × token_dim × 4（float32）+
               num_tokens × num_msa × msa_dim × 4 +
               pair_representation_memory
```

### 2.3 中间激活显存

```
activation_memory ≈ 模型推理中间张量大小，通常为模型权重的 2-5 倍
```

对于蛋白质结构预测（如 AlphaFold 3），recycles 数量是主要影响因素：
```
activation_memory ≈ base_activation × (1 + num_recycles × recycle_overhead_factor)
```

### 2.4 结果物化显存

推理完成后，将设备端输出转换为 CPU 端数据结构（如 `np.asarray(tensor)`、`.cpu().numpy()`）会临时额外分配内存。这部分内存峰值可能接近或超过推理阶段的内存：

```
materialization_memory ≈ output_tensor_size × materialization_overhead
```

材料化开销系数通常为 **1.5-2.5×**（取决于框架的拷贝/转换策略）。

### 2.5 总预算

```
total_estimated = model_memory + input_memory + activation_memory + materialization_memory
```

### 2.6 安全边际

**单卡维度**：

| 总估算 / 单卡可用显存 | 风险等级 | 操作 |
|---|---|---|
| < 60% | 低风险 | 正常执行 |
| 60% - 80% | 中风险 | 启用内存优化参数 |
| 80% - 95% | 高风险 | 必须使用低内存配置 |
| > 95% | 单卡超限 | 进入多卡聚合判断（见 2.8） |

**多卡聚合维度**（见 2.8）：当单卡超限时，不立即阻断；先判断多卡并行是否能覆盖需求。

### 2.7 可用显存查询

```bash
# 查询所有 GPU 的总显存和空闲显存
nvidia-smi --query-gpu=index,name,memory.total,memory.free --format=csv,noheader

# 或在 Python 中
python -c "import torch; [print(f'GPU {i}: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.1f} GiB total, {torch.cuda.memory_reserved(i) / 1024**3:.1f} GiB reserved') for i in range(torch.cuda.device_count())]"
```

### 2.8 多卡聚合判断 —— 多 seed 并行

当单卡显存估算 > 95%（单卡超限）时，不立即阻断。先判断任务是否支持多 seed 并行，以及多卡聚合后是否能覆盖需求。

**适用任务类型**：
- 蛋白质结构预测（AlphaFold 3、ESMFold 等）：支持 `num_seeds` 参数，每个 seed 是独立推理任务
- 生成式模型推理（扩散模型、自回归模型）：支持多 sample 并行
- 任何具有独立随机种子的推理任务

**聚合算法**：

```
# 步骤 1：计算每张卡的可用显存
per_gpu_memory = [gpu.free_memory for gpu in idle_gpus]

# 步骤 2：任务单次推理显存需求（使用最低内存配置）
task_memory_low = model_memory + input_memory + base_activation × 1.3  # num_recycles=1
                  + materialization_memory × 0.5                        # 分段物化，折半

# 步骤 3：判定每张卡是否能容纳一个任务
feasible_gpus = [gpu for gpu in idle_gpus if gpu.free_memory > task_memory_low]

# 步骤 4：计算可并行的 seed 数量
max_parallel_seeds = len(feasible_gpus)

# 步骤 5：决策
if max_parallel_seeds == 0:
    → 所有卡都不够单任务最低需求 → 阻断，blocking_reason=gpu_oom_all_gpus_insufficient
elif max_parallel_seeds == 1:
    → 仅 1 张卡可行 → 单卡执行，num_seeds=1
else:
    → 多卡可行 → num_seeds = max_parallel_seeds
    → 每张卡跑 1 个 seed，通过 CUDA_VISIBLE_DEVICES 隔离
```

**聚合决策表**：

| 条件 | 决策 | num_seeds | 调度方式 |
|------|------|-----------|---------|
| 单卡满足 | 单卡执行 | 用户指定或默认 1 | `CUDA_VISIBLE_DEVICES=0` |
| 单卡不满足，N 张卡满足 | 多卡多 seed | N（使用全部可行 GPU） | 每卡 1 seed，`CUDA_VISIBLE_DEVICES=i` |
| 所有卡都不满足最低需求 | 阻断 | — | `blocking_reason=gpu_oom_all_gpus_insufficient` |

**关于 seed 数量上限**：
- 多 seed 并行通过 `CUDA_VISIBLE_DEVICES` 隔离，每个进程完全独立，**不存在技术上的并发上限**
- `num_seeds` 直接等于可行 GPU 数量，不做人为截断（如 8 或其它固定值）
- AlphaFold 3 等模型在更多 seed 下可获得更好的采样多样性，seed 数量越多结果越稳定
- 若用户通过 CLI 显式指定了 `--num_seeds` 或 `--seed`，以用户值为准，不自动覆盖

**关键约束**：
- 多 seed 并行时，每个 seed 是**完全独立**的推理任务，不存在跨卡通信，因此不需要 NCCL/torchrun
- 使用 shell 层面的 `CUDA_VISIBLE_DEVICES=i` 隔离，每个进程只看到 1 张卡
- 每个 seed 的结果独立保存到 `<output_dir>/seed_<i>/`
- 全部 seed 完成后，取最优结果（按模型置信度分数排序）或合并所有结果

**示例——AlphaFold 3 7PNM 案例**：

```
单卡估算：138 GiB / 83 GiB = 166% → 单卡超限
最低配置估算：17 + 0 + 17×1.3 + 35 = 74 GiB / 83 GiB = 89% → 单卡可容纳
空闲 GPU：8 张 × 83 GiB
决策：num_seeds = min(8, 8) = 8
调度：CUDA_VISIBLE_DEVICES=0 python run_af3.py --seed=1 &
      CUDA_VISIBLE_DEVICES=1 python run_af3.py --seed=2 &
      ...
      CUDA_VISIBLE_DEVICES=7 python run_af3.py --seed=8 &
      wait
```

## 3. 自动参数降级策略

当 OOM 发生或预执行估算为高风险时，按以下优先级自动降级参数：

### 3.1 AlphaFold 3 类蛋白质结构预测

| 优先级 | 参数 | 降级方向 | 说明 |
|--------|------|---------|------|
| 1 | `num_recycles` | 减少（10→5→3→1） | 回收次数是显存占用的最大影响因素 |
| 2 | `num_seeds` | 多卡分散（见 2.8）而非减少 | 单卡不满足时通过多 seed 并行利用多卡，不降低 seed 数量 |
| 3 | `chunk_size` / `max_extra_msa` | 减少 | 缩小 MSA 块大小 |
| 4 | `use_gpu_relax` | 关闭 | CPU 弛豫节省 GPU 显存 |
| 5 | `flash_attention` | 开启 | Flash Attention 节省显存 |

### 3.2 通用深度学习推理

| 优先级 | 参数 | 降级方向 | 说明 |
|--------|------|---------|------|
| 1 | `batch_size` | 减半 | 最直接有效的策略 |
| 2 | `sequence_length` / `max_tokens` | 分段处理 | 长序列切分为短段 |
| 3 | 精度 | float32 → float16/bfloat16 | 混合精度节省约 50% 显存 |
| 4 | `gradient_checkpointing` | 开启 | 节省激活显存（如适用） |
| 5 | 模型并行 | 切换到多卡 | 模型分片到多张卡 |

### 3.3 结果物化策略

当推理成功但结果物化 OOM 时：

1. **分批物化**：将大张量按维度切分后分别调用 `.cpu().numpy()`
   - 对于形状为 `[N, D]` 的张量，按 `N` 维度切分为多块
   - 每块大小不超过可用显存的 30%
2. **直接保存到磁盘**：跳过 Python 内存中转，使用 `torch.save()` 或 `np.save()` 直接落盘
3. **降低输出精度**：float32 → float16 保存，减少一半内存

## 4. OOM 重试机制

### 4.1 重试预算

- GPU OOM 最大自动重试 **2 次**（每个降级级别一次）
- 每次重试前必须清理 GPU 显存
- 若 2 次重试后仍 OOM，停止并报告 `blocking_reason=gpu_oom_retry_exhausted`

### 4.2 GPU 显存清理

每次重试前执行：

```bash
# 1. 杀除残余 Python 进程
pkill -f python 2>/dev/null; sleep 2

# 2. 清理 JAX/XLA 编译缓存（JAX 特有）
rm -rf /tmp/jax_cache_* ~/.jax_cache 2>/dev/null

# 3. 清理 PyTorch CUDA 缓存
python -c "import torch; torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()" 2>/dev/null

# 4. 检查 GPU 状态
nvidia-smi --query-gpu=index,memory.used,memory.free --format=csv,noheader
```

### 4.3 重试证据记录

每次重试前，记录到 `evidence.execute.gpu_oom_retries`：

```json
{
  "retry_count": 1,
  "previous_params": {"num_recycles": 10, "batch_size": 4},
  "adjusted_params": {"num_recycles": 5, "batch_size": 2},
  "gpu_state_before": {"gpu_0": {"total_gib": 85, "free_gib": 12}},
  "adjustment_reason": "previous OOM at model materialization stage"
}
```

## 5. 内存碎片化处理

### 5.1 BFC 分配器问题

JAX/TensorFlow 的 BFC (Best-Fit with Coalescing) 分配器在长时间运行后会出现严重的内存碎片化，表现为 `LargestFreeBlock: 0B` 但 `memory.free > 0`。

**处理策略**：

1. **强制使用默认分配器**（禁用 BFC）：
   ```bash
   export XLA_PYTHON_CLIENT_ALLOCATOR=platform  # JAX
   export TF_GPU_ALLOCATOR=cuda_malloc_async     # TensorFlow
   ```

2. **降低显存预分配比例**：
   ```bash
   export XLA_PYTHON_CLIENT_MEM_FRACTION=0.7   # JAX: 仅预分配 70% 显存
   export TF_FORCE_GPU_ALLOW_GROWTH=true        # TensorFlow: 按需增长
   ```

3. **PyTorch 内存管理**：
   ```python
   import os
   os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
   # 或在代码中
   torch.cuda.set_per_process_memory_fraction(0.8)
   ```

### 5.2 JAX 编译缓存

JAX 会在 `/tmp/` 持久化编译缓存，长时间累积可能导致磁盘和内存碎片：
```bash
# 清理旧缓存（保留最近 24 小时的编译产物）
find /tmp/jax_cache_* -type f -mtime +1 -delete 2>/dev/null
```

## 6. 调度策略集成

### 6.1 优先选择空闲 GPU

从 `nvidia-smi` 中筛选空闲 GPU（显存占用 < 5%），优先在空闲卡上执行，避免与其他任务的显存竞争：

```bash
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader | \
  awk -F', ' '{pct=$2*100/$3; if(pct<5) print "GPU "$1" is idle ("pct"% used)"}' 
```

### 6.2 多卡时选择最大空闲显存的卡

```bash
nvidia-smi --query-gpu=index,memory.free --format=csv,noheader | \
  sort -t', ' -k2 -rn | head -1 | awk -F', ' '{print "GPU "$1" has most free memory ("$2" MiB)"}'
```

## 7. 输出契约

进入本流程后，执行输出增加：

- `gpu_oom_preflight`: 预执行显存估算结果（低/中/高/超限）
- `gpu_memory_estimation`: 各项显存估算明细
- `gpu_oom_retries`: 重试记录数组
- `adjusted_params`: 调整后的参数
- `gpu_oom_resolved`: 是否通过降级成功解决
- `blocking_reason`: 若耗尽重试预算，记录 `gpu_oom_retry_exhausted`

## 参考案例

| 案例 | 问题 | 参数 | 解决方式 |
|------|------|------|---------|
| AlphaFold 3 7PNM (5337 tokens) | 推理成功但结果物化 OOM (需 69 GiB) | num_recycles: 10→5→3 | 降低 recycles、清理 BFC 缓存、使用默认分配器 |
| AlphaFold 3 7PNM (5337 tokens, 8 GPUs) | 单卡 83 GiB 不够用 | num_seeds=8, num_recycles=1 | 自动多 seed 并行：8 张卡各跑 1 个 seed，每卡仅需 ~74 GiB |
| Evo 2 SAE (100k tokens) | FFT 计算 OOM | sequence_length: 100k→8k 分段 | 分块处理（13 个 chunks） |
