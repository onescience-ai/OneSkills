---
name: bio-ptdit-protoken-inference
description: PT-DiT 与 ProToken 推理 skill。用于执行 OneScience PT-DiT 的 ProToken latent 蛋白序列-结构协同生成、de novo design、RePaint，以及 ProToken 的 PDB 编码、VQ code、decode_structure 结构重建，收紧 embedding/checkpoint 配套、NRES、设备 batch、padding_len 和输出 token/PDB 校验。
---

# PT-DiT / ProToken 推理

## 使用边界

用于 ProToken 结构 token 化/解码和 PT-DiT latent 生成。若只需骨架到序列 inverse folding，用 `../proteinmpnn-inference/SKILL.md`。

## 可复用资源

- `{onescience_path}/onescience/examples/biosciences/_manifests/model_requests/ptdit_protoken_request.yaml`：embedding、ckpt、nres、decode、batch 和输出模板。
- `references/ptdit_protoken_execution.md`：PT-DiT / ProToken 联动与常见错误。

## 推荐流程

1. 读模型卡：`pt_dit.md` 和 `protoken.md`。
2. PT-DiT 入口：`{onescience_path}/onescience/examples/biosciences/pt_dit/example_scripts/de_novo_design.py`。
3. ProToken 入口：`src/onescience/flax_models/protoken/scripts/infer.py` 或 `decode_structure.py`。
4. Preflight：`protoken_emb.pkl`、`aatype_emb.pkl`、PT-DiT ckpt、ProToken ckpt、`nres`、device count、padding。
5. Postflight：`result.pkl`、token indexes、optional PDB、序列/结构长度、是否成功 decode。

## 禁止事项

- 不要把普通 FASTA/PDB 直接当成 PT-DiT tokens。
- `nres`、embedding 维度和 checkpoint 必须配套。
- ProToken reconstruction 不等于 AF2/AF3 置信结构预测。
