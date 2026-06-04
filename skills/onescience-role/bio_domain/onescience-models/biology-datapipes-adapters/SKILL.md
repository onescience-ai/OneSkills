---
name: bio-biology-datapipes-adapters
description: OneScience 生信 datapipe 和 adapter skill。用于 biology/protenix/simplefold/openfold/evo2 数据读取、FASTA/MSA/PDB/mmCIF/JSON/SMILES 到模型 batch 的桥接、adapter registry、ProtenixInferAdapter、GenomeDataset 和输入协议兼容性判断。
---

# OneScience 生信 Datapipe 与 Adapter

## 使用边界

用于数据协议和模型输入桥接。若用户只是做传统生信文件处理，进入 `data-foundation`；若已经明确模型族，也同时读取对应模型 skill。

## 主要锚点

- 通用 biology：`src/onescience/datapipes/biology`
- Protenix：`src/onescience/datapipes/protenix`、`src/onescience/datapipes/biology/adapters/protenix_infer_adapter.py`
- SimpleFold：`src/onescience/datapipes/simplefold`
- OpenFold：`src/onescience/datapipes/openfold`
- Evo2：`src/onescience/models/evo2/data`、`src/onescience/datapipes/biology/datasets/genome_dataset.py`

## 兼容性检查

1. 样本返回格式是否匹配模型 forward 或训练脚本。
2. DataLoader batch 结构是否与训练脚本解包方式一致。
3. 输入文件是否已包含 MSA、template、ligand、CCD、tokenized structure 或 labels。
4. adapter 是否已有注册；没有注册时，不假装可直接运行。
5. 是否应在 datapipe、adapter、配置层还是调用层做最小桥接。

## 交接物

```yaml
bio_task_family: onescience-bio-datapipe
target_model_family:
input_files:
current_sample_schema:
expected_model_protocol:
adapter_or_datapipe:
compatibility_gaps:
bridge_plan:
source_anchors:
coder_assets_to_read:
execution_entry: onescience-skill -> onescience-coder
```

## 禁止事项

- 不要把所有生信模型都接到同一个 feature dict。
- 不要把 `GenomeDataset` 的普通序列输出直接当 Evo2 batch。
- 不要把 Protenix/AF3 JSON、OpenFold batch、SimpleFold feats 混用。
