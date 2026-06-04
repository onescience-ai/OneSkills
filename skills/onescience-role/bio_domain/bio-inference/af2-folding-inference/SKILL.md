---
name: bio-af2-folding-inference
description: AlphaFold v2 / OpenFold 蛋白结构推理 skill。用于执行 OneScience 中 AlphaFold JAX、AlphaFold-Multimer 或 OpenFold PyTorch 的 FASTA/MSA/template 推理，收紧 model_preset、db_preset、feature pipeline、checkpoint、输出 PDB/PAE/pLDDT 校验和常见失败恢复。
---

# AF2 / OpenFold 结构推理

## 使用边界

用于 AF2 风格蛋白结构预测：AlphaFold JAX/Haiku 或 OpenFold PyTorch。若输入含蛋白、核酸、配体多分子复合物并使用 AF3 JSON，读取 `../af3-protenix-complex-inference/SKILL.md`。

## 可复用资源

- `{onescience_path}/onescience/examples/biosciences/_manifests/model_requests/af2_inference_request.yaml`：FASTA、preset、数据库、参数和输出模板。
- `references/af2_openfold_execution.md`：AlphaFold 和 OpenFold 的入口、协议差异、preflight 和输出检查。
- 公共检查工具：`{onescience_path}/onescience/examples/biosciences/_manifests/tools/validate_bio_inference_manifest.py`、`{onescience_path}/onescience/examples/biosciences/_manifests/tools/check_inference_outputs.py`。

## 推荐流程

1. 选择模型：原版 AF2/JAX 用 `AlphaFold`；PyTorch/OpenFold 权重或 OpenFold pipeline 用 `OpenFold`。
2. 明确输入：FASTA、monomer/multimer、MSA 是否预计算、template 最大日期、数据库 preset。
3. 读模型卡：`onescience-coder/assets/models/alphafold.md` 或 `openfold.md`。
4. 固定入口：
   - AlphaFold：`{onescience_path}/onescience/examples/biosciences/alphafold/run_alphafold.py`
   - OpenFold：`{onescience_path}/onescience/examples/biosciences/openfold/run_pretrained_openfold.py`
5. Preflight：参数目录、数据库目录、MSA 工具、template、输出目录、设备和精度。
6. Postflight：ranked PDB、unrelaxed/relaxed 区分、ranking_debug、pLDDT/PAE、链数和残基数。

## 交接物

```yaml
bio_task_family: bio-inference
selected_concrete_skill: af2-folding-inference
model_family: AlphaFold_or_OpenFold
inference_mode: monomer_or_multimer
input_protocol: FASTA_plus_MSA_template_pipeline
entrypoint:
checkpoint_or_model_dir:
database_preset:
model_preset:
preflight_checks:
expected_outputs:
output_validation_plan:
execution_entry:
```

## 禁止事项

- 不要把 AlphaFold JAX feature dict 直接交给 OpenFold PyTorch batch。
- Multimer 不能只把多条链拼成 monomer FASTA；必须走对应 preset 和 pipeline。
- 不要把 relaxed PDB 当作模型原始结构误差分析对象。
