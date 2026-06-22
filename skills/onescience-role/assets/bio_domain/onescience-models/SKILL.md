---
name: bio-onescience-models
description: OneScience 生信模型开发范畴路由。用于 AlphaFold、OpenFold、AlphaFold3、Protenix、SimpleFold、RFdiffusion、ProteinMPNN、PT-DiT、ProToken、Evo2、MolSculptor、SE3Transformer 相关的模块、训练、微调、checkpoint、batch 协议、datapipe 适配和源码改造任务；单纯执行已有模型推理时优先使用 bio-inference。
---

# OneScience 生信模型范畴路由

当用户请求涉及模型本体、模块替换、训练、微调、checkpoint、batch 协议、datapipe adapter 或 `examples/biosciences` 源码改造时，使用本范畴。若用户目标只是稳定执行已有模型的 inference / predict / sampling / generation，回到 `../bio-inference/SKILL.md`。

## 具体 skill 路由

- 蛋白/复合物结构预测：AlphaFold、OpenFold、AlphaFold3、Protenix、SimpleFold。读取 `./protein-structure-prediction/SKILL.md`
- 蛋白设计和生成：RFdiffusion、ProteinMPNN、PT-DiT、ProToken、SE3Transformer。读取 `./protein-design-generation/SKILL.md`
- 基因组语言模型：Evo2。读取 `./genome-language-modeling/SKILL.md`
- 小分子生成与优化：MolSculptor。读取 `./molecular-design/SKILL.md`
- biology/protenix/simplefold/openfold/evo2 datapipe 或 adapter：读取 `./biology-datapipes-adapters/SKILL.md`

## 必须交接给 coder 的资产

模型任务进入 `onescience-coder` 前，要求下游先读：

- `onescience-coder/assets/models/model_index.md`
- 对应模型卡，例如 `protenix.md`、`evo2.md`、`rfdiffusion.md`
- 需要时读取 `onescience-coder/assets/datapipes/biology_protein.md` 或 `biology_genome.md`
- 需要改模块时读取 `onescience-coder/assets/contracts/component_index.md`

## 可复用模板

- `../../../onescience-coder/assets/bio_model_templates/model_handoff.yaml`：模型训练、微调、模块修改和 batch/adapter 改造任务的交接模板。纯推理任务使用 `onescience-runtime/assets/bio_inference_templates/bio_inference_handoff.yaml`。
- `../../../onescience-coder/assets/bio_model_templates/datapipe_adapter_handoff.yaml`：datapipe/adapter 兼容性判断和桥接计划模板。

当用户请求已经要转入实现层时，优先按模板补齐字段再交给 `onescience-skill -> onescience-coder`。

## 交接规则

输出时至少整理：

- `onescience_model_family`
- `task_mode`
- `input_protocol`
- `example_entry`
- `source_anchors`
- `coder_assets_to_read`
- `remote_involved`
- `execution_entry`

## 禁止事项

- 不要把所有结构预测默认归到 `Protenix`。
- 不要混用 AF2、AF3、Protenix、OpenFold、SimpleFold 的 batch 协议。
- 不要把传统 RNA-seq、single-cell、variant workflow 误判成 OneScience 模型任务。
- 不要把“运行已有 checkpoint 做推理”的任务扩大成模型结构改造；先走 `bio-inference` 的 preflight 和输出校验。
