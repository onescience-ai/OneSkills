# 阶段 6：推理执行

目标：使用正确的运行通道执行推理，并捕获证据。依赖包、硬件和运行环境需求在本阶段随 runtime handoff 一起交给 `onescience-runtime`，不再单独成阶段。

## Runtime 交接

使用 `onescience-runtime` 执行。准备 `infer_workdir` 下的 `runtime_request.json`，并把 runtime 返回结果记录到本技能的 manifest；最终仍由本技能返回外层 `execution_result`：

```json
{
  "task": "run inference",
  "code_save_dir": "",
  "repro_artifact_dir": "",
  "infer_workdir": "",
  "workdir": "",
  "entrypoint": "",
  "command": "",
  "execution_mode": "local | local_slurm | remote_slurm | remote_direct | unknown",
  "hardware": "",
  "package_requirements": [],
  "environment_requirements": {
    "python": "",
    "frameworks": [],
    "accelerator": "",
    "memory": "",
    "modules": [],
    "conda": "",
    "container_or_image": ""
  },
  "knowledge_inputs": {
    "model_knowledge_path": "",
    "data_manifest_path": "",
    "model_loading_plan_path": "",
    "inference_plan_path": ""
  },
  "preflight_checks": [],
  "expected_outputs": [],
  "log_dir": "",
  "manifest_path": ""
}
```

`package_requirements` 和 `environment_requirements` 来自 `step_handoff.inputs.runtime`、`infer_workdir` 中保存的 `model_knowledge.md` / `model_loading_plan.md` / `inference_plan.md`、项目 `requirements.txt` / `pyproject.toml` / 环境文件、官方 README、导入错误或模型加载计划。只记录有来源的信息；无法确认版本时写入范围、约束或 `MISSING:`，不要猜测精确版本。

如果本阶段存在多个待执行输入、多个候选结果或多个待处理目标，则应将它们纳入同一次执行流程或批处理流程。只有在真实阻断或用户要求中断时，才在当前输入处暂停。

如果用户要求本地执行，且当前环境合适，也应把 package 和环境需求记录到 `runtime_request.json`。如果用户要求 SLURM、SCnet、SSH 或远程执行，则路由到 `onescience-runtime`，并保留远程执行意图。

## 执行前检查

确认：

- `infer_workdir` 中所需知识文件已存在，并已据此构造 `runtime_request.json.knowledge_inputs`
- 入口文件存在
- Config、checkpoint 和输入文件存在或可解析
- **`repro_artifact_dir` 已创建且目录结构完备**：`code/`、`outputs/`、`logs/` 子目录均已创建，推理脚本和产物已正确写入对应子目录，未散落在源码目录中
- 输出目录可写
- 数据 manifest 满足模型输入契约
- 需要安装或确认的 package 已写入 `runtime_request.json.package_requirements`
- Python、框架、加速后端、内存、模块、conda、容器或镜像需求已写入 `runtime_request.json.environment_requirements`
- 对大型下载、package 安装、环境修改或远程提交等需要授权的操作，已获得用户授权；未授权时返回 `blocked` 或把执行标记为 `pending`

### GPU 预检

当推理涉及 GPU 时，执行前必须完成：

- 通过 `nvidia-smi --query-gpu=index,name,memory.total,memory.free --format=csv,noheader`（或 `rocm-smi`）获取实际可用 GPU 列表及其显存信息，写入 `evidence.preflight.gpu_info`
- 将检测到的 GPU 列表与生成的推理脚本中声明的 `--gpus` 参数做一致性校验：脚本不得硬编码 GPU 数量，必须与实际可用 GPU 列表匹配
- `gpu_count` = 实际空闲 GPU 数（显存占用 < 10% 视为空闲），`worker_count` = 推理任务需要的并发工作单元数。调度策略：`worker_count > gpu_count` 时分批轮转，`worker_count <= gpu_count` 时一卡一 worker

### GPU 显存预算估算

当推理任务预期使用 GPU 且模型规模或输入规模较大时（如蛋白质结构预测、大语言模型推理、长序列处理），执行前必须完成显存预算估算。详细策略见 `./references/gpu-oom-handling.md`。估算步骤：

1. **模型权重显存**：参数量 × bytes_per_element（float32=4, float16=2）
2. **输入数据显存**：tokens × dimensions × bytes_per_element
3. **中间激活显存**：权重显存的 2-5 倍；对于有 recycles 的任务，× (1 + num_recycles × 0.3)
4. **结果物化显存**：输出张量大小 × 2.0（拷贝开销）
5. **总估算** = 1 + 2 + 3 + 4

对比总估算与可用显存，确定风险等级：
- **< 60%**：低风险，正常执行
- **60%-80%**：中风险，自动启用内存优化参数（降低 recycles、启用 flash_attention、使用混合精度）
- **80%-95%**：高风险，必须使用低内存配置（最小 recycles、关闭 GPU relax、分段物化）
- **> 95%**：单卡超限，不要立即阻断——进入多卡聚合判断

