---
name: bio-protein-design-structure-validation
description: 蛋白设计 + 结构验证端到端 workflow skill。用于 RFdiffusion 骨架生成、ProteinMPNN 序列设计、SimpleFold/OpenFold/Protenix/AlphaFold3 结构预测验证、Slurm 提交、离线模型资产准备、候选排序和失败恢复；触发词包括蛋白设计流水线、protein design pipeline、RFdiffusion、ProteinMPNN、SimpleFold、结构验证、binder design、motif scaffolding、设计序列折叠评估。
---

# 蛋白设计 + 结构验证 workflow

## 使用边界

用于把蛋白设计候选从约束或骨架推进到计算结构验证和候选排序。它是 workflow 编排 skill，不替代单个模型 skill：

- 骨架生成：RFdiffusion。
- 骨架到序列：ProteinMPNN。
- 单体快速折叠验证：SimpleFold。
- 复合物、核酸、配体或 binder-target 统一结构验证：Protenix 或 AlphaFold3。
- AF2/OpenFold 路线：仅在 MSA/template 资产已准备好且任务符合 AF2/OpenFold 输入协议时使用。

本 skill 只给出计算筛选和结构预测置信度，不把 pLDDT、RMSD、TM-score 或 ranking score 表述为实验验证。

## 可复用资源

- `references/protein_design_validation_workflow.md`：端到端路由、阶段产物、实现约定、输出检查和故障恢复。
- `references/simplefold_offline_preflight.md`：SimpleFold/ESM/Boltz 离线资产预检和常见报错处理。
- `{onescience_path}/onescience/examples/biosciences/workflows/protein_design_validation/request.yaml`：OneScience 官方 workflow request 示例。
- `{onescience_path}/onescience/examples/biosciences/workflows/protein_design_validation/tools/setup_esm_torchhub.sh`：在 `submit.slurm` 开头执行，用于重建当前用户 torch.hub ESM 缓存并检查 SimpleFold 离线资产。

## 路径约定

- 读卡片或引用 OneScience 仓库内示例资产时，路径写法与 `onescience-coder` 资产卡片一致（`{onescience_path}/onescience/...`）。
- 生成远程 Slurm 或 Python 脚本时，通过 handoff 传入已解析的远端绝对路径到 `ONESCIENCE_DIR`；未传入时 fallback 远端 `~/onescience`。
- 所有 OneScience 代码入口、示例 PDB、配置和 helper 脚本在作业脚本内都必须从 `$ONESCIENCE_DIR` 派生，禁止写成 `./examples/...` 或裸 `examples/...`。`./...` 只允许表示当前 run 目录下的产物。
- 所有 workflow 示例资产从 OneScience 仓库读取；不要从 `oneskills` 或 `skills/onescience-installer` 读取执行脚本。
- `setup_esm_torchhub.sh` 不在 `sbatch` 之前执行；它必须作为 `submit.slurm` 最前面的环境准备步骤执行。
- 默认模型资产根目录是 `/public/share/sugonhpcapp01/onestore/onemodels`，在脚本中使用 `ONESCIENCE_MODELS_DIR="${ONESCIENCE_MODELS_DIR:-/public/share/sugonhpcapp01/onestore/onemodels}"`。
- 对常用示例输入，RFdiffusion 的 `1qys.pdb` 必须解析为 `$ONESCIENCE_DIR/examples/biosciences/RFdiffusion/examples/input_pdbs/1qys.pdb`，不要使用 `./examples/input_pdbs/1qys.pdb`。
- Slurm 作业开头先 fail-fast 检查 `$ONESCIENCE_DIR`、各模型入口脚本、关键输入文件和 staged setup 脚本是否存在；不要让路径错误混进模型运行阶段才暴露。

## 必读顺序

1. 先读本文件，判断是否真是端到端蛋白设计验证，而不是单个模型推理。
2. 读取 `references/protein_design_validation_workflow.md`，确定链路和交接物。
3. 如果验证器包含 SimpleFold，读取 `references/simplefold_offline_preflight.md`，并使用 OneScience 仓库内的 `setup_esm_torchhub.sh`。不要在 `sbatch` 前运行它。
4. 生成执行代码时优先采用“一个 Python pipeline + 一个 submit.slurm”的形态：Python 负责编排 RFdiffusion、ProteinMPNN、SimpleFold 和验证；Slurm 只负责环境、run 目录、远端 setup 脚本执行、日志和真实退出码。
5. 在 `submit.slurm` 开头加入环境准备段：

