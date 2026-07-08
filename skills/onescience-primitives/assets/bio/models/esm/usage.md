# launch

ESM 是蛋白语言模型原语集合，用于蛋白序列表征提取、接触/概率输出、ESMFold 单序列结构预测、突变效应零样本打分和 GVP inverse folding。用户说“提取蛋白 embedding”“用 ESMFold 快速折叠”“用 ESM 给突变打分”“基于结构做 inverse folding”时召回。

表征提取示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/esm/scripts/extract.py "$ONESCIENCE_MODELS_DIR/esm_models/esm2_t6_8M_UR50D.pt" examples/biosciences/esm/data/few_proteins.fasta "$RUN_DIR/esm_extract_out" --include mean per_tok contacts --repr_layers 6 --toks_per_batch 4096 --truncation_seq_length 1022
```

ESMFold 结构预测示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/esm/scripts/fold.py -i examples/biosciences/esm/data/few_proteins.fasta -o "$RUN_DIR/esmfold_pdb_out" --model-dir "$ONESCIENCE_MODELS_DIR/esm_models" --num-recycles 4 --max-tokens-per-batch 1024 --chunk-size 128
```

突变效应打分示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/esm/variant-prediction/predict.py --model-location esm1v_t33_650M_UR90S_1 --sequence WTSEQUENCE_HERE --dms-input examples/biosciences/esm/variant-prediction/data/BLAT_ECOLX_Ranganathan2015.csv --mutation-col mutant --dms-output "$RUN_DIR/esm_variant_prediction.csv" --offset-idx 24 --scoring-strategy wt-marginals
```

# input_schema

- 表征提取输入：蛋白 FASTA、ESM checkpoint 或模型名、输出目录、`repr_layers`、`include` 项和 token batch 大小。
- ESMFold 输入：蛋白 FASTA、模型目录、输出 PDB 目录、recycle 数、token batch、chunk size、CPU/GPU/offload 设置。
- Variant scoring 输入：野生型序列、突变 CSV、突变列名、offset、模型位置、scoring strategy。
- Inverse folding 输入：蛋白 backbone PDB/CIF、链 ID、采样温度和输出 FASTA；只在用户明确要求 ESM/GVP inverse folding 或需要 ESM 对照时作为结构到序列的辅助设计，普通 backbone-to-sequence 默认召回 ProteinMPNN。
- 常用默认/显式参数：extract `toks_per_batch=4096`，`repr_layers=-1`，`truncation_seq_length=1022`；ESMFold `max_tokens_per_batch=1024`，`num_recycles` 可显式设置，`chunk_size` 用于降显存。
- ESM 只处理蛋白氨基酸序列或蛋白结构；DNA/RNA 序列生成和变异效应优先 Evo2，复合物结构优先 Protenix/AlphaFold3，普通骨架到序列设计优先 ProteinMPNN。
- 智能体召回时建议记录：`usage_mode=representation | esmfold_structure | variant_scoring | inverse_folding | simplefold_feature_support`，`entrypoint=extract.py | fold.py | predict.py | inverse_folding scripts`，`input_artifacts=fasta | mutation_csv | pdb`，`output_artifacts=pt_embeddings | pdb | scored_csv | fasta`，`preflight_checks=protein_alphabet | model_path | repr_layers | token_limit | chain_id`。

# runtime_interfaces

- `extract.py`：批量提取 per-token、mean、BOS 和 contacts 表征。
- `fold.py`：ESMFold 单序列结构预测入口，输出 PDB。
- `predict.py`：突变效应零样本打分入口。
- `inverse_folding` scripts：基于 backbone 采样或打分序列。
- `Alphabet`/batch converter：把蛋白序列转换为 ESM token。

# main_functions

- `forward`
- `predict_contacts`
- `infer_pdb`
- `score_sequence`
- `sample_sequence`

# execution_resources

- 表征提取和 ESMFold 推荐 GPU；长序列可降低 `max-tokens-per-batch`、启用 `chunk-size` 或 CPU offload。
- 需要 ESM 模型权重、FASTA/突变表/PDB 输入和可写输出目录。
- 输出包括 `.pt` embedding、contacts、PDB、突变分数 CSV 或 inverse folding FASTA。
- 观察项应包含：输出文件数量、embedding 层是否正确、PDB 是否生成、突变分数列是否写出、失败是否来自非法氨基酸、token 长度、模型路径或显存。

# operation_limits

- ESM 不是 DNA/RNA 长序列基因组模型；核酸序列推理和变异优先 Evo2。
- ESMFold 是快速单序列结构预测，不替代 OpenFold 的完整 MSA/template 结构协议。
- ESM 不生成 RFdiffusion 风格新 backbone；骨架生成用 RFdiffusion。
- ESM inverse folding 只在用户显式要求 ESM/GVP inverse folding 或需要对照时使用；普通结构到序列设计和复杂约束设计通常优先 ProteinMPNN。
