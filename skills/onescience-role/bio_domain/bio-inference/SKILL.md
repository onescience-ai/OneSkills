---
name: bio-inference
description: OneScience 生信模型推理范畴路由。用于执行当前 OneScience 代码仓已有 biosciences 模型的 inference、predict、sampling、generation、score-only 或 batch inference：AlphaFold、OpenFold、AlphaFold3、Protenix、SimpleFold、RFdiffusion、ProteinMPNN、PT-DiT、ProToken、Evo2、MolSculptor。强调输入协议、checkpoint、设备、环境、命令入口、输出校验和失败恢复；模型结构或训练改造请转 onescience-models。
---

# OneScience 生信模型推理范畴路由

本范畴只处理“稳定执行已有模型推理”。如果用户要改模型层、训练、微调、datapipe adapter 或组件契约，读取 `../onescience-models/SKILL.md`。

## 具体 skill 路由

- AF2 风格蛋白结构预测：AlphaFold JAX / AlphaFold-Multimer / OpenFold PyTorch。读取 `./af2-folding-inference/SKILL.md`
- AF3 风格复合物结构预测：AlphaFold3 JAX / Protenix PyTorch。读取 `./af3-protenix-complex-inference/SKILL.md`
- SimpleFold flow-matching 蛋白折叠推理：读取 `./simplefold-inference/SKILL.md`
- RFdiffusion 骨架生成、motif scaffolding、binder、partial diffusion：读取 `./rfdiffusion-inference/SKILL.md`
- ProteinMPNN backbone-to-sequence inverse folding、score-only、fixed/tied positions：读取 `./proteinmpnn-inference/SKILL.md`
- PT-DiT de novo co-design、ProToken 编码/解码/结构重建：读取 `./ptdit-protoken-inference/SKILL.md`
- Evo2 genome LM prompt / FASTA / logits / variant scoring 类推理：读取 `./evo2-inference/SKILL.md`
- MolSculptor 小分子生成、优化、SMILES/分子图推理：读取 `./molsculptor-inference/SKILL.md`

## 公共资源

- `references/model_inference_matrix.md`：模型到入口、输入、checkpoint、输出和高危混淆点的矩阵。
- `references/inference_execution_contract.md`：所有生信模型推理必须遵守的 preflight、run、postflight 契约。
- `../../../../onescience-runtime/assets/bio_inference_templates/bio_inference_handoff.yaml`：交给 `onescience-skill -> onescience-coder/runtime` 前的统一交接模板。
- `{onescience_path}/onescience/examples/biosciences/_manifests/inference_run_manifest.yaml`：单次推理运行的可复现 manifest。
- `{onescience_path}/onescience/examples/biosciences/_manifests/model_requests/`：OneScience 官方 per-model request 示例。
- `{onescience_path}/onescience/examples/biosciences/_manifests/tools/validate_bio_inference_manifest.py`：无第三方依赖地检查 manifest 是否缺关键字段。
- `{onescience_path}/onescience/examples/biosciences/_manifests/tools/check_inference_outputs.py`：按模型类型检查输出目录是否至少包含预期产物。
## 推理路由原则

1. 先判定 `model_family`，再判定 `inference_mode`，不要从输出类型反推模型。例如“结构文件”可能来自 AlphaFold、OpenFold、AlphaFold3、Protenix、SimpleFold、RFdiffusion 或 ProToken。
2. 使用 OneScience 已有入口，不临时发明 wrapper：
   - AlphaFold：`examples/biosciences/alphafold/run_alphafold.py`
   - OpenFold：`examples/biosciences/openfold/run_pretrained_openfold.py`
   - AlphaFold3：`examples/biosciences/alphafold3/run_alphafold.py`
   - Protenix：`examples/biosciences/protenix/runner/inference_unified.py`
   - SimpleFold：`examples/biosciences/simplefold/inference.py` 或 `sample.py`
   - RFdiffusion：`examples/biosciences/RFdiffusion/scripts/run_inference.py`
   - ProteinMPNN：`examples/biosciences/ProteinMPNN/protein_mpnn_run.py`
   - PT-DiT：`examples/biosciences/pt_dit/example_scripts/de_novo_design.py`
   - Evo2：`examples/biosciences/evo2/infer.py` 或 `predict.py`
   - MolSculptor：`src/onescience/flax_models/MolSculptor/train/inference.py` 或 `examples/biosciences/molsculptor/inference/*`
3. 每次推理都必须明确：输入文件、checkpoint、环境变量、设备、输出目录、随机种子、精度、模型卡、源码锚点和输出校验。
4. 需要远程 GPU/DCU 或大数据库时，交接到 `onescience-skill` 后让执行层进入 `onescience-runtime` 的 discover/preflight；若环境未 ready 再回退 `onescience-installer`，不要在角色层直接承诺可运行。
5. manifest 校验和输出产物检查使用 OneScience 仓库 `examples/biosciences/_manifests/tools/`，role 层只把工具路径写入交接摘要。

## 最小输出

```yaml
bio_task_family: bio-inference
selected_concrete_skill:
model_family:
inference_mode:
input_protocol:
entrypoint:
checkpoint:
runtime_device:
preflight_checks:
command_plan:
expected_outputs:
output_validation_plan:
failure_recovery:
execution_entry:
```

## 禁止事项

- 不要混用 AF2/OpenFold、AF3/Protenix、SimpleFold 的 feature dict 或 batch。
- 不要把 RFdiffusion 的 Gly backbone 输出当成完成侧链序列设计；需要后接 ProteinMPNN 或筛选。
- 不要把 ProteinMPNN 当作结构预测模型。
- 不要把 Evo2 的 DNA token 推理、MolSculptor 的 SMILES/分子图推理接到蛋白结构 datapipe。
- 不要在 checkpoint、模型卡和 entrypoint 未一致时启动推理。
- 不要在 role 层直接运行 bio inference manifest 或输出检查脚本。
