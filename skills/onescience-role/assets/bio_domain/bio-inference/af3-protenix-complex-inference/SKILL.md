---
name: bio-af3-protenix-complex-inference
description: AlphaFold3 / Protenix 复合物结构推理 skill。用于执行 OneScience 中 AlphaFold3 JAX 或 Protenix PyTorch 的蛋白、核酸、配体、离子复合物推理，收紧 AF3 JSON、Protenix JSON、MSA/template/CCD/RDKit、checkpoint、diffusion samples、attention fallback 和 confidence 输出校验。
---

# AF3 / Protenix 复合物结构推理

## 使用边界

用于 AF3 风格复合物结构预测。AlphaFold3 与 Protenix 概念相近但实现不兼容：AlphaFold3 是 JAX/Haiku，Protenix 是 PyTorch/OneScience 模块化。

## 可复用资源

- `{onescience_path}/onescience/examples/biosciences/_manifests/model_requests/af3_protenix_request.yaml`：JSON、checkpoint、MSA、diffusion sample、attention 和输出模板。
- `references/af3_protenix_execution.md`：二者入口、输入协议、资源和失败恢复差异。

## 推荐流程

1. 选择模型：需要 AF3 JAX data pipeline / model_dir 用 `AlphaFold3`；需要 Protenix unified PyTorch 入口用 `Protenix`。
2. 读模型卡：`alphafold3.md` 或 `protenix.md`。
3. 固定入口：
   - AlphaFold3：`{onescience_path}/onescience/examples/biosciences/alphafold3/run_alphafold.py`
   - Protenix：`{onescience_path}/onescience/examples/biosciences/protenix/runner/inference_unified.py`
4. Preflight：JSON schema、protein/RNA/DNA/ligand、MSA/template、CCD/RDKit、model checkpoint、attention 实现、输出目录。
5. 运行策略：先小样本/少 diffusion sample 验证输入，再放大 `num_diffusion_samples`、`N_sample`、`N_step`。
6. Postflight：结构文件、ranking/confidence、PAE/PDE/pLDDT/contact、链/配体/原子数、失败日志。

## 交接物

```yaml
bio_task_family: bio-inference
selected_concrete_skill: af3-protenix-complex-inference
model_family: AlphaFold3_or_Protenix
inference_mode: biomolecular_complex_structure
input_protocol: AF3_JSON_or_Protenix_JSON
entrypoint:
checkpoint_or_model_dir:
msa_template_mode:
ligand_ccd_resources:
diffusion_sampling:
attention_fallback:
expected_outputs:
output_validation_plan:
execution_entry:
```

## 禁止事项

- 不要把 AF3 JSON 直接当作 Protenix feature dict，或反过来复用。
- 不要忽略配体 CCD、SMILES/SDF、RDKit 和 bond 信息。
- Attention 报错时优先切换 fallback，不要改模型结构。
