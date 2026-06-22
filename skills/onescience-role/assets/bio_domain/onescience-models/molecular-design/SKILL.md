---
name: bio-molecular-design
description: OneScience 小分子生成与药物设计模型 skill。用于 MolSculptor 的 SMILES/分子图、autoencoder、latent diffusion、分子优化、reward、DSDP/docking 相关 case、训练和推理任务。
---

# OneScience 小分子设计模型

## 使用边界

用于 OneScience 中 MolSculptor 相关模型任务。若用户只是计算描述符、相似性或 SMARTS 过滤，进入 `analysis-tools/cheminformatics-toolkit`。

## OneScience 锚点

- `examples/biosciences/molsculptor/inference`
- `examples/biosciences/molsculptor/training`
- `examples/biosciences/molsculptor/cases`
- `src/onescience/flax_models/MolSculptor`

## 输入协议

- SMILES 或分子图特征。
- autoencoder latent。
- diffusion transformer config。
- reward/optimization 依赖，如 QED、SA、LogP、docking score 或 case-local reward。

## 交接物

```yaml
bio_task_family: onescience-bio-model
onescience_model_family: MolSculptor
task_mode: inference | training | optimization | case-adaptation | module-change
input_protocol:
compound_source:
reward_definition:
checkpoint_or_weight_source:
source_anchors:
coder_assets_to_read:
execution_entry: onescience-skill -> onescience-coder
```

## 禁止事项

- 不要把蛋白质 datapipe 或 AF3 feature dict 复用于 MolSculptor。
- 不要把 RDKit 描述符任务误判为 MolSculptor 模型任务。
- 不要把 docking/reward 分数直接解释为药效。
