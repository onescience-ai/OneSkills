# 蛋白设计 + 结构验证工作流

## 目标

把蛋白设计任务从用户约束推进到可复现的计算结构验证结果。该流程覆盖 RFdiffusion、ProteinMPNN、SimpleFold、Protenix、AlphaFold3 和 OpenFold 的组合编排，重点是输入协议、离线资产、Slurm 运行、日志和候选排序。

默认模型资产根目录：

```text
/public/share/sugonhpcapp01/onestore/onemodels
```

不要再使用历史私有模型目录；所有新管线、模板和预检脚本都以本节的新路径为准。

默认 OneScience 代码仓根目录（远端 Slurm 作业内）：

```bash
ONESCIENCE_DIR="${ONESCIENCE_DIR:-~/onescience}"
ONESCIENCE_MODELS_DIR="${ONESCIENCE_MODELS_DIR:-/public/share/sugonhpcapp01/onestore/onemodels}"
```

`ONESCIENCE_DIR` 应由 handoff 注入远端绝对路径；未传入时 fallback 远端 `~/onescience`。

SimpleFold/ESM setup 脚本位于 OneScience 仓库：

```bash
SETUP_ESM_SCRIPT="$ONESCIENCE_DIR/examples/biosciences/workflows/protein_design_validation/tools/setup_esm_torchhub.sh"
```

Slurm 作业直接从 `$ONESCIENCE_DIR` 执行该脚本，不要从 `oneskills` 或 `skills/onescience-installer` 读取执行资产。

## 路径解析原则

- OneScience repo 路径：只使用 `$ONESCIENCE_DIR/...`，例如 `$ONESCIENCE_DIR/examples/biosciences/RFdiffusion/scripts/run_inference.py`。
- 运行产物路径：只使用 `$RUN_DIR/...` 或当前 run 目录下的相对路径，例如 `step1_rfdiffusion/samples/*.pdb`。
- skill 资源路径：role 只读取说明文档；可执行脚本必须来自 OneScience repo 或运行目录。
- Slurm 脚本路径：直接使用 `$ONESCIENCE_DIR/examples/biosciences/workflows/protein_design_validation/tools/setup_esm_torchhub.sh`。
- 禁止把 repo 内路径写成 `./examples/...`、`examples/...` 或从任意临时目录拼接。`FileNotFoundError: './examples/input_pdbs/1qys.pdb'` 就是这类错误。
- `~` 在传给 Python 前要展开为 `$HOME` 或用 `Path(...).expanduser()`；不要把未展开的 `~` 写入 JSON/YAML 后直接交给模型脚本。
- Slurm 作业开头 fail-fast 检查 repo、入口脚本、输入文件和 setup 脚本：

```bash
test -d "$ONESCIENCE_DIR" || { echo "missing OneScience repo: $ONESCIENCE_DIR" >&2; exit 2; }
test -f "$ONESCIENCE_DIR/examples/biosciences/RFdiffusion/scripts/run_inference.py" || exit 2
test -f "$ONESCIENCE_DIR/examples/biosciences/ProteinMPNN/protein_mpnn_run.py" || exit 2
test -f "$SETUP_ESM_SCRIPT" || { echo "missing setup script: $SETUP_ESM_SCRIPT" >&2; exit 2; }
if [[ "${REQUIRE_RFDIFFUSION_EXAMPLE_1QYS:-0}" == "1" ]]; then
  test -f "$ONESCIENCE_DIR/examples/biosciences/RFdiffusion/examples/input_pdbs/1qys.pdb" || exit 2
fi
```

## Setup 脚本约定

在生成并提交 `submit.slurm` 前，agent 只检查 OneScience 仓库内脚本路径存在。`sbatch submit.slurm` 只提交作业；不要在 Slurm 外提前执行 `setup_esm_torchhub.sh`。

## 代码生成参考形态

对远端集群任务，优先生成两个文件：`protein_design_pipeline.py` 和 `submit.slurm`。

