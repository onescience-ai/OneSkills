# 阶段 5：推理代码生成

目标：生成与模型契约和数据契约一致、可复现的推理 pipeline。

## Codegen 输入

写代码前，先从 `infer_workdir` 中已保存的知识文件读取并汇总：

- `model_knowledge.md`
- 存在数据时的 `data_preparation_plan.md` 和 `data_manifest.json`
- `model_loading_plan.md`
- `inference_plan.md`
- 运行目标和硬件约束
- 必需输出和验证标准

非平凡代码生成或仓库编辑应使用 `onescience-coder`。交接内容必须自包含，包含路径、契约、参数默认值和阻塞项；在 infer -> coder 交接时，路径只用于追踪，供 coder 直接消费的知识必须同时以内容形式提供，不能只传文件路径。

## Pipeline 要求

生成的推理代码应支持：

- 对 config、checkpoint、input、output directory、device、dtype、batch size、seed 和领域参数提供显式 CLI 参数
- 输出路径必须使用 `repro_artifact_dir` 下的子目录：推理脚本写入 `<repro_artifact_dir>/code/`，推理输出结果写入 `<repro_artifact_dir>/outputs/`，运行日志写入 `<repro_artifact_dir>/logs/`。不得将推理产物散落在源码目录（如 `paper_cases/`）中。
- 在 `infer_workdir` 中记录对应引用
- 结构化日志和机器可读的结果摘要
- 对缺失文件、格式错误输入、device 不匹配和无效输出给出清晰失败信息
- 除非用户明确要求，执行期间不要隐藏式下载

### GPU 分配规则

生成多 GPU 推理代码时，必须遵守以下规则：

- 禁止将协议参数（如 seed 数量）硬编码为 GPU 数量。将 `seed_count`（协议参数）、`gpu_count`（从 `nvidia-smi` 或 `rocm-smi` 检测的硬件资源）、`worker_count`（并发工作单元）分别建模为独立变量。
- GPU 列表必须通过命令行参数 `--gpus` 传入，不得硬编码默认值（如 `default="0,1,2,3,4"`）。
- 不得含有对具体 GPU 数量的硬编码校验（如 `len(gpu_ids) != 5`）。
- 调度策略：`worker_count > gpu_count` 时分批轮转执行，`worker_count <= gpu_count` 时一卡一 worker。
- `worker_count` 的粒度应根据推理独立性选择：多个 seed-sample 组合可独立并发拆分为 worker，而非仅按 seed 级拆分。

### 多 seed 并行代码生成

当 phase_6 的多卡聚合判断决定启用多 seed 并行时，生成的推理入口脚本必须支持以下模式：

**必须支持的 CLI 参数**：

```
--seed SEED              单个 seed 值（多卡模式下每个进程传入不同的 seed）
--num_seeds N            seed 总数（用于元数据记录）
--output_dir DIR         每个 seed 的输出独立子目录（如 outputs/seed_1/）
--gpus GPU_IDS           可用 GPU 列表（如 "0,1,2,3,4,5,6,7"）
```

**单进程模式（兼容单卡）**：

```python
# 单卡/单 seed 模式：直接使用传入的 seed
python run_inference.py --input_json input.json --seed 1 --output_dir outputs/
```

**多进程调度脚本模式（多卡多 seed）**：

生成一个 shell 调度脚本 `run_multi_seed.sh`，内容模板：

