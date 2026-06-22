---
name: bio-simplefold-inference
description: SimpleFold 蛋白结构推理 skill。用于执行 OneScience SimpleFold flow-matching FoldingDiT 的 FASTA 到结构、sample、pLDDT 和 ESM 条件推理，收紧模型规模、ESM 特征、atom-token 特征、采样步数、checkpoint 和结构输出校验。
---

# SimpleFold 推理

## 使用边界

用于 OneScience SimpleFold 示例的蛋白折叠推理。它不是 AF2/OpenFold 或 AF3/Protenix feature pipeline，不要互换输入。

## 可复用资源

- `{onescience_path}/onescience/examples/biosciences/_manifests/model_requests/simplefold_request.yaml`：FASTA、模型规模、采样、ESM、checkpoint 和输出模板。
- `references/simplefold_execution.md`：SimpleFold 输入特征、采样参数和失败恢复。

## 推荐流程

1. 读模型卡：`onescience-coder/assets/models/simplefold.md`。
2. 确认入口：`{onescience_path}/onescience/examples/biosciences/simplefold/inference.py`，需要采样实验时看 `sample.py`。
3. Preflight：FASTA、模型规模、checkpoint、ESM 表征路径或在线生成能力、GPU 显存。
4. 参数收紧：`num_steps`、`tau`、`nsample_per_protein`、输出目录和 seed。
5. Postflight：结构文件、残基数、pLDDT/置信度、空结构、采样多样性。

## 禁止事项

- 不要把 OpenFold/Protenix batch 送入 SimpleFold。
- 缺少 `esm_s` 或 atom-token 特征路径时，不要假装能直接最小 forward 完成结构推理。
- 不要只看生成 PDB 是否存在，必须检查残基数和坐标是否非空。
