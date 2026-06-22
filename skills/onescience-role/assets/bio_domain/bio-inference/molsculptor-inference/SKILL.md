---
name: bio-molsculptor-inference
description: MolSculptor 小分子生成与优化推理 skill。用于执行 OneScience MolSculptor 的 SMILES/分子图编码、latent diffusion、de novo generation、分子优化、reward 筛选和 case 脚本，收紧 RDKit sanitize、padding/vocab/checkpoint、采样策略、外部 docking 依赖和 SMILES/SDF 输出校验。
---

# MolSculptor 推理

## 使用边界

用于小分子/药物设计辅助推理。它不接受蛋白 FASTA、PDB folding batch 或 Evo2 DNA tokens。

## 可复用资源

- `{onescience_path}/onescience/examples/biosciences/_manifests/model_requests/molsculptor_request.yaml`：SMILES/target case、checkpoint、采样、reward 和输出模板。
- `references/molsculptor_execution.md`：SMILES/graph、RDKit、diffusion、case/docking 和输出检查。

## 推荐流程

1. 读模型卡：`onescience-coder/assets/models/molsculptor.md`。
2. 选择入口：通用推理看 `src/onescience/flax_models/MolSculptor/train/inference.py`；具体靶点优化看 `examples/biosciences/molsculptor/inference/*` 或 `cases/<case>/`。
3. Preflight：RDKit、JAX/Flax、checkpoint、vocab、padding atom 上限、初始 SMILES/分子、case 配置。
4. 若涉及 docking reward：确认 OpenBabel/PDBQT/DSDP 脚本和 receptor 文件，不默认运行。
5. Postflight：SMILES validity、duplicate、property、reward、SDF/CSV/PKL、失败分子比例。

## 交接物

```yaml
bio_task_family: bio-inference
selected_concrete_skill: molsculptor-inference
model_family: MolSculptor
inference_mode: de_novo_or_optimization
input_protocol: SMILES_or_molecule_graph
entrypoint:
checkpoint:
sampling_strategy:
reward_or_case:
expected_outputs:
output_validation_plan:
execution_entry:
```

## 禁止事项

- 不要把 docking reward 当作已经运行，除非日志和产物证明完成。
- 不要忽略 RDKit sanitize 失败和重复分子。
- 不要把生成分子直接写成候选药物结论。