估算结果写入 `evidence.preflight.gpu_memory_budget`，在 `runtime_request.json.environment_requirements.memory` 中声明实际显存需求。

### 多卡聚合判断 —— 多 seed 并行

当单卡显存估算 > 95% 时，执行多卡聚合判断（详见 `./references/gpu-oom-handling.md` 第 2.8 节）：

**判断流程**：

1. **确认任务支持多 seed 并行**：
   - AlphaFold 3 / ESMFold 等蛋白质结构预测：检查推理入口是否接受 `--seed` 或 `--num_seeds` 参数
   - 若任务不支持多 seed，跳过此流程，直接按单卡 OOM 处理

2. **计算最低配置需求**：
   ```
   task_memory_low = model_memory + base_activation × 1.3（num_recycles=1）+ materialization × 0.5（分段物化）
   ```

3. **筛选可行 GPU**：
   ```bash
   nvidia-smi --query-gpu=index,memory.free --format=csv,noheader | \
     awk -F', ' -v threshold=<task_memory_low_mib> '{if($2>threshold) print "GPU "$1" feasible ("$2" MiB free)"}'
   ```

4. **决策**：
   - `feasible_gpus == 0`：所有卡都不够 → `blocking_reason=gpu_oom_all_gpus_insufficient`，阻断
   - `feasible_gpus == 1`：单卡可行 → 单卡执行，`num_seeds=1`
   - `feasible_gpus >= 2`：多卡可行 → `num_seeds = feasible_gpus`，多卡多 seed 并行（不做人为截断）

5. **生成多卡调度命令**：
   ```bash
   # 每张卡独立运行一个 seed，通过 CUDA_VISIBLE_DEVICES 隔离
   for i in $(seq 0 $((num_seeds - 1))); do
     CUDA_VISIBLE_DEVICES=$i python run_inference.py \
       --seed=$((i + 1)) \
       --output_dir <repro_artifact_dir>/outputs/seed_$((i + 1))/ &
   done
   wait
   ```

6. **结果汇总**：全部 seed 完成后，合并所有 seed 的结果目录，取最优预测（按模型置信度分数）或合并为多 conformer 输出。

**关键约束**：
- 多 seed 并行**不需要** NCCL、torchrun 或任何跨卡通信库；每个进程是完全独立的
- 使用 shell 级 `CUDA_VISIBLE_DEVICES` 隔离，确保每个进程只能看到 1 张卡
- 每个 seed 的输出独立保存，避免文件写入冲突
- 若用户明确指定了 `num_seeds=1`，尊重用户选择，不自动启用多 seed

### GPU OOM 重试

若推理执行过程中发生 GPU OOM（非 SLURM 调度层 OOM），不要立即判定失败。按 `./references/gpu-oom-handling.md` 第 4 节执行：

1. 清理 GPU 显存（杀除残余进程、清理 JAX/PyTorch 缓存）
2. 按降级优先级自动调整参数（recycles → batch_size → 精度 → 分段物化）
3. 最多重试 2 次，每次记录调整证据
4. 耗尽重试预算后报告 `blocking_reason=gpu_oom_retry_exhausted`

### MMseqs / MSA 数据管线预检

当推理输入依赖 MMseqs2 或 JackHmmer 进行 MSA 搜索时：

- 若启用 `--use_mmseqs_gpu=true`，必须先估算 MMseqs 数据库索引（Uniref90、MGnify、BFD、Uniprot）的预估显存占用（通过 `du -sh <mmseqs_db_dir>/*.idx` 获取索引文件大小并 ×2.5 作为运行时显存估算系数），与可用 GPU 显存对比
- 若估算显存超出单卡可用显存的 70%，**自动回退 `--use_mmseqs_gpu=false`**，使用 CPU 模式搜索，并将回退原因记录到 `evidence.preflight.mmseqs_fallback_reason`
- 若存在已有 MSA 搜索缓存目录（如 `alignDB`），优先检查缓存命中，避免对每个案例重复全库搜索

执行前检查、命令构造和失败诊断应以 `infer_workdir` 中保存的知识产物为准，不要在这些文件已存在时重新凭会话上下文猜测模型 IO、数据格式、checkpoint 约束或预期输出。

## 证据捕获

将以下内容捕获到 `runtime_result.json`：

- 命令或提交脚本
- 执行通道和目标
- runtime 处理 package / 环境需求的结果
- Job ID 或进程退出码
- 日志路径和已同步日志路径
- 输出文件
- 可用时的运行时长
- 失败时的失败分类

执行后更新 `inference_run_manifest.json`。如果执行失败且没有产生可检查输出，不要继续进入验证；将失败证据写入 `execution_result.observation.risks` 和 `missing`，供 orchestrator 更新 Task State。