```bash
export ONESCIENCE_DIR="${ONESCIENCE_DIR:-~/onescience}"
export ONESCIENCE_MODELS_DIR="${ONESCIENCE_MODELS_DIR:-/public/share/sugonhpcapp01/onestore/onemodels}"
RUN_DIR="${RUN_DIR:-$SLURM_SUBMIT_DIR}"
SETUP_ESM_SCRIPT="$ONESCIENCE_DIR/examples/biosciences/workflows/protein_design_validation/tools/setup_esm_torchhub.sh"
conda activate onescience311
bash "$SETUP_ESM_SCRIPT"
```

6. 如果需要下钻单模型，再交给对应推理 skill：
   - RFdiffusion：`../../bio-inference/rfdiffusion-inference/SKILL.md`
   - ProteinMPNN：`../../bio-inference/proteinmpnn-inference/SKILL.md`
   - SimpleFold：`../../bio-inference/simplefold-inference/SKILL.md`
   - Protenix/AlphaFold3：`../../bio-inference/af3-protenix-complex-inference/SKILL.md`

## 推荐流程

1. 明确起点：长度/contig/motif/binder 目标、已有 backbone PDB、已有设计序列，或复合物验证输入。
2. 选择最短链路：
   - 无 backbone：`RFdiffusion -> ProteinMPNN -> structure validator`
   - 已有 backbone：`ProteinMPNN -> structure validator`
   - 已有序列：直接进入 `structure validator`
3. 固定资产根目录：`/public/share/sugonhpcapp01/onestore/onemodels`，不要继续使用旧路径。
4. 远端 Slurm 通过 handoff 传入 `ONESCIENCE_DIR`；未传入时 fallback 远端 `~/onescience`。
5. SimpleFold 环境准备：ESM repo、ESM2 权重、pLDDT、Boltz `ccd.pkl` 和 `boltz1_conf.ckpt` 必须本地可用；`setup_esm_torchhub.sh` 在 Slurm 作业开头执行。
6. Python pipeline 必须保存 `pipeline_summary.json`，记录每阶段状态、产物数量、关键文件路径和错误信息；必需阶段产物为 0 时非零退出。
7. Slurm 运行必须保留完整日志、真实退出码和每阶段产物清单。
8. 输出候选排序表：RFdiffusion backbone 指标、ProteinMPNN score、结构预测置信度、结构文件路径、失败原因。

## 交接物

```yaml
bio_task_family: bio-workflow
selected_concrete_skill: protein-design-structure-validation
workflow_type: protein_design_to_structure_validation
starting_point: no_backbone | backbone_pdb | designed_sequence | complex_validation
design_models:
  backbone_generator: RFdiffusion | none
  sequence_designer: ProteinMPNN | none
structure_validator: SimpleFold | Protenix | AlphaFold3 | OpenFold
onescience_root: "{onescience_path}/onescience"
models_root: /public/share/sugonhpcapp01/onestore/onemodels
input_protocol:
  contig:
  motif_or_target_pdb:
  backbone_pdb:
  fasta:
  complex_json:
runtime:
  env_name: onescience311
  scheduler: slurm
  device: dcu_or_gpu_or_cpu
remote_environment_setup:
  remote_setup_script_uploaded:
  simplefold_setup_runs_in_slurm:
  missing_assets:
expected_outputs:
  backbone_pdbs:
  designed_fastas:
  predicted_structures:
  summary_json:
  full_logs:
validation_plan:
  structure_count_nonzero:
  confidence_metrics:
  sequence_design_scores:
  optional_reference_metrics:
execution_entry: onescience-skill -> onescience-coder -> onescience-runtime
```

## 禁止事项

- 不要把 RFdiffusion 输出当作完成序列设计；它通常还需要 ProteinMPNN。
- 不要把 ProteinMPNN 当结构预测模型。
- 不要混用 SimpleFold、OpenFold、Protenix 和 AlphaFold3 的输入协议。
- 不要让计算节点运行时联网下载 ESM、pLDDT、CCD 或 Boltz 资产。
- 不要让 `SimpleFold completed (exit=0)` 但 `0 structures` 的管线被标记为成功。