- Python pipeline 负责真实业务流程：阶段函数、命令执行、日志、产物检查、失败汇总和 `pipeline_summary.json`。
- Slurm 脚本负责资源声明、模块/conda 环境、run 目录创建、执行 OneScience setup 脚本、调用 Python pipeline，并用 `${PIPESTATUS[0]}` 返回 Python 的真实退出码。
- 不要把复杂模型命令全部堆在 Slurm 里；Slurm 里只保留环境准备和一个清晰的 `python protein_design_pipeline.py --run_dir "$RUNDIR"` 调用。
- 模型根目录只在少数位置定义：`ONESCIENCE_MODELS_DIR` 和 Python 中的 `ONEMODELS_DIR` 应来自同一个配置。默认使用 `/public/share/sugonhpcapp01/onestore/onemodels`，用户显式提供旧路径时才覆盖。
- OneScience 代码仓在作业脚本内只从 `ONESCIENCE_DIR` 派生（由 handoff 注入远端路径，未传入时 fallback `~/onescience`）；不要用当前目录推断 repo。
- 每个阶段都要写入结构化 summary：`status`、产物数量、主要产物路径；异常要记录 `error`，最终有任何必需阶段失败时 `sys.exit(1)`。
- 允许 `--skip_rfdiffusion`、`--skip_proteinmpnn`、`--skip_simplefold`、`--skip_validation` 这类恢复参数，但跳过时必须从 run 目录重新发现已有产物。

阶段实现宜保持下面的粒度，而不是生成一个长函数：

```text
log()
run_command()
first_existing_path()
prepare_simplefold_cache()
step1_rfdiffusion()
step2_proteinmpnn()
step3_simplefold()
step4_validate()
main()
```

这些函数名不是强制 API，但生成代码应保持同等清晰的阶段边界。

## 路由选择

| 起始产物 | 设计步骤 | 验证步骤 | 推荐链路 |
| --- | --- | --- | --- |
| 只有长度、contig、motif 或 binder 目标 | 生成 backbone，再设计序列 | 预测设计序列结构 | `RFdiffusion -> ProteinMPNN -> SimpleFold/Protenix/AlphaFold3/OpenFold` |
| 已有 backbone PDB/mmCIF | 设计或重设计序列 | 预测设计序列结构 | `ProteinMPNN -> SimpleFold/Protenix/AlphaFold3/OpenFold` |
| 已有设计序列 FASTA | 跳过设计 | 预测结构和置信度 | `SimpleFold` 单体；复合物走 `Protenix/AlphaFold3` |
| 蛋白 + DNA/RNA/配体复合物 | 只设计蛋白链或使用已有序列 | 统一预测复合物 | `Protenix` 或 `AlphaFold3` |
| 单体快速筛选 | 可选 ProteinMPNN | 快速 sequence-to-structure ensemble | `SimpleFold` |

## 标准阶段

1. **RFdiffusion backbone generation**
   - 入口：`$ONESCIENCE_DIR/examples/biosciences/RFdiffusion/scripts/run_inference.py`
   - 建议工作目录：`$ONESCIENCE_DIR/examples/biosciences/RFdiffusion/scripts`；若不切换目录，则所有 `--config-path`、`inference.input_pdb` 和 `inference.output_prefix` 都必须使用绝对路径。
   - 示例输入 PDB：`$ONESCIENCE_DIR/examples/biosciences/RFdiffusion/examples/input_pdbs/1qys.pdb`，不要写成 `./examples/input_pdbs/1qys.pdb`。
   - 关键配置：`contigmap.contigs`、`inference.input_pdb`、`ppi.hotspot_res`、`diffuser.partial_T`、`inference.num_designs`、`inference.output_prefix`
   - 权重目录：`${ONESCIENCE_MODELS_DIR}/RFdiffusion/models`
   - 生成代码优先用 OmegaConf 读取 `config/inference/base.yaml`，写出 run 目录下的 `rf_config.yaml`，再用 `run_inference.py --config-path=<config_dir> --config-name=<config_stem>` 运行；这样比拼接长 Hydra 参数更稳。
   - 产物：设计 PDB、`.trb`、轨迹目录。`.trb` 要保留，用于追踪 contig 和残基映射。

2. **ProteinMPNN sequence design**
   - 入口：`$ONESCIENCE_DIR/examples/biosciences/ProteinMPNN/protein_mpnn_run.py`
   - 建议工作目录：`$ONESCIENCE_DIR/examples/biosciences/ProteinMPNN`
   - 权重目录：`${ONESCIENCE_MODELS_DIR}/ProteinMPNN/vanilla_model_weights`
   - 常用参数：`--pdb_path`、`--pdb_path_chains`、`--num_seq_per_target`、`--sampling_temp`、`--batch_size`、`--seed`、`--model_name v_48_020`
   - 对每个 RFdiffusion backbone 单独建输出目录，`--pdb_path` 使用绝对路径，`--out_folder` 指向当前 run 的 `step2_proteinmpnn/design_<n>/`。
   - 复杂约束优先走 helper JSON：fixed chains、fixed positions、tied positions、PSSM、omit AA。
   - 产物：FASTA、score header、probability/score 文件。

