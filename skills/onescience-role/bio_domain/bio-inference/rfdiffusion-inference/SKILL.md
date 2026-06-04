---
name: bio-rfdiffusion-inference
description: RFdiffusion 蛋白骨架生成推理 skill。用于执行 OneScience RFdiffusion 的 unconditional backbone generation、motif scaffolding、binder design、symmetric oligomer、partial diffusion，收紧 Hydra contig、input_pdb、checkpoint、num_designs、output_prefix、TRB/trajectory 和后接 ProteinMPNN 校验。
---

# RFdiffusion 推理

## 使用边界

用于生成蛋白骨架或基于目标/基序的骨架设计。若目标是从骨架生成氨基酸序列，读取 `../proteinmpnn-inference/SKILL.md`。

## 可复用资源

- `{onescience_path}/onescience/examples/biosciences/_manifests/model_requests/rfdiffusion_request.yaml`：contig、input PDB、checkpoint、num designs、partial diffusion 和输出模板。
- `references/rfdiffusion_execution.md`：常见模式、参数风险和输出解释。

## 推荐流程

1. 读模型卡：`onescience-coder/assets/models/rfdiffusion.md`。
2. 固定入口：`{onescience_path}/onescience/examples/biosciences/RFdiffusion/scripts/run_inference.py`。
3. 明确模式：unconditional、motif scaffolding、binder、partial diffusion、symmetry。
4. Preflight：contig 长度、input_pdb、hotspot、checkpoint、IGSO3 cache、output_prefix、num_designs。
5. Postflight：PDB、TRB、traj、contig 映射、是否只有 Gly backbone、是否需要 ProteinMPNN。

## 禁止事项

- 不要把 RFdiffusion 输出当成完整侧链设计。
- partial diffusion 必须保证输入结构长度与 contig/被扩散区域一致。
- 不要随意改 `model` / `preprocess` / `diffuser` 强绑定训练参数。
