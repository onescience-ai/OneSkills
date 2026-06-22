# SimpleFold 离线预检与故障恢复

## 适用场景

当端到端蛋白设计验证链路包含 SimpleFold 时，把本环境准备脚本放入 `submit.slurm` 最前面执行。该流程针对没有外网/DNS 的集群节点，避免 SimpleFold 在运行时隐式下载 ESM repo、ESM2 权重、pLDDT 或 Boltz cache。

默认模型资产根目录：

```text
/public/share/sugonhpcapp01/onestore/onemodels
```

默认 OneScience 代码仓根目录（远端 Slurm 作业内）：

```bash
export ONESCIENCE_DIR="${ONESCIENCE_DIR:-~/onescience}"
export ONESCIENCE_MODELS_DIR="${ONESCIENCE_MODELS_DIR:-/public/share/sugonhpcapp01/onestore/onemodels}"
RUN_DIR="${RUN_DIR:-$SLURM_SUBMIT_DIR}"
SETUP_ESM_SCRIPT="$ONESCIENCE_DIR/examples/biosciences/workflows/protein_design_validation/tools/setup_esm_torchhub.sh"
```

`setup_esm_torchhub.sh` 属于 OneScience 仓库示例资产，不再从 `oneskills` 或 `skills/onescience-installer` 下发副本。

## 脚本来源

在提交 `sbatch` 前，agent 只检查脚本存在，不执行 setup：

- OneScience 源脚本：`$ONESCIENCE_DIR/examples/biosciences/workflows/protein_design_validation/tools/setup_esm_torchhub.sh`
- Slurm 运行：在作业开头直接执行该脚本。

## Slurm 开头运行

把下面逻辑放在 `submit.slurm` 的环境准备段，且早于 RFdiffusion、ProteinMPNN 和 SimpleFold 主流程：

```bash
set -euo pipefail
RUN_DIR="${RUN_DIR:-$SLURM_SUBMIT_DIR}"
export ONESCIENCE_DIR="${ONESCIENCE_DIR:-~/onescience}"
export ONESCIENCE_MODELS_DIR="${ONESCIENCE_MODELS_DIR:-/public/share/sugonhpcapp01/onestore/onemodels}"
SETUP_ESM_SCRIPT="$ONESCIENCE_DIR/examples/biosciences/workflows/protein_design_validation/tools/setup_esm_torchhub.sh"

test -f "$SETUP_ESM_SCRIPT" || { echo "missing setup script: $SETUP_ESM_SCRIPT" >&2; exit 2; }

conda activate onescience311
set +e
bash "$SETUP_ESM_SCRIPT" 2>&1 | tee "$RUN_DIR/setup_esm_torchhub.log"
setup_status=${PIPESTATUS[0]}
set -e
if [[ "$setup_status" -ne 0 ]]; then
  echo "setup_esm_torchhub failed with exit code $setup_status" >&2
  exit "$setup_status"
fi
```

确认输出包含：

- `SimpleFold checkpoints are ready`
- `SimpleFold offline cache is ready`
- `OK: found callable esm2_t36_3B_UR50D`
- `Patching hubconf.py to load esm2_t36_3B_UR50D without contact-regression`

这些信息应出现在 Slurm 日志或 `$RUN_DIR/setup_esm_torchhub.log` 中。

## 默认资产布局

```text
/public/share/sugonhpcapp01/onestore/onemodels/
  esm_models/
    esm-main/
    esm2_t36_3B_UR50D.pt
    esm2_t36_3B_UR50D-contact-regression.pt  # 可选；只有 --use-contact 时强制需要
  simplefold/
    boltz1_conf.ckpt
    ccd.pkl
    plddt.ckpt
    plddt_module_1.6B.ckpt
    simplefold_100M.ckpt
    simplefold_360M.ckpt
    simplefold_700M.ckpt
    simplefold_1.1B.ckpt
    simplefold_1.6B.ckpt
    simplefold_3B.ckpt
```