```bash
#!/bin/bash
# 多 seed 并行调度脚本 — 由 onescience-infer 自动生成
# 每个 seed 是独立进程，通过 CUDA_VISIBLE_DEVICES 隔离到不同 GPU

set -e

GPU_IDS=(${GPU_IDS:-0 1 2 3 4 5 6 7})
NUM_SEEDS=${NUM_SEEDS:-${#GPU_IDS[@]}}
INPUT_JSON="${1:-input.json}"
OUTPUT_BASE="${2:-outputs}"

echo "=== Multi-Seed Parallel Inference ==="
echo "GPUs: ${GPU_IDS[*]}"
echo "Seeds: ${NUM_SEEDS}"
echo "Input: ${INPUT_JSON}"

for i in $(seq 0 $((NUM_SEEDS - 1))); do
    SEED=$((i + 1))
    GPU_ID=${GPU_IDS[$i]}
    SEED_OUTDIR="${OUTPUT_BASE}/seed_${SEED}"
    LOGFILE="${OUTPUT_BASE}/seed_${SEED}.log"
    mkdir -p "${SEED_OUTDIR}"

    echo "[$(date)] Launching seed=${SEED} on GPU ${GPU_ID}..."
    CUDA_VISIBLE_DEVICES=${GPU_ID} python run_inference.py \
        --input_json "${INPUT_JSON}" \
        --seed "${SEED}" \
        --output_dir "${SEED_OUTDIR}" \
        > "${LOGFILE}" 2>&1 &
done

echo "[$(date)] All seeds launched. Waiting for completion..."
wait

echo "[$(date)] All seeds completed."
echo "Outputs in: ${OUTPUT_BASE}/seed_*/"

# 可选：合并所有 seed 结果
python -c "
import json, os, glob
results = []
for d in sorted(glob.glob('${OUTPUT_BASE}/seed_*/')):
    result_file = os.path.join(d, 'result.json')
    if os.path.exists(result_file):
        with open(result_file) as f:
            results.append(json.load(f))
print(f'Merged {len(results)} seed results')
# 取最优结果（按置信度分数）
best = max(results, key=lambda r: r.get('confidence_score', 0))
print(f'Best seed: {best[\"seed\"]}, score: {best.get(\"confidence_score\", \"N/A\")}')
"
```

**关键约束**：
- 代码中不得硬编码 GPU 数量或 seed 数量；全部通过环境变量或 CLI 参数传入
- 每个 seed 的输出写入独立子目录，避免文件冲突
- 多 seed 并行不依赖任何跨卡通信库（不需要 NCCL/MPI/torchrun）
- 推理脚本本身保持单进程单 seed 逻辑不变；并行调度由外层 shell 脚本处理

对于 HuggingFace 模型，若文档给出官方 API 模式，应使用该模式。对于仓库模型，复用官方 runner 或 datapipe 模块，不要重新实现内部逻辑。

## Infer -> Coder 交接

当将当前阶段交接给 `onescience-coder` 时，至少提供以下信息：

```text
infer_handoff=true
task_method=inference_codegen
infer_workdir=<code_save_dir>/.infer_work/<run_id>
repro_artifact_dir=<repro_artifact_dir>
code_save_dir=<用户代码保存目录>
model_knowledge_path=<infer_workdir>/model_knowledge.md
model_knowledge_content=<model_knowledge.md 全文或执行所需完整内容>
data_preparation_plan_path=<infer_workdir>/data_preparation_plan.md
data_preparation_plan_content=<可选，但只要下游需要就必须提供>
data_manifest_path=<infer_workdir>/data_manifest.json
data_manifest_content=<可选，但只要下游需要就必须提供>
model_loading_plan_path=<infer_workdir>/model_loading_plan.md
model_loading_plan_content=<可选，但只要下游需要就必须提供>
inference_plan_path=<infer_workdir>/inference_plan.md
inference_plan_content=<inference_plan.md 全文或执行所需完整内容>
required_outputs=<当前步骤要求输出>
validation_criteria=<当前步骤完成标准>
next_action=onescience-coder
```

具体代码生成前，必须先从 `infer_workdir` 中保存的知识文件读取，再组织交接内容。由于 `onescience-coder` 只允许直接消费 `reference_resources[*].content` 或资源技能返回内容，infer 交接给 coder 时必须同时传递 `*_path` 与 `*_content`；路径用于追踪与 provenance，内容用于直接消费。

## 输入输出适配器

将 adapter 与模型逻辑分离：

- 输入 adapter：把准备好的数据转换为模型 batch
- 输出 adapter：写出 tensor、NetCDF/Zarr/CSV/JSON/image 或模型原生产物
- 验证 adapter：读取输出，不需要重新运行推理

对于所有领域，尽可能在输出中保留可解释元数据，例如坐标、单位、样本 ID、结构 ID、参考版本、mesh/field 映射、时间轴或模型原生 metadata。

## 最小测试

生成代码时，至少生成一个静态测试或 smoke test：

- CLI help/import 测试
- Manifest shape 和文件存在性检查
- 可行时执行 tiny sample inference
- 输出 schema 验证

在测试或预检实际运行前，不要声称生成的 pipeline 可执行。