3. **Structure validation**
   - SimpleFold：FASTA 到单体结构，适合快速折叠筛选。
   - SimpleFold 前先把 ProteinMPNN 的多序列 FASTA 拆成单条 FASTA，统一写到 `step3_simplefold/fasta_inputs/`，header 用简单稳定格式，例如 `>A|design_<n>`。
   - SimpleFold 运行前在 `step3_simplefold/output/cache/` 准备 `ccd.pkl` 和 `boltz1_conf.ckpt`，来源优先为环境变量，其次为 `${ONESCIENCE_MODELS_DIR}/simplefold` 或兼容的 SimpleFold/Boltz 资产目录。
   - Protenix/AlphaFold3：复合物、核酸、配体、binder-target 接口。
   - OpenFold：AF2/OpenFold 风格输入，要求 MSA/template 资产和正确 batch 协议。

4. **Ranking and report**
   - 汇总 RFdiffusion backbone 指标、ProteinMPNN `score/global_score`、结构预测 pLDDT/ranking score、候选结构路径和失败原因。
   - 只有存在参考结构时才计算 RMSD、TM-score、lDDT 等参考指标。

## SimpleFold 管线实现约定

含 SimpleFold 的端到端管线必须把 `setup_esm_torchhub.sh` 放在 `submit.slurm` 的环境准备段最前面运行。不要在 `sbatch` 前运行该脚本。

推荐 Slurm 开头：

```bash
set -euo pipefail
RUN_DIR="${RUN_DIR:-$SLURM_SUBMIT_DIR}"
export ONESCIENCE_DIR="${ONESCIENCE_DIR:-~/onescience}"
export ONESCIENCE_MODELS_DIR="${ONESCIENCE_MODELS_DIR:-/public/share/sugonhpcapp01/onestore/onemodels}"
SETUP_ESM_SCRIPT="$ONESCIENCE_DIR/examples/biosciences/workflows/protein_design_validation/tools/setup_esm_torchhub.sh"

test -d "$ONESCIENCE_DIR" || { echo "missing OneScience repo: $ONESCIENCE_DIR" >&2; exit 2; }
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

管线实现应满足：

- `ONESCIENCE_MODELS_DIR=/public/share/sugonhpcapp01/onestore/onemodels`
- `ONESCIENCE_DIR` 由 handoff 注入远端绝对路径；未传入时 fallback 远端 `~/onescience`。
- SimpleFold checkpoint 目录使用 `${ONESCIENCE_MODELS_DIR}/simplefold`；如果集群资产使用 `SimpleFold` 大写目录，生成代码应通过配置或候选路径兼容，而不是在多个位置硬编码。
- SimpleFold 建议从 `$ONESCIENCE_DIR/examples/biosciences` 或项目实际安装环境运行；如果依赖本仓库内模块，先把需要的 repo 目录加入 `PYTHONPATH`。
- SimpleFold 使用 `sys.executable` 或当前 conda 环境的 `python` 调用，避免 Slurm 环境中意外切到系统 Python。
- SimpleFold 命令使用：

```bash
python -c "from simplefold.cli import main; main()" ...
```

- 如果上游 `simplefold/cli.py` 已补 `if __name__ == "__main__": main()`，也可以使用模块入口，但优先保留上面的显式 `main()` 调用以避免空跑。
- SimpleFold 输入应是目录形式的单条 FASTA 集合，而不是直接把 ProteinMPNN 的多序列 `.fa` 原样传入。
- SimpleFold 命令显式加 `--output_format pdb`，并检查 `predictions_*/*.pdb` 或 `predictions_*/*.cif`。
- 保存 `simplefold_stdout.log` 和 `simplefold_stderr.log`，不要只打印最后几行。
- SimpleFold 返回码非 0 或输出结构数为 0 时，整个管线必须非零退出。
- Slurm 脚本使用 `set -o pipefail`，并用 `status=${PIPESTATUS[0]}` 保留 Python 管线真实退出码。
- 每个 run 的 `step3_simplefold/output/cache` 要能从 `${ONESCIENCE_MODELS_DIR}/simplefold/ccd.pkl` 和 `${ONESCIENCE_MODELS_DIR}/simplefold/boltz1_conf.ckpt` 复制到 `ccd.pkl`、`boltz1_conf.ckpt`，不要让计算节点联网下载。

## 关键资产布局

```text
/public/share/sugonhpcapp01/onestore/onemodels/
  RFdiffusion/
    models/
  ProteinMPNN/
    vanilla_model_weights/
  esm_models/
    esm-main/
    esm2_t36_3B_UR50D.pt
    esm2_t36_3B_UR50D-contact-regression.pt
  simplefold/
    boltz1_conf.ckpt
    ccd.pkl
    plddt_module_1.6B.ckpt
    simplefold_100M.ckpt
    plddt.ckpt
    simplefold_360M.ckpt
    simplefold_700M.ckpt
    simplefold_1.1B.ckpt
    simplefold_1.6B.ckpt
    simplefold_3B.ckpt
