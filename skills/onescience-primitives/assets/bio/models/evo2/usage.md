# launch

Evo2 是基因组语言模型原语，用于 DNA/genome token 的 prompt 生成、FASTA logits、序列似然打分、变异上下文评分，以及 Evo2 训练或微调。用户明确说“用 Evo2”“genome LM”“DNA token model”“基因组语言模型”“Evo2 predict/logits/score/generate/训练/微调”时召回。

DNA prompt 生成示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/evo2/infer.py --ckpt-dir "$ONESCIENCE_MODELS_DIR/evo2_nemo_7b" --prompt "ATGCGT" --temperature 1.0 --top-k 0 --top-p 0.0 --max-new-tokens 1024 --seed 0 --tensor-parallel-size 1 --pipeline-model-parallel-size 1 --context-parallel-size 1 --ckpt-format torch_dist --output-file "$RUN_DIR/evo2_generated.txt"
```

FASTA logits / 序列打分示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/evo2/predict.py --fasta "$RUN_DIR/evo2_inputs/example.fasta" --ckpt-dir "$ONESCIENCE_MODELS_DIR/evo2_nemo_7b" --output-dir "$RUN_DIR/evo2_predict" --batch-size 1 --model-size 7b --tensor-parallel-size 1 --pipeline-model-parallel-size 1 --context-parallel-size 1 --ckpt-format torch_dist --output-log-prob-seqs --log-prob-collapse-option mean
```

训练或微调示例：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/evo2/train_one_node.py -d "$ONESCIENCE_DIR/examples/biosciences/evo2/config/genome_data_config.yaml" --dataset-dir "$RUN_DIR/genome_mmap" --model-size 7b --devices 1 --num-nodes 1 --seq-length 8192 --tensor-parallel-size 1 --pipeline-model-parallel-size 1 --context-parallel-size 1 --micro-batch-size 1 --global-batch-size 1 --max-steps 1000 --lr 0.0003 --wd 0.01 --ckpt-format torch_dist --seed 1234 --result-dir "$RUN_DIR/evo2_train_results"
```

# input_schema

- 输入对象：DNA prompt、DNA FASTA、候选序列 FASTA、变异上下文序列，或用于训练/微调的 JSON/mmap/tokenized genome dataset。
- 推理输入：`infer.py` 需要 `--prompt`、`--ckpt-dir`、生成参数和并行参数；`predict.py` 需要 `--fasta`、`--ckpt-dir`、输出目录、batch size、模型规模和输出 log probability 选项。
- 训练/微调输入：需要 dataset config 或预处理后的 dataset dir、checkpoint 或模型规模、`seq_length`、batch、并行策略、学习率、训练步数和结果目录。
- 常用默认/显式参数：`seq_length=8192`，`model_size=7b`，`ckpt_format=torch_dist`，`tensor/pipeline/context_parallel_size=1`，`batch_size=1`，`temperature=1.0`，`top_k=0`，`top_p=0.0`。
- 数据检查：输入必须是 DNA/genome 序列或 Evo2 token batch；进入模型前确认非 DNA 字符、大小写策略、BOS/EOD、序列长度、序列 ID、参考版本和坐标语义。
- 训练/微调 batch 必须能提供 `tokens`、`position_ids`、`labels`、`loss_mask`；普通 FASTA prediction 输入不能直接当作训练数据。
- 智能体召回时建议记录：`usage_mode=inference | training | finetuning | scoring_node`，`entrypoint=infer.py | predict.py | train_one_node.py`，`input_artifacts=prompt | fasta | dataset_config | mmap_dir`，`output_artifacts=generated_sequence | logits | score_table | checkpoint | logs`，`preflight_checks=checkpoint | tokenizer | seq_length | DNA_chars | parallel_config`。

# runtime_interfaces

- `infer.py`：已有 checkpoint 的 DNA prompt generation 入口。
- `predict.py`：FASTA prediction、logits、sequence log probability、variant scoring 和候选序列排序入口。
- `train_one_node.py`：单节点训练或微调入口。
- `train_slurm.py`、`train_multi_node_slurm_evo2.sh`、`train_evo2.sh`：多节点或集群训练入口。
- `SimpleFastaDataset`：把 FASTA 转为 Evo2 prediction 样本并写出 `seq_idx_map.json`。
- `Evo2Tokenizer`：DNA 文本到 Evo2 token ids 的桥接。
- `MambaModel.forward`：执行推理 logits 或带 `labels/loss_mask` 的训练 loss。

# main_functions

- `infer`
- `predict`
- `train`
- `forward`
- `mamba_forward_step`
- `write_idx_map`

# execution_resources

- 需要 Evo2 checkpoint、NeMo/Megatron/BioNeMo、PyTorch 分布式环境、tokenizer、输入文件和可写输出目录。
- prompt 推理和 FASTA prediction 需要 checkpoint 格式、模型规模和并行参数与脚本匹配；常见格式为 `torch_dist`。
- 训练、微调、长上下文和大批量候选打分通常需要 GPU/DCU、SLURM 或远端运行环境。
- 输出观察项包括：生成序列、logits、sequence log probability、variant score、`seq_idx_map.json`、checkpoint、训练日志、失败序列 ID 和输出校验结果。

# operation_limits

- Evo2 只处理 DNA/genome token 建模；不是 variant caller、assembler、系统发育工具、蛋白结构预测器、蛋白设计器或小分子模型。
- 不把蛋白 FASTA、PDB、MSA、AF2/AF3/OpenFold/Protenix/SimpleFold/RFdiffusion/ProteinMPNN batch、SMILES 或分子图送入 Evo2。
- 普通基因组分析、变异检测、组装注释、RNA-seq、单细胞或临床解读不默认召回 Evo2；只有用户要求 Evo2/genome LM/生成/打分/训练/微调时才使用。
- Evo2 分数和生成结果只能作为研究型模型证据或候选排序特征，不能替代数据库注释、统计检验、公共卫生判断、临床复核或湿实验验证。