`esm_models/esm_models` 和 `esm_models/esm2_t36_3B_UR50D` 这两个空目录不要作为 ESM repo 或权重目录使用；有效 repo 是 `esm_models/esm-main`。

路径不同就用参数覆盖：

```bash
SETUP_ESM_SCRIPT="$ONESCIENCE_DIR/examples/biosciences/workflows/protein_design_validation/tools/setup_esm_torchhub.sh"
bash "$SETUP_ESM_SCRIPT" \
  --onemodels-dir /path/to/onemodels \
  --esm-repo-src /path/to/esm-main \
  --weight /path/to/esm2_t36_3B_UR50D.pt \
  --contact /path/to/esm2_t36_3B_UR50D-contact-regression.pt \
  --simplefold-dir /path/to/simplefold \
  --simplefold-cache /path/to/simplefold
```

如果管线改用 `simplefold_1.6B`：

```bash
SETUP_ESM_SCRIPT="$ONESCIENCE_DIR/examples/biosciences/workflows/protein_design_validation/tools/setup_esm_torchhub.sh"
bash "$SETUP_ESM_SCRIPT" \
  --simplefold-model-ckpt /public/share/sugonhpcapp01/onestore/onemodels/simplefold/simplefold_1.6B.ckpt
```

## 必要下载文件

SimpleFold：

```text
https://ml-site.cdn-apple.com/models/simplefold/plddt_module_1.6B.ckpt
保存为: simplefold/plddt.ckpt

https://ml-site.cdn-apple.com/models/simplefold/simplefold_1.6B.ckpt
保存为: simplefold/simplefold_1.6B.ckpt
```

ESM2：

```text
https://github.com/facebookresearch/esm/archive/refs/heads/main.zip
解压为: esm_models/esm-main/

https://dl.fbaipublicfiles.com/fair-esm/models/esm2_t36_3B_UR50D.pt
保存为: esm_models/esm2_t36_3B_UR50D.pt

https://dl.fbaipublicfiles.com/fair-esm/regression/esm2_t36_3B_UR50D-contact-regression.pt
保存为: esm_models/esm2_t36_3B_UR50D-contact-regression.pt
说明: 默认预检脚本会 patch hubconf 跳过 contact head；该文件缺失时仍可运行。只有显式加 `--use-contact` 才强制需要。
```

Boltz/SimpleFold FASTA 预处理：

```text
https://huggingface.co/boltz-community/boltz-1/resolve/main/ccd.pkl
保存为: simplefold/ccd.pkl

https://huggingface.co/boltz-community/boltz-1/resolve/main/boltz1_conf.ckpt
保存为: simplefold/boltz1_conf.ckpt
```

## 脚本副作用

`setup_esm_torchhub.sh` 会清空当前用户的 `torch.hub.get_dir()`，通常是：

```text
~/.cache/torch/hub
```

并重建：

```text
~/.cache/torch/hub/facebookresearch_esm_main/
~/.cache/torch/hub/checkpoints/esm2_t36_3B_UR50D.pt
~/.cache/torch/hub/checkpoints/esm2_t36_3B_UR50D-contact-regression.pt
```

如果同一用户还依赖其它 torch.hub repo，先备份或确认可重建。

## 管线侧必须配合的检查

- `submit.slurm` 开头必须检查 `$ONESCIENCE_DIR/examples/biosciences/workflows/protein_design_validation/tools/setup_esm_torchhub.sh` 存在。
- SimpleFold 每个 run 的输出目录下应有 `cache/ccd.pkl` 和 `cache/boltz1_conf.ckpt`。
- 命令应显式带 `--output_format pdb`。
- 完整保存 stdout/stderr。
- 结构数为 0 时非零退出。
- Slurm 侧使用 `set -o pipefail` 和 `${PIPESTATUS[0]}` 保留 Python 真实退出码。