```

Protenix、AlphaFold3 和 OpenFold 的 checkpoint / database 路径以对应推理 skill 和项目配置为准，但仍应挂在 `ONESCIENCE_MODELS_DIR` 或项目显式配置下。

## 生成后静态检查

agent 生成 `protein_design_pipeline.py` 和 `submit.slurm` 后，提交前先做一次轻量检查：

- Slurm 是否只调用一个 Python pipeline，并用 `${PIPESTATUS[0]}` 作为最终退出码。
- `setup_esm_torchhub.sh` 是否从 OneScience 仓库执行，且位于主 pipeline 之前。
- Python 是否从 `ONESCIENCE_DIR` 派生 RFdiffusion、ProteinMPNN、SimpleFold 的工作目录。
- 模型根目录是否集中配置，没有散落多个互相矛盾的私有路径。
- RFdiffusion 是否写 run 目录内的配置 YAML，并使用绝对 output prefix。
- ProteinMPNN 是否按 backbone 循环，输出到 run 目录内的独立子目录。
- SimpleFold 是否拆分单条 FASTA、准备离线 cache、显式 `main()`、保存 stdout/stderr、检查 PDB/CIF 数量。
- 任一必需阶段产物数量为 0 时，最终是否非零退出并写入 `pipeline_summary.json`。

## 输出检查

每次运行至少检查：

- RFdiffusion：PDB 数量、`.trb` 数量、contig 映射、轨迹是否完整。
- ProteinMPNN：FASTA 数量、header 中 score/global_score、设计链数量、固定位置是否保持。
- SimpleFold：结构文件数量大于 0、残基数非空、坐标非零、pLDDT/置信度文件存在时可解析。
- Protenix/AlphaFold3：结构文件、ranking/confidence JSON、实体数、链 ID、配体/核酸原子数。
- Slurm：`.out/.err`、pipeline full log、每阶段 stdout/stderr、最终 exit code。

## 常见失败和处理

| 日志片段 | 原因 | 处理 |
| --- | --- | --- |
| `SimpleFold completed (exit=0)` 但没有结构 | `python -m simplefold.cli` 只导入模块，未执行 `main()`；或输出格式/路径检查错误 | 改用 `python -c "from simplefold.cli import main; main()"`，加 `--output_format pdb`，并检查结构数 |
| `FileNotFoundError ... plddt.ckpt` | 开了 `--plddt`，但缺 pLDDT 权重 | 下载 `plddt_module_1.6B.ckpt` 并保存为 `simplefold/plddt.ckpt` |
| `Cannot find callable esm2_t36_3B_UR50D in hubconf` | torch.hub 缓存里的 ESM repo 错误或不完整 | 确认 OneScience `setup_esm_torchhub.sh` 已在 Slurm 作业开头执行并重建 `~/.cache/torch/hub` |
| `ImportError ... site-packages/esm/pretrained.py` | conda 中旧 `esm` 包抢先于 hub repo 导入 | 预检脚本检查时把 hub repo 放到 `sys.path` 首位；管线不要手动导入旧包 |
| `Missing key(s) ... contact_head.regression.*` | contact-regression 权重和 ESM 代码/主权重不兼容 | SimpleFold 不用 contact head，脚本默认 patch `hubconf.py` 跳过 |
| `Downloading the CCD dictionary ... URLError` | 节点无网，缺 `ccd.pkl` 或 `boltz1_conf.ckpt` | 把两个文件放入 `simplefold/`，管线运行前复制到当前 run cache |

## 交付建议

最终交付不要只给“运行成功”。至少给：

- run 目录
- 每阶段产物数量
- top candidates 表
- 每个候选的 FASTA、backbone PDB、预测结构路径
- 置信度和设计分数
- 失败候选的失败阶段和日志路径
- 可复现命令和环境变量
