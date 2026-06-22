# OneScience 生信模型推理矩阵

| 模型 | 用途 | 推荐入口 | 输入协议 | checkpoint / 权重 | 核心输出 | 高危混淆点 |
| --- | --- | --- | --- | --- | --- | --- |
| AlphaFold | AF2/Multimer JAX 结构预测 | `examples/biosciences/alphafold/run_alphafold.py` | FASTA + MSA/template pipeline | AF2 params | ranked/unrelaxed/relaxed PDB、pLDDT、PAE | 不等于 OpenFold batch，也不等于 AF3 JSON |
| OpenFold | AF2-style PyTorch 结构预测 | `examples/biosciences/openfold/run_pretrained_openfold.py` | OpenFold feature pipeline / FASTA + alignments | OpenFold params | PDB、feature/output pickle | recycling 维在 batch 最后一维，不能只喂 aatype |
| AlphaFold3 | AF3 JAX 复合物结构预测 | `examples/biosciences/alphafold3/run_alphafold.py` | AF3 JSON / data pipeline | AF3 model_dir | structure、ranking、PAE/PDE/confidence | JAX 编译、flash attention、CCD/配体资源敏感 |
| Protenix | AF3-style PyTorch 复合物结构预测 | `examples/biosciences/protenix/runner/inference_unified.py` | Protenix JSON + feature dict | `model_v0.5.0.pt` 等 | CIF/PDB、confidence、contact | 与 AlphaFold3 JSON 概念相近但 adapter 不兼容 |
| SimpleFold | flow-matching 蛋白折叠 | `examples/biosciences/simplefold/inference.py` | FASTA CLI / atom-token feats + ESM | SimpleFold scale ckpt | predicted structure、pLDDT | 需要 ESM/atom_to_token 特征，不是 OpenFold batch |
| RFdiffusion | 蛋白骨架生成 | `examples/biosciences/RFdiffusion/scripts/run_inference.py` | Hydra contig + optional PDB | RFdiffusion models | backbone PDB、TRB、trajectory | 输出多为骨架，通常还需 ProteinMPNN |
| ProteinMPNN | backbone-to-sequence | `examples/biosciences/ProteinMPNN/protein_mpnn_run.py` | PDB / parsed JSONL + chain/fixed/tied constraints | `vanilla_model_weights` / CA-only | FASTA、score、probability | `chain_M` 控设计位置，不能和 padding mask 混用 |
| PT-DiT | ProToken latent protein co-design | `examples/biosciences/pt_dit/example_scripts/de_novo_design.py` | ProToken emb + AA emb + diffusion config | PT-DiT + ProToken ckpt | token indexes、embedding、optional PDB | batch 需能按设备数整除，NRES 注意 128 倍数 |
| ProToken | structure tokenizer / decode | `src/onescience/flax_models/protoken/scripts/infer.py` / `decode_structure.py` | PDB or ProToken indexes | ProToken ckpt | VQ code、reconstructed PDB | 重建不是 AF2/AF3 预测；fake aatype 不等于真实设计序列 |
| Evo2 | genome LM 推理 | `examples/biosciences/evo2/infer.py` / `predict.py` | DNA prompt / FASTA tokens | `evo2_nemo_*` | logits、generated/scored sequence | NeMo/Megatron 依赖，不使用 protein feature dict |
| MolSculptor | 小分子生成优化 | `src/onescience/flax_models/MolSculptor/train/inference.py` / case scripts | SMILES / molecule graph / latent | AE/DiT ckpt | SMILES、reward、candidate table | RDKit sanitize、padding、vocab、docking 外部依赖 |
